from pathlib import Path

import numpy as np
import uproot


# Define sampling fraction constant
sfc = 0.11
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "exercise03"


def _resolve_path(fname: str) -> str:
    """Return an absolute path for the requested ROOT file."""
    file_path = Path(fname)
    if not file_path.is_absolute():
        file_path = DATA_DIR / fname
    return str(file_path)


def getData(fname: str = "", procName: str = "Events"):
    """Load data from a ROOT file, resolving it from the data directory by default."""
    input_file = uproot.open(_resolve_path(fname))
    dq_dict = input_file[procName].arrays(library="np")
    dq_events = {
        "Hits": {
            "edep": dq_dict["hit_edep"],
            "elmID": dq_dict["hit_elmID"],
        }
    }
    return dq_events


def process_event(sample_type: str = "electron", event_number: int = 0):
    """Hits of one event: dict with 'elmID' and raw 'edep' (divide by sfc for GeV).

    sample_type: "electron" or "dielectron"; event_number: 0-9.
    """
    if sample_type not in ("electron", "dielectron"):
        raise ValueError('sample_type must be "electron" or "dielectron"')
    if not 0 <= int(event_number) <= 9:
        raise ValueError("Event number must be between 0 and 9")

    file_name = f"{sample_type}.root"
    proc_name = f"Events{event_number}"

    dq_events = getData(file_name, proc_name)
    dq_hits = dq_events["Hits"]

    raw_elmID = dq_hits["elmID"]
    raw_edep = dq_hits["edep"]

    # Apply energy threshold mask
    emin = 0.005
    eng_mask = raw_edep >= emin
    elmID = raw_elmID[eng_mask]
    edep = raw_edep[eng_mask]

    return {
        "elmID": elmID,
        "edep": edep
    }


def get_hit_data(sample_type=None, event_number=None):
    """Return (elmID, raw edep) of one event.

    get_hit_data("electron", 5) reads event 5 of the electron sample. Arguments that
    are not given are asked for interactively.
    """
    if sample_type is None:
        sample_type = input("Enter sample type (electron or dielectron): ").strip()
    if event_number is None:
        event_number = int(input("Enter event number (0-9): ").strip())

    event_data = process_event(sample_type, event_number)
    elmID = event_data["elmID"]
    edep = event_data["edep"]

    return elmID, edep


def generate_2d_points(num_clusters=3, points_per_cluster=20, spread=4.0, random_seed=42):
    """Synthetic clusters for testing: centres uniform over the EMCal face (x in +-120 cm,
    y in +-60 cm), Gaussian points with standard deviation `spread` (cm) around them.
    Returns an (num_clusters * points_per_cluster, 2) array."""
    rng = np.random.default_rng(random_seed)
    centres = rng.uniform([-120, -60], [120, 60], size=(num_clusters, 2))
    data = [c + rng.normal(0.0, spread, size=(points_per_cluster, 2)) for c in centres]
    return np.vstack(data)


ECAL_DETID = 100  # detector ID of the EMCal in the A' (full-detector) sample


def get_testing_clustering(ecal_only=True):
    """Return per-event (elmID, edep) arrays from the A' -> e+e- sample.

    The A' file contains hits from the *whole* spectrometer (drift chambers,
    hodoscopes, ...). Only hits with ``hit_detID == 100`` are EMCal towers.
    The other detectors store a placeholder edep (3.4e38), so the ``emax`` cut
    already removes them; ``ecal_only`` makes this selection explicit.
    """
    input_file = uproot.open(_resolve_path("Aprime_dielectron.root"))
    arrays = input_file["Events"].arrays(["hit_detID", "hit_elmID", "hit_edep"], library="np")
    emax = 10000
    elmID, edep = [], []
    for det, elm, e in zip(arrays["hit_detID"], arrays["hit_elmID"], arrays["hit_edep"]):
        mask = e <= emax
        if ecal_only:
            mask &= det == ECAL_DETID
        elmID.append(elm[mask])
        edep.append(e[mask])
    return np.array(elmID, dtype=object), np.array(edep, dtype=object)


# ---------------------------------------------------------------------------
# Section 4 helpers: A' events with truth, and a toy EM-shower generator
# ---------------------------------------------------------------------------

N_ROWS, N_COLUMNS, CELL_SIZE = 72, 36, 5.535  # PHENIX EMCal geometry (cm)
_SENTINEL = 1e6  # truth branches are padded with 2^31-1


def get_aprime_event(event_number=0, emin=0.005):
    """One EMCal event of the A' -> e+e- sample, together with the MC truth.

    Returns a dict with
      - ``elmID``, ``edep``: EMCal hits (raw edep, divide by ``sfc`` for GeV)
      - ``true_E``: generated energies of the two leptons (GeV)
      - ``true_xy``: (2, 2) impact point on the EMCal face in the notebook
        convention (cm); rows are NaN if the lepton never reached the EMCal.

    Note: the truth branches use the opposite sign convention for y than
    ``channel_to_spatial_coordinates`` in the notebook, so y is flipped here.
    """
    input_file = uproot.open(_resolve_path("Aprime_dielectron.root"))
    a = input_file["Events"].arrays(
        ["hit_detID", "hit_elmID", "hit_edep", "ge", "gx_ecal", "gy_ecal"],
        entry_start=event_number, entry_stop=event_number + 1, library="np")
    det, elm, e = a["hit_detID"][0], a["hit_elmID"][0], a["hit_edep"][0]
    mask = (det == ECAL_DETID) & (e >= emin)

    true_xy = np.full((len(a["ge"][0]), 2), np.nan)
    for p in range(len(a["ge"][0])):
        gx, gy = a["gx_ecal"][0][p], a["gy_ecal"][0][p]
        valid = np.abs(gx) < _SENTINEL
        if valid.any():
            true_xy[p] = gx[valid][0], -gy[valid][0]
    return {"elmID": elm[mask], "edep": e[mask],
            "true_E": np.asarray(a["ge"][0], dtype=float), "true_xy": true_xy}


def _xy_to_channel(x, y):
    """Inverse of the notebook's channel -> (x, y) map (cell centres)."""
    r = np.floor(x / CELL_SIZE + N_ROWS / 2 + 0.5).astype(int)
    c = np.floor(N_COLUMNS / 2 - y / CELL_SIZE + 0.5).astype(int)
    inside = (r >= 0) & (r < N_ROWS) & (c >= 0) & (c < N_COLUMNS)
    return np.where(inside, r * N_COLUMNS + c, -1)


def _sample_lateral_profile(n, rng, r_core=1.0, r_tail=5.0, p_core=0.86):
    """Sample n radial distances (cm) from a two-component lateral profile.

    Each component is f(r) = 2 r R^2 / (r^2 + R^2)^2 (Grindhammer-type),
    whose CDF r^2/(r^2+R^2) can be inverted analytically.
    """
    R = np.where(rng.random(n) < p_core, r_core, r_tail)
    u = rng.random(n)
    r = R * np.sqrt(u / (1.0 - u))
    phi = rng.uniform(0, 2 * np.pi, n)
    return r * np.cos(phi), r * np.sin(phi)


def _deposit(E, x0, y0, rng, spots_per_gev=40):
    """Energy deposits (x, y, e) of one EM shower of energy E (GeV) at (x0, y0)."""
    n = int(max(100, spots_per_gev * E))
    dx, dy = _sample_lateral_profile(n, rng)
    return x0 + dx, y0 + dy, np.full(n, E / n)


def generate_shower_event(n_showers=2, energies=None, positions=None,
                          min_separation=6.0, max_separation=30.0,
                          energy_range=(5.0, 80.0), noise=0.01, emin=0.005,
                          random_seed=None):
    """Toy PHENIX-like EMCal event with ``n_showers`` electromagnetic showers.

    The output mimics ``process_event``: ``elmID`` and *raw* ``edep``
    (divide by ``sfc`` to get GeV), so the same notebook code works on both.
    In addition the full MC truth is returned:
      - ``true_E`` (K,), ``true_xy`` (K, 2): energies and impact points
      - ``true_fraction`` (n_hits, K): fraction of each hit's energy that
        belongs to each shower (rows sum to 1) -> "truth energy sharing"
    Showers are placed near the detector centre, separated by
    ``min_separation``..``max_separation`` cm from the first one.
    """
    rng = np.random.default_rng(random_seed)
    if energies is None:
        energies = rng.uniform(*energy_range, size=n_showers)
    energies = np.asarray(energies, dtype=float)
    K = len(energies)
    if positions is None:
        first = rng.uniform([-60, -30], [60, 30])
        positions = [first]
        while len(positions) < K:
            d = rng.uniform(min_separation, max_separation)
            phi = rng.uniform(0, 2 * np.pi)
            cand = first + d * np.array([np.cos(phi), np.sin(phi)])
            if all(np.linalg.norm(cand - p) >= min_separation for p in positions):
                positions.append(cand)
    positions = np.asarray(positions, dtype=float)

    n_cells = N_ROWS * N_COLUMNS
    per_shower = np.zeros((K, n_cells))
    for k, (E, (x0, y0)) in enumerate(zip(energies, positions)):
        x, y, e = _deposit(E, x0, y0, rng)
        ch = _xy_to_channel(x, y)
        ok = ch >= 0
        np.add.at(per_shower[k], ch[ok], e[ok])

    total = per_shower.sum(axis=0) + rng.normal(0.0, noise, n_cells)
    raw = total * sfc
    hit = raw >= emin
    elmID = np.flatnonzero(hit)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = per_shower[:, hit].T / per_shower[:, hit].sum(axis=0)[:, None]
    frac = np.nan_to_num(frac, nan=1.0 / K)
    return {"elmID": elmID.astype(np.int32), "edep": raw[hit].astype(np.float32),
            "true_E": energies, "true_xy": positions, "true_fraction": frac}


def make_shower_images(n_images, size=7, kind="single", energy_range=(5.0, 80.0),
                       separation_range=(4.0, 9.0), noise=0.01, emin=0.005,
                       normalize=True, random_seed=None):
    """A dataset of ``size x size`` tower windows centred on the seed tower.

    kind:
      - "single": one EM shower hitting a random point of the central tower
      - "merged": two EM showers closer than ~2 towers (look like one cluster)
      - "mip":    a minimum-ionising particle (muon) -> ~0.3 GeV in one tower
    Images are indexed ``img[iy, ix]`` (plot with ``origin="lower"``) and, if
    ``normalize``, divided by their sum (energy fractions, sum = 1).
    Returns ``images`` (n, size, size) and a dict of truth arrays:
    ``dx``, ``dy`` (impact point w.r.t. the seed-tower centre, cm) and ``E``.
    """
    rng = np.random.default_rng(random_seed)
    half = size // 2
    pad = 2  # simulate on a larger window, then crop around the seed
    big = size + 2 * pad
    edges = (np.arange(big + 1) - big // 2 - 0.5) * CELL_SIZE
    images = np.zeros((n_images, size, size))
    truth = {"dx": np.zeros(n_images), "dy": np.zeros(n_images), "E": np.zeros(n_images)}
    for i in range(n_images):
        x0, y0 = rng.uniform(-CELL_SIZE / 2, CELL_SIZE / 2, size=2)
        E = rng.uniform(*energy_range)
        if kind == "single":
            x, y, e = _deposit(E, x0, y0, rng)
        elif kind == "merged":
            f = rng.uniform(0.3, 0.7)
            d = rng.uniform(*separation_range)
            phi = rng.uniform(0, 2 * np.pi)
            x1, y1, e1 = _deposit(f * E, x0, y0, rng)
            x2, y2, e2 = _deposit((1 - f) * E, x0 + d * np.cos(phi), y0 + d * np.sin(phi), rng)
            x, y, e = np.r_[x1, x2], np.r_[y1, y2], np.r_[e1, e2]
        elif kind == "mip":
            E = rng.normal(0.3, 0.05)
            x = x0 + rng.normal(0, 0.3, 200)
            y = y0 + rng.normal(0, 0.3, 200)
            e = np.full(200, E / 200)
        else:
            raise ValueError("kind must be 'single', 'merged' or 'mip'")
        img, _, _ = np.histogram2d(y, x, bins=[edges, edges], weights=e)
        img += rng.normal(0.0, noise, img.shape)
        img[img * sfc < emin] = 0.0
        # re-centre on the most energetic tower (what a seed finder would do)
        c = big // 2
        core = img[c - 1:c + 2, c - 1:c + 2]
        iy, ix = np.unravel_index(np.argmax(core), core.shape)
        iy, ix = iy + c - 1, ix + c - 1
        img = img[iy - half:iy + half + 1, ix - half:ix + half + 1]
        x0 -= (ix - c) * CELL_SIZE
        y0 -= (iy - c) * CELL_SIZE
        if normalize:
            img = img / img.sum()
        images[i] = img
        truth["dx"][i], truth["dy"][i], truth["E"][i] = x0, y0, E
    return images, truth

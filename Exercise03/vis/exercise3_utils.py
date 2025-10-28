import numpy as np
import uproot


# Define sampling fraction constant
sfc = 0.11


def getData(fname="", procName="Events"):
    """Load data from a ROOT file."""
    input_file = uproot.open(fname)
    dq_dict = input_file[procName].arrays(library="np")
    dq_events = {
        "Hits": {
            "edep": dq_dict["hit_edep"],
            "elmID": dq_dict["hit_elmID"],
        }
    }
    return dq_events


def process_event(sample_type="electron", event_number=0):
    if event_number < 0 or event_number > 10:
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


def get_hit_data():
    sample_type = input("Enter sample type (electron or dielectron): ").strip()
    event_number = int(input("Enter event number (0-9): ").strip())

    event_data = process_event(sample_type, event_number)
    elmID = event_data["elmID"]
    edep = event_data["edep"]

    return elmID, edep


def generate_2d_points(num_clusters=3, points_per_cluster=50, spread=1.0, random_seed=42):
    np.random.seed(random_seed)
    data = []

    for i in range(num_clusters):
        center = np.random.rand(2) * 10
        cluster_points = center + np.random.randn(points_per_cluster, 2) * spread
        data.append(cluster_points)

    data = np.vstack(data)
    return data


def get_testing_clustering():
    Aprime = "Aprime_dielectron.root"
    dq_events = getData(Aprime, "Events")
    dq_hits = dq_hits = dq_events["Hits"]
    raw_elmID = dq_hits["elmID"]
    raw_edep = dq_hits["edep"]
    emax = 10000
    elmID = []
    edep = []
    for elmID_subarray, edep_subarray in zip(raw_elmID, raw_edep):
        mask = [value <= emax for value in edep_subarray]
        elmID.append(np.array([e for e, m in zip(elmID_subarray, mask) if m]))
        edep.append(np.array([e for e, m in zip(edep_subarray, mask) if m]))
    return np.array(elmID, dtype=object), np.array(edep, dtype=object)

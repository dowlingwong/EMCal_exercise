# Exercise 03 (EMCal) — review, November 2026

Scope: `notebooks/exercise03/Exercise03.ipynb` (student), `Exercise03_Solutions.ipynb` (solution),
`src/exercise03/exercise3_utils.py`, `tests/exercise03/`, `docs/Exercise03.tex/.pdf`, and the repository layout.

> **Status (6 Nov 2026, later the same day):** the review items for Exercise 03 have been worked through except the `[TBD]` dates and the repository restructuring; see **§7 Revision log** at the end for what was fixed and what is still open.

**How this was checked**
- The full solution notebook was executed headless (nbclient), with `get_hit_data()` fed the events the text asks for.
- Student and solution notebooks were diffed cell by cell.
- All markdown and code was read for physics, logic and wording.
- Both sheets were rebuilt to update the dates.

**Cell references:** `S[i]` = student notebook, `O[j]` = solution notebook (0-based cell index as in nbformat / JupyterLab "cell number − 1").
**Severity:** **High** = wrong result, broken for students, or answer leak · **Med** = misleading or inconsistent · **Low** = cosmetic.

---

## 0. Done in this round

| what | where |
|---|---|
| Notebook headers → "D. Wong, November 2026" | `S[0]`, `O[0]` |
| Hand-in date → `[TBD] January 2027`; Q&A session → `November 2026 (date and time: [TBD])`; marked `% TODO(dates)` | `docs/Exercise03.tex` l. 13, 23–24 |
| Geant4 sheet date → January 21, 2027 | `docs/Geant4.tex` l. 8 |
| Both PDFs rebuilt (semester → *Winter Semester 2026/27*) | `docs/Exercise03.pdf`, `docs/Geant4.pdf` |
| Solution check: Section 4 is in both notebooks (66 cells); the solution has all outputs (17 figures, no errors); the student version contains no solution code (4 TODO cells, empty answer boxes); everything before Section 4 in the student notebook is unchanged | — |

> **Action needed — PDFs.** The semester, staff list and KIT logo come from `../common/style_exercise.sty`, which is **not in this repo**. The two PDFs were therefore built with a stand-in style that reproduces the WS 2025/26 header (layout within a few pt). Before release:
> 1. Update the semester and staff in the real `common/` and recompile both sheets.
> 2. Confirm the staff list. It was copied from the WS 2025/26 Exercise 03 sheet. The old `Geant4.pdf` was still the **WS 2024/25** version (German header, different staff), so its header has now changed.
> 3. Fill the three `[TBD]` placeholders (`grep -n "TODO(dates)" docs/*.tex`).

---

## 1. High-priority issues

**H1 — All local figures are missing, and `.gitignore` prevents adding them.**
- The notebooks show `figures/x0.png`, `e_eng_loss.png`, `mu_eng_loss.png`, `PHENIX_color_view.gif`, `emcal.png`, `emcal_1.png` and `padding.png` (`S[5,8,21,33,37,82]`, `O[5,8,21,33,84]`).
- None of these files exist anywhere in the repo, and `.gitignore` contains `figures/`, so they cannot be committed. Students currently see broken images, including the seed-search illustration they need for Problem 3.2.
- The README points to `assets/figures/exercise03/`, which does not exist either.
- *Fix:* add the images under e.g. `notebooks/exercise03/figures/` and remove `figures/` from `.gitignore` (ignore only generated output dirs).

**H2 — The solution notebook does not run top to bottom.** Headless run results:
- `O[12]`: `TypeError: critical_energy() takes from 1 to 2 positional arguments but 3 were given` (`critical_energy(Z_PbWO4, 800, 1.2)`).
- `O[42]`: `import exercise3_utils as ex3` → `ModuleNotFoundError`. Only `src/` is on `sys.path`, and the setup cell already did `from exercise03 import exercise3_utils as ex3`. Delete the line. This error cascades into `O[44]`, `O[53]` and `O[56]` (`NameError`).
- `O[73]` / `S[70]`: `%run -i unit_test.py` → file not found. The test lives in `tests/exercise03/`, so use `%run -i ../../tests/exercise03/unit_test.py`, as Section 4 does for `gmm_test.py`.
- After patching these three, every other cell runs.

**H3 — An answer is leaked in the student notebook.**
- `S[79]` asks *"Compare computational complexity for elbow and silhouette"* and `S[80]` is the empty answer box.
- `S[81]` then contains the complete derivation, with boxed $\mathcal{O}(\cdot)$ results.
- *Fix:* remove `S[81]` from the student version (it belongs in the solution only). The solution notebook has the derivation (`O[83]`) but not the exercise prompt, so add the prompt to the solution as well.

**H4 — Problem 2.2: cluster moments are computed without energy weights, and the provided answers interpret pure geometry.**
- `f_mean`, `f_width`, `f_skewness` and `f_kurtosis` take only hit coordinates. Every tower counts the same, whether it holds 20 GeV or 50 MeV.
- For electron event 5 (a 3×3 block of hits, `O[53]`) the result is skewness 0 and kurtosis 1.5 in both x and y: the moments of a 3×3 grid of points, not of the shower.
- The solution answer `O[54]` nevertheless explains skewness and kurtosis physically (magnetic field, hadronic tails).
- *Fix:* use energy-weighted moments, $\mu = \sum_i E_i x_i / \sum_i E_i$ and likewise for higher moments (pass `weights=edep`), and rewrite the answer. Section 4.1 now makes exactly this point, so 2.2 and 4.1 would then agree.

**H5 — Section 1 formulas and solution code disagree.**
- $E_c$: the text gives $800\,\text{MeV}/Z$ (`S/O[7]`), the solution uses $610/Z$ (`O[12]`). Neither cites PDG's $610/(Z+1.24)$ (solids).
- $x_\text{max}$: the text gives $\ln(E/E_c)/\ln 2 \cdot X_0$, the solution computes $\ln(E/E_c)\cdot X_0$ (`O[16]`). The printed answer (9.2 $X_0$) therefore does not follow from the formula students are given (13.3 $X_0$).
- `O[12]` silently redefines `Z_PbWO4 = 68.35` after using 31.3, with no explanation.
- `O[16]` uses $X_0 = 0.92$ cm for PbWO$_4$; please check against the PDG page linked in the exercise (≈0.89 cm). The comment says `# Photon energy` for a 100 GeV *electron*.

**H6 — Several student template cells are Python syntax errors as distributed.**
- `S[12]` has `def critical_energy(..., ..., ...):` (`...` is not a valid parameter name).
- `S[39]` and `S[41]` contain functions with a docstring or nothing at all as body.
- `S[41]` also contains the data-loading lines, so students cannot even load an event before writing both plotting functions.
- *Fix:* use valid stubs (`def f(Z, A):` + `raise NotImplementedError` or `return ...`) and move the loading code into its own cell.

**H7 — `seed_search` window bounds were swapped in the solution (fixed in this round).**
- The energy matrix is transposed, but the window used `n_rows` and `n_columns` the wrong way round. For towers with row index ≥ 37 the neighbourhood came out empty, so every tower above threshold became a "seed".
- The student description (`S[82]`) gives no hint about the transpose, so expect the same bug in student code.
- Section 4 builds on the student's `seed_search`, so a buggy version gives wrong results there silently (see S4-2).

---

## 2. Correctness and logic (medium)

| id | location | issue | suggested fix |
|---|---|---|---|
| M1 | `O[25]` | Muon answer: "We expect a narrow EM shower" — a 50 GeV muon is a MIP and does **not** shower. The (m_e/m_μ)² factor concerns bremsstrahlung only. | Answer with ionisation: dE/dx ≈ 10 MeV/cm in PbWO₄ × 22 cm ≈ 0.2 GeV, deposited along a narrow track (one tower). |
| M2 | `O[27]` | Muon "critical energy" from pure (m_μ/m_e)² scaling ≈ 407 GeV is presented as the result. | Ask students to compare with the muon critical energy on the PDG page they already use (O(100 GeV)) and discuss why the naive scaling overestimates it. |
| M3 | `S[35]`, utils | `get_hit_data()` uses `input()`. The notebook cannot be executed non-interactively (nbconvert, CI, autograding), and every re-run asks again. | Default to `process_event(sample, n)` in the text; keep `get_hit_data` as an optional helper. |
| M4 | utils `process_event` | Guard is `event_number > 10` but the message says 0–9 → event 10 gives a `KeyError` deep in uproot. | `if not 0 <= event_number <= 9`. |
| M5 | `O[41]` `plot_spatial_energy_matrix` | Accepts `centroids` and `labels` but ignores both. All elbow/silhouette plots in 3.2 therefore show uncoloured points without centroids, although the titles say "Clusters: k". | Colour by `labels`, draw `centroids`. |
| M6 | `S[61]`/`S[63]`, `O[64]`/`O[66]` | Text says `import ex3; ex3.generate_2d_points()` "with default settings" — wrong import, and the notebook then redefines `generate_2d_points` **without defaults** and with a different box (±120×±60 cm vs utils `rand(2)*10`). Calling it "without arguments" raises `TypeError`. | Use one generator (the utils one, with defaults that match the detector), fix the import line. |
| M7 | `S[63]`/`O[66]` | One cell produces **27** figures of 10×10 in (3 × 3 × 3 loop) → notebook bloat and scrolling. | One figure with a 3×3 subplot grid, or fewer combinations. |
| M8 | `O[69]` KMeans | `init="k-means++"` is accepted but ignored (always random init); `_kmeanspp_init` is never called; mixes Python `random` and NumPy RNG. `S[64]` says "Forgy method" while the default is k-means++. | Honour `init`, use one RNG. |
| M9 | `S[68]`/`O[71]` | "Unit test 1" compares your KMeans (`random_state=34`) with sklearn (`random_state=42`) → not a like-for-like comparison. | Same seed, or average over seeds. |
| M10 | `S[53]`/`O[56]` (provided code) | `print(f'Raw skewness: {x_skewness},{y_skewness}')` prints the **standardised** value under the "raw" label; `x_skewness_raw` is computed but never printed. | Print `x_skewness_raw, y_skewness_raw`. |
| M11 | `O[51]` | `f_variance` calls `width(data)` (undefined) → `NameError` when used. | `f_width(data)**2`. |
| M12 | `S/O[42–46]` | "What is the distribution of all measured energies?" — the solution only prints a list of 10 numbers. | Histogram (and note that 10 events is very few). |
| M13 | `S[58]`/`O[61]` | Problem 3.1 ("homemade K-means") opens with an exercise on moments of multi-particle events. | Move to the end of 2.2 as a transition. |
| M14 | `S[75,77]`, `O[78,80]` | "Test it on a few events" — the code only runs on synthetic points; no EMCal event is clustered in 3.2. | Add one dielectron event, or reword. |
| M15 | `S[82]`/`O[84]` | Seed-search recipe talks about a "15×15 grid" and a "(15+1)×(15+1) array" (detector is 72×36); "sort ascending" is irrelevant for a local-maximum test; the default threshold of 5 GeV misses low-energy electrons (seed fraction 30–90 %). | Describe the real grid, drop the sort, and discuss threshold vs efficiency. |
| M16 | `O[88]` | Solution answer box for the seed search is **empty**; the asked question ("what parameters can you tune?") is unanswered. | Threshold, padding size, merging of adjacent seeds, minimum cluster energy. |
| M17 | `O[39]` | Coordinate convention `x = (r − 36)·s`, `y = (18 − c)·s` puts tower centres asymmetrically (x ∈ [−199, 193] cm) and flips y with respect to the MC-truth branches in the A′ file. Not wrong, but undocumented. | State the convention in 2.1. If you change it, change `exercise3_utils._xy_to_channel` too (Section 4 relies on it). |
| M18 | `S/O[32]` | "In this section, we will consider a real EMCal, used in the PHENIX experiment". The A′ file looks like it comes from the SpinQuest/DarkQuest simulation (branches `st1`/`st3`, `dimuon_*`, `fpga_trigger`), whose EMCal is built from former PHENIX modules. Also "a particle gun with a gaussian energy distribution, ranging from 5 to 80 GeV" is self-contradictory. | Check the origin and state it; specify the gun spectrum. |
| M19 | `S/O[64]` | The k-means primer (avian-flu epidemiology example, "Forgy method") appears to be adapted from Cornell CS 1110's k-means assignment (the archive even contains `cornell_kmean_test.py`). | Add a credit line or rewrite. |
| M20 | `S/O[10]` | Hot-linked ResearchGate image for the CMS ECAL — fragile and unlicensed. | Local figure with source. |
| M21 | student ↔ solution drift | The text differs between versions in places other than answers: `S[26]` vs `O[26]` (student has "(how is this transition energy called?)" and the typo "evenrgy"); `S[37]` vs `O[37]` (completely different paragraph, student version has the two missing EMCal figures); docstrings of `KMeans` and `evaluate_method` differ. | Generate the student notebook *from* the solution (e.g. `nbgrader` or a `### BEGIN SOLUTION` marker script) instead of maintaining two files by hand. |

---

## 3. Sloppiness (wording, typos, formatting)

**Typos** (student / solution cells):
- "nucles" → nucleus (`S/O[7]`); "weigth" → weight (`S/O[11]`); "evenrgy" (`S[26]`)
- "dieletron" ×2 and "digit `electron`" → "type" (`S/O[35]`); "conveinently" (`S[42]`, `O[43]`)
- "not ment" → meant (`S/O[39]`); "an hit" (`O[37]`)
- "Silouette" (`S[74]`, `O[77]`, also in the commented tex); "evalue" (`S[67]`, `O[70]`)
- "has passed all the test" (`S[69]`, `O[72]`); "on few events" (`S[77,83]`, `O[85]`)
- Solution answers: "momenta" → moments (`O[63]`), "logaritmically" (`O[18]`), "appratus" (`O[30]`), "The silhouette method if more refined" / "despite apparently simpler" (`O[82]`).

**Exercise sheet page 1:** "Each particle typically deposit" (l. 18), "the k-mean algorithm" (l. 20), "work though" → through (l. 30).

**Naming:** "Thomson's approximation" (`S/O[6,14]`) is not a standard name for these formulas (they are the usual Rossi/PDG approximations; the $X_0$ expression is a simplified Tsai formula). Use "approximate formulas (see PDG, Passage of particles through matter)".

**Markdown/HTML hygiene:**
- `( $\sim$ 10 )~MeV` renders a literal "~" (`S/O[6]`).
- 20 exercise boxes close a `</span>` that was never opened (`S[11,15,17,24,26,29,38,40,42,47,49,58,62,65,67,69,75,77,79,83]`).
- 12 answer boxes open `<div class="alert">` without closing it (`S[13,18,25,30,51,54,60,77,79,80,83,86]`).
- Headings mix Markdown and HTML (`## <h1 style=...>`), so the JupyterLab table of contents shows raw HTML.

**Style:**
- `S[37]` is a single 120-word sentence that also starts with a fragment ("As briefly mentioned in the previous section.").
- `S[0]` has trailing spaces.
- Large commented-out blocks: 214 of 392 lines of `Exercise03.tex` are commented-out theory duplicated in the notebook. Delete them or move them to a separate `theory.tex`.
- Sheet vs repo: the sheet tells students to open `Exercise03/Exercise03.ipynb`, but in this repo it is `notebooks/exercise03/Exercise03.ipynb`. Keep the instructions in sync with whatever layout is shipped to `tp1_forstudents`.

**Data format:** `electron.root`/`dielectron.root` store each event as its own tree (`Events0`…`Events9`), while `Aprime_dielectron.root` uses one tree `Events` with 100 entries. Two access paths for the same kind of data.

---

## 4. Section 4 (new) — self-review

| id | issue | suggestion |
|---|---|---|
| S4-1 | Section 4 uses the student's `channel_to_spatial_coordinates`. The toy simulation assumes exactly the solution's convention (M17). A student with a different but valid convention (half-cell offset, y not flipped) gets wrong truth comparisons without an error. | Add a check cell at the start of Section 4 that compares the student function with the convention used by `ex3` and stops with a clear message. |
| S4-2 | Same for `seed_search` (see H7): a student version with the bounds bug produces many fake seeds; 4.1/4.2 then look broken. | Either ship a reference `ex3.seed_search` or add a sanity check (two well-separated toy showers → exactly 2 seeds). |
| S4-3 | The toy simulation is 2D only (no longitudinal profile, no sampling-layer fluctuations, constant noise); its "tuning to PHENIX" rests on the 10 electron events. | Say so in the notebook (it does, briefly), or validate against a Geant4 sample from the Geant4 exercise. |
| S4-4 | Length: the notebook is now 153 cells; Section 4 alone takes about 3 min to run (VAE ≈ 1 min, energy-sharing scan and BIC scan ≈ 1 min). | Consider shipping Section 4 as `Exercise03b.ipynb` (optional/bonus), which also keeps Section 1–3 grading unchanged. |
| S4-5 | Rate-distortion scan in 4.3 fits the student's `KMeans` up to K = 128 on 20 000 × 49 points; a non-vectorised student implementation may take minutes. | Cap at K = 64 or subsample in the student version. |
| S4-6 | Only 4 TODO cells: the section is guided rather than open. That was deliberate (interpretation over coding), but grading should then weight the answer boxes. | Decide on points per answer box. |

---

## 5. Repository structure — proposal

**Current state:**
- Notebooks, data, utils, tests and sheets are split by *type* (`notebooks/`, `data/`, `src/`, `tests/`, `docs/`), so one exercise is spread over five folders.
- Solutions sit next to the student notebooks. The sheet says students pull `tp1_forstudents`; if that repo is fed from here, solutions must be filtered out.
- `archive/` is **48 MB** in the working tree (the whole git pack is 57 MB) and holds:
  - third-party PDFs (CERN-LHCC-96-41, conference talks)
  - a copy of `Geant4-models-master`
  - older notebooks, committed `__pycache__/*.pyc` and `.ipynb_checkpoints/`
- `src/geant4_simulation/libphyslist.so` is a compiled binary in git (it should be built in the Docker image from `physicsList/`).
- The LaTeX style (`common/`) that the sheets need is missing from the repo, so nobody can rebuild a sheet from a clean clone.
- No environment file: the `Dockerfile` only adds Geant4. Its `PYTHONPATH=/opt/geant4/...` and `G4*DATA=/data_share/...11.1.1` paths do not match `conda install geant4`, and DAWN is downloaded over plain http.
- `.gitignore` excludes every `figures/` directory (H1).

**Proposed layout** (by exercise, with a clear student/solution boundary):

```
EMCal_exercise/
├── README.md                      # what is where, how to run, how to release
├── environment.yml                # numpy, matplotlib, uproot, scikit-learn (+ geant4 for ex05)
├── docker/Dockerfile
├── common/                        # style_exercise.sty, definitions.tex, kit_logo.pdf  (sheets build from a clean clone)
├── exercises/
│   ├── ex03_emcal/
│   │   ├── Exercise03.ipynb       # student version (generated, outputs stripped)
│   │   ├── figures/               # x0.png, padding.png, ... (tracked)
│   │   ├── data/                  # electron.root, dielectron.root, Aprime_dielectron.root
│   │   ├── emcal_utils.py         # today: src/exercise03/exercise3_utils.py
│   │   ├── tests/                 # unit_test.py, gmm_test.py (paths relative to the notebook)
│   │   └── sheet/                 # Exercise03.tex/.pdf, img/
│   └── ex05_geant4/
│       ├── Geant4_Part1.ipynb, Geant4_Part2.ipynb
│       ├── geant4_simulation/     # package; libphyslist.so built, not committed
│       └── sheet/                 # Geant4.tex/.pdf
├── solutions/                     # source of truth: full notebooks with outputs (NOT synced to students)
│   ├── ex03_emcal/Exercise03_Solutions.ipynb
│   └── ex05_geant4/...
└── tools/
    ├── make_student.py            # strips solutions / answer text → exercises/*/ (or use nbgrader)
    ├── run_notebooks.py           # executes all solutions headless (CI smoke test)
    └── release.sh                 # copies exercises/ (not solutions/) into tp1_forstudents
```

**Migration steps** (in this order):
1. Move `archive/` to a separate branch or tag (`git switch -c archive`, then remove it on `main`). For the existing pack size, rewrite history with `git filter-repo` only if it matters.
2. Delete the committed `__pycache__/` and `.ipynb_checkpoints/` folders and `libphyslist.so`, and add them to `.gitignore`. Replace the `figures/` rule with specific output folders.
3. Add `common/` and `environment.yml`.
4. Move files with `git mv` (keeps history). Update `sys.path` in the setup cells (or `pip install -e .` a tiny package) and the `%run` test paths.
5. Add a CI job (GitHub Actions / GitLab CI) that runs `tools/run_notebooks.py` on the solutions and `pytest tests/`. H2 would have been caught automatically.
6. Generate the student notebooks from the solutions (M21) and strip outputs (`nbstripout`).

---

## 6. Suggested order of work

1. H1 (figures), H3 (answer leak), H2 (solution runs), H6 (valid templates). These directly affect students and take under an hour.
2. H4/H5 (physics consistency in Sections 1–2) and M1/M2 (muon answers).
3. Fill the `[TBD]` dates and recompile the sheets with the real `common/`.
4. Typos and HTML hygiene (section 3). Mostly search-and-replace.
5. Repository restructuring (section 5), ideally before the next release to `tp1_forstudents`.

---

## 7. Revision log (6 Nov 2026)

Cell numbers in §1–§4 refer to the notebooks *before* this revision.
The solution notebook is now the **single source**: cells that differ for students are tagged (`answer`, `solution` + `student_source`, `solution-only`), and `tools/make_student.py` generates `Exercise03.ipynb`.
The solution runs top to bottom headless with **0 errors** (no keyboard input, about 3 min).

| id | status | what was done |
|---|---|---|
| H1 | fixed | The 8 images (incl. the previously commented-out `shower.gif`) are in `notebooks/exercise03/figures/`, all paths resolve in both notebooks, captions describe each figure and credit PDG/PHENIX where known; `figures/` removed from `.gitignore`. **Open:** fill in the sources marked "to be documented" in `figures/README.md`. |
| H2 | fixed | Cell 12 rewritten, wrong `import` removed, test path `../../tests/exercise03/unit_test.py`; full headless run: 0 errors. |
| H3 | fixed | Complexity derivation is now the (tagged) answer to the complexity exercise; students get an empty box. |
| H4 | fixed | Moments take optional energy weights (`np.average`); text, formulas and answers rewritten; unweighted vs weighted comparison printed for three electron events. |
| H5 | fixed | PDG formulas in the text ($E_c = 610/(Z+1.24)$, practical $X_0$, $E_s = 21.2$ MeV, Heitler *and* PDG $x_\text{max}$); code computes exactly these; PDG values for PbWO₄ ($X_0$ = 0.8903 cm, $E_c$ = 9.64 MeV, verified on the PDG page); mass-fraction rule shown as a bonus (gives 7.36 vs PDG 7.39 g/cm²); `Z_PbWO4 = 68.35` removed. |
| H6 | fixed | All student code cells parse (checked with `ast`); loading code moved to its own cell. |
| H7 | fixed | Window bounds fixed in the solution; recipe now warns about the transposed matrix; Section 4 checks the student's `seed_search` before using it. |
| M1 | fixed | MIP answer: ≈ 10.2 MeV/cm × 22 cm ≈ 0.2 GeV, track-like, Landau "MIP peak". |
| M2 | fixed | Naive scaling (≈ 410 GeV) compared with the PDG muon critical energy (170 GeV for PbWO₄, 141 GeV for Pb) and explained. |
| M3, M4 | fixed | `get_hit_data(sample, event)` takes arguments (prompts only if omitted); `process_event` validates sample and 0–9 range. |
| M5 | fixed | `plot_spatial_energy_matrix` colours by `labels` and draws `centroids`; elbow/silhouette plots now show the clustering. |
| M6, M7 | fixed | One generator (`ex3.generate_2d_points`, detector-sized defaults); 27 figures → 3 grid figures. |
| M8, M9 | fixed | `init="k-means++"`/`"random"` honoured, single NumPy RNG; new k-means++ unit test; same seed as sklearn (identical inertia 78.8557). |
| M10, M11, M12 | fixed | Raw-moment print, `f_variance`, energy histogram of both samples. |
| M13, M14 | fixed | Multi-particle moments moved to the end of 2.2; elbow/silhouette also applied to dielectron event 6. |
| M15, M16 | fixed | Seed recipe describes the real 72×36 grid, no sort; default threshold 1 GeV; seeds plotted on events; solution answer written. |
| M17 | fixed | Convention stated in Problem 2.1 and checked by an assertion at the start of Section 4. |
| M18 | reworded | Neutral wording ("geometry of the PHENIX lead–scintillator EMCal", gun energies 5–80 GeV). **Open:** confirm the origin of the samples. |
| M19 | fixed | The avian-flu example was replaced by a calorimeter example (no attribution needed any more). |
| M20 | fixed | Hot-linked image removed; CMS ECAL cited (JINST 3 (2008) S08004). |
| M21 | fixed | Student notebook generated from the solution (`tools/make_student.py`); text drift removed. |
| §3 sloppiness | fixed | All listed typos; "Thomson's approximation" removed; `~MeV`; 0 stray `</span>`, all alert `<div>`s closed; headings are plain HTML (clean table of contents); run-on paragraph in 2.1 rewritten; sheet typos fixed and 205 lines of commented-out theory deleted from `Exercise03.tex`; page 1 now mentions Section 4. **Not changed:** the per-event tree layout of the ROOT files; the "subfolder `Exercise03`" instruction (depends on how `tp1_forstudents` is laid out). |
| S4-1, S4-2 | fixed | Assertion cell checks the coordinate convention and that `seed_search` finds exactly 2 seeds for two separated showers. |
| S4-3 | fixed | Toy-model limitations stated in the notebook. |
| S4-4 | open | Section 4 is still part of the main notebook (splitting into `Exercise03b.ipynb` is a course decision). |
| S4-5 | fixed | Rate-distortion scan capped at K = 64. |
| S4-6 | open | Points per answer box (grading decision). |
| new | fixed | Found during the revision: the elbow scan started at K = 2, so an elbow at the true K = 2 was invisible; it now starts at K = 1 (integer x-ticks), and the answer discusses the ambiguous 6-cluster case (local minima of a single k-means++ start). |
| §5 restructuring | not done | Content-only revision, as agreed; no files were moved or deleted. |
| dates | not done | The three `[TBD]` placeholders remain (`grep -n "TODO(dates)" docs/*.tex`). |

**Rebuilt PDF:** `docs/Exercise03.pdf` was built again with the stand-in header style (see §0); recompile with the real `common/` before release.

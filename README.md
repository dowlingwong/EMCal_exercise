# EMCal Exercises

This repo bundles two teaching exercises:
- **Exercise 03 (EMCal clustering)**: electromagnetic calorimetry fundamentals, PHENIX EMCal geometry, and clustering of calorimeter hits. You work with provided ROOT samples (`electron`, `dielectron`, `Aprime`) to visualize showers, study moments, and implement/compare K-means (plus a seeded variant) for cluster finding.
- **Geant4 exercise**: intro to Geant4-based detector simulation. You drive the provided `geant4_simulation` Python package via the notebooks: select geometries/physics lists, initialize the kernel, shoot particles with chosen PDG codes/energies, and visualize the detector or runs.

## Repository layout
- `docs/` – handouts and sources for both exercises (`Exercise03.pdf/.tex`, `Geant4.pdf/.tex`).
- `data/exercise03/` – ROOT samples for the calorimetry tasks.
- `notebooks/exercise03/` – main and solution notebooks for Exercise 03.
- `notebooks/geant4/` – Part 1/2 notebooks and solutions for the Geant4 exercise.
- `src/exercise03/` – reusable helpers (`exercise3_utils.py`) for loading ROOT data.
- `src/geant4_simulation/` – Geant4 wrapper package with geometries, actions, and visualization macros.
- `assets/figures/exercise03/` – figures used by the EMCal handout.
- `tests/exercise03/` – standalone NumPy-based KMeans test harness.
- `archive/` – legacy/reference material kept out of the main workflow.

## Working with the notebooks
- Ensure Python has access to `src/` (the notebooks pre-pend it to `sys.path`). Exercise 03 depends on `numpy`, `matplotlib`, and `uproot`; the Geant4 notebooks additionally require `Geant4Py` bindings and `kafe2` (as referenced in Part 2).
- Exercise 03 notebooks use `exercise3_utils` to load data from `data/exercise03/` and apply basic energy masking; adjust `DATA_DIR` there if you relocate data.
- Geant4 notebooks import `geant4_simulation`; geometries/macros are resolved relative to `src/geant4_simulation` so they work from the repo root.

## Running tests
- KMeans harness: `python3 tests/exercise03/unit_test.py` (expects a `KMeans` class on the import path or in the current working directory).

## License
- Licensed under the MIT License (see `LICENSE`).

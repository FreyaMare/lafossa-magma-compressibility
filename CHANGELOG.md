# Changelog

## [Windows app 1.0.1] — 2026-10-27
### Added
- `windows_app/`: Windows desktop edition of the any-volcano notebook (PySide6), with installer and portable
  version. It runs the notebook's cells verbatim, so its results are identical; fill-in tables with Excel copy and
  paste, ready-made volcanoes, project files, Excel and HTML export, uplift map, EVo calculator, a user guide for
  first-time users, and self-tests (`--selftest`, `--check-all`).
- `notebooks/Magma_Compressibility_Uplift_AnyVolcano.ipynb`: the chain for any volcano, any number of magmas and
  reservoirs, all source shapes, EVo modes, redox options and fugacities; EVo 1.1.0 and dmodelspy 0.2 embedded;
  ready-made inputs for Etna, Campi Flegrei and Kīlauea.
- `docs/Input_data_Etna_CampiFlegrei_Kilauea.pdf`: every input value of the ready-made volcanoes with its source.
- `.github/workflows/windows-app.yml`: builds the app on Windows, installs it, tests the installed program and
  drafts a release with the installer.

## [1.0.0] — 2026-09-22
First public release, accompanying the MSc thesis.

### Added
- Complete seven-step chain (depth → pressure → EVo gas state → β_m → β_c → r_V → ΔV_c → uplift) for the 13 configurations of the FREYA scheme.
- All results displayed on the notebook page: input tables, reservoir states, gas speciation and fugacities, compressibilities, r_V, volume changes, the five completed scheme tables, shape (depth) diagnostic, inverse detectability analysis with admissibility screen, thin-crack consistency check, validation against Di Traglia et al. (2023), three figures and the complete results table.
- Lever defaults set to the published/measured values (Scenario A).
- EVo pinned to commit `2487939` (v1.1.0) for reproducibility.
- Automated test that executes the notebook and checks r_V and uplift against the reference values.

### Fixed
- EVo stops with a bare `exit()`, which is undefined inside Jupyter/Colab kernels. The resulting `NameError` made earlier versions silently fall back to the analytical solubility model for undersaturated reservoirs, so saturation pressures were not reported (uplift values were unaffected because φ = 0 in both cases). Every EVo module now receives an `exit()` that raises `SystemExit`, and EVo is used for all configurations.
- NumPy ≥ 2 compatibility of `dmodelspy` (Gauss–Legendre nodes; point-wise crack displacement kernel).
- Lever defaults of earlier drafts (e.g. aspect 0.5, dip 80°, μ 20/2 GPa, H₂O 2–3 wt%) replaced by the published values.

### Removed
- Word, Excel and CSV outputs (everything is now shown on the page).

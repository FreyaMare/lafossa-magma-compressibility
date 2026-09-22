# Changelog

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

# La Fossa (Vulcano) — from magma compressibility to surface uplift

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/FreyaMare/lafossa-magma-compressibility/blob/main/notebooks/LaFossa_Vulcano_uplift_EVo.ipynb)
[![tests](https://github.com/FreyaMare/lafossa-magma-compressibility/actions/workflows/tests.yml/badge.svg)](https://github.com/FreyaMare/lafossa-magma-compressibility/actions/workflows/tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

A reproducible Google Colab notebook that predicts how much the ground at **La Fossa volcano (Vulcano Island, Aeolian Arc, Italy)** rises when magma is injected into each storage level of its plumbing system — and, inverted, how much magma a given uplift implies.

It couples the thermodynamic degassing code **[EVo](https://github.com/pipliggins/EVo)** to the analytical deformation sources of **dMODELS** (Mogi sphere, Yang prolate spheroid, Fialko penny-shaped crack), using melt compositions, temperatures and volatile budgets **measured** at Vulcano rather than assumed ones. Everything is displayed directly on the notebook page: no files are written.

This code accompanies the MSc thesis *"From magma compressibility to surface deformation at La Fossa volcano (Vulcano Island, Italy)"*.

---

## Contents

- [Why this matters](#why-this-matters)
- [The seven-step chain](#the-seven-step-chain)
- [Quick start](#quick-start)
- [What the notebook shows](#what-the-notebook-shows)
- [Levers (adjustable inputs)](#levers-adjustable-inputs)
- [Key results](#key-results)
- [Validation](#validation)
- [Assumptions and limitations](#assumptions-and-limitations)
- [Repository structure](#repository-structure)
- [Running locally and testing](#running-locally-and-testing)
- [Citation](#citation)
- [Licence](#licence)
- [References](#references)

---

## Why this matters

Geodesy (InSAR, GNSS) measures how much a volcano's surface moves. It is tempting to read the source volume change inverted from that signal as the volume of magma that moved. It is not. When magma is injected into a reservoir, part of the injected volume is taken up by **compressing the resident magma**, and only the rest dilates the cavity and lifts the ground. The partitioning is set by the factor

$$r_V = 1 + \frac{\beta_m}{\beta_c}$$

where $\beta_m$ is the compressibility of the magma (dominated by its exsolved gas) and $\beta_c$ that of the reservoir (set by its shape and by the host-rock stiffness) (Rivalta & Segall, 2008). An injected volume $V_e$ produces a cavity volume change of only $\Delta V_c = V_e / r_V$. For gas-free magma $r_V \approx 1$–3; for gas-rich magma in a stiff reservoir it can exceed 10, so that most of an intrusion is invisible at the surface.

This notebook computes $r_V$ — and the resulting uplift — for every storage level of Vulcano from measured petrological data.

## The seven-step chain

| Step | Quantity | How it is computed |
|---|---|---|
| 1 | Pressure $P$ | $P = \rho_c g z$ (lithostatic) |
| 2 | Gas volume fraction $\varphi$, saturation pressure, fugacities | **EVo**, closed-system C–O–H–S equilibrium at $f_{O_2}$ = FMQ+1 |
| 3 | Magma compressibility | $\beta_m = \varphi\,\beta_{gas} + (1-\varphi)\,\beta_{liquid}$, with $\beta_{gas} = 1/P$ |
| 4 | Chamber compressibility $\beta_c$ | sphere $3/4\mu$; prolate spheroid (Amoruso & Crescentini 2009); penny crack (Fialko et al. 2001, half-space) |
| 5 | Partitioning factor | $r_V = 1 + \beta_m/\beta_c$ |
| 6 | Reservoir volume change | $\Delta V_c = V_e / r_V$ |
| 7 | Surface uplift | Mogi (1958); Yang et al. (1988) with Newman et al. (2006); Fialko et al. (2001) — via `dmodelspy` |

The scenario matrix (the "FREYA" scheme) crosses three magmatic storage levels — **rhyolite at 2 km, trachyte at 5 km, latite at 12 km** — with three source geometries and three injected volumes each, plus the **2021 unrest source** of Di Traglia et al. (2023) at 598 m below sea level: 13 configurations × 3 volumes = 39 forward cases.

## Quick start

**In the browser (recommended, nothing to install):**

1. Click the **Open in Colab** badge above.
2. *Runtime ▸ Run all*.
3. Scroll down: all tables and figures appear under the cells. A full run takes well under a minute after the first installation step (about 1–2 minutes, once per session).

Cell 1 installs `dmodelspy` and clones EVo from GitHub, pinned to the exact commit used for the thesis results. No account, key or upload is needed.

## What the notebook shows

| Cell | Output on the page |
|---|---|
| 1 | Environment check; loads the on-screen table toolkit |
| 2 | Table of the physical parameters in use |
| 3 | Table of the magmatic inputs with their sources |
| 4 | Oxide compositions of the four melts, with sample numbers (Gioncada et al. 1998, Table 1) |
| 5 | **Steps 1–6**: saturation state of every reservoir; gas speciation and fugacities (fH₂O, fCO₂, fSO₂, fH₂S) of the saturated magma; independent check of the saturation pressure; $\beta_m$, $\beta_c$, $r_V$ for all 13 configurations; frozen vs. equilibrium compressibility; reservoir volume changes |
| 6 | **Step 7**: the five completed scheme tables (Mogi, Yang, penny cracks of 0.5/1/2 km) with uplift at the centre, 1 km and 2 km; a table of shape ratios usable as a depth indicator |
| 7 | Injected volume and overpressure needed for a chosen uplift (default 10 mm), with a mechanical-admissibility screen; thin-crack consistency of the penny reservoirs; validation against the published 2021 source |
| 8 | Three figures (radial profiles, $r_V$ and detectability, map view of the 2021 source) and the complete numerical results table |

## Levers (adjustable inputs)

All physical choices are Colab form fields. Defaults reproduce **Scenario A** of the thesis exactly.

**Cell 2 — physical**

| Lever | Default | Source |
|---|---|---|
| `rho_crust` | 2500 kg m⁻³ | assumed; 2300–2700 explored |
| `mu_crust_GPa` / `nu` | 10 GPa / 0.25 | intact rock, Heap et al. (2020) |
| `mu_shallow_GPa` / `nu_shallow` | 1 GPa / 0.35 | altered rock, Heap et al. (2020); Di Traglia et al. (2023) |
| `dFMQ` | +1.0 | oxidised arc magmas |
| `yang_aspect`, `yang_dip`, `yang_strike` | 0.099, 69°, 137° | Di Traglia et al. (2023), Table S1 (ν = 0.35) |
| `yang_overburden_km` | 0.598 km | pressure datum of the shallow source (see limitations) |
| `use_evo` | True | False → simple analytical solubility model |

**Cell 3 — magmatic (Scenario A: measured melt-inclusion budgets)**

| Magma (level) | T (°C) | H₂O (wt%) | CO₂ (wt%) | S (wt%) | β_liquid (Pa⁻¹) |
|---|---|---|---|---|---|
| Rhyolite (2 km, 2021 level) | 1000 | 1.25 | 0.005 | 0.02 | 1.2×10⁻¹⁰ |
| Trachyte (5 km) | 1075 | 1.25 | 0.005 | 0.07 | 1.1×10⁻¹⁰ |
| Latite (12 km) | 1080 | 1.35 | 0.005 | 0.10 | 1.0×10⁻¹⁰ |
| Shoshonite (recharge) | 1100 | 0.85 | 0.022 | 0.03 | 0.8×10⁻¹⁰ |

**Cell 7 — detectability:** `target_uplift_mm` (10 mm) and `max_admissible_dP_MPa` (10 MPa).

After changing a lever, use *Runtime ▸ Run after* on the cell below it. Full provenance of every default is in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Key results

With the default (measured) inputs:

- **Only the shallowest reservoir is gas-saturated.** The rhyolite at the 2021 source level holds φ = 15.5 vol% of vapour (r_V = 11.9, so 92% of any injection is absorbed by compression). The reservoirs at 2, 5 and 12 km are undersaturated (saturation pressures 29.8, 53.7 and 55.9 MPa against storage pressures of 49, 123 and 294 MPa), because the melt-inclusion budgets were trapped at shallow level after degassing.
- The computed saturation pressure of the rhyolite, **29.8 MPa**, agrees with fluid-inclusion barometry (30–60 MPa; Clocchiatti et al. 1994) and gas-chemistry modelling (38 MPa; Paonita et al. 2013).
- $r_V$ ranges from 1.03 (wide shallow sill) to 201 (narrow deep crack); spheres give 2.3–2.6 at all depths.
- **1 cm of central uplift** needs 1.3–4.4 × 10⁵ m³ of magma from 0.6–2 km, but ~1.3–1.4 × 10⁷ m³ from 12 km. Three crack configurations would need 15–121 MPa of overpressure and are mechanically inadmissible.
- The **shape** of the uplift field — e.g. $u_z(2\,\mathrm{km})/u_z(0)$ = 0.02, 0.35, 0.80, 0.96 for sources at 0.6, 2, 5, 12 km — is a depth indicator independent of volume and $r_V$.

## Validation

Against the 2021 source of Di Traglia et al. (2023, Supporting Information, Table S1):

| Quantity | This code | Published |
|---|---|---|
| β_c·μ of the spheroid | 0.978 | 0.976 (from k = 11.6×10⁻⁸ m⁻³) |
| ΔV_c at ΔP = 8.48 MPa | 73,229 m³ | 73,108 ± 6,900 m³ |
| ΔP for ΔV_c = 73,108 m³ | 8.47 MPa | 8.48 MPa |
| β_c·μ at ν = 0.25–0.45 (five inversions) | 0.977–0.978 | 0.976–0.980 |
| Vertical uplift above the centroid | 36.8 mm | cm-scale, confined to the crater |

Because Di Traglia et al. also used dMODELS (same Amoruso & Crescentini expression), this demonstrates implementation equivalence; the physical accuracy of the expression is set by its exact limits (sphere 0.3%, needle 2.8%). Two probable misprints in the published tables are documented in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

The automated test in `tests/` executes the whole notebook and checks every $r_V$ and uplift value against the reference results.

## Assumptions and limitations

- **Elastic half-space**: homogeneous, isotropic, flat surface at sea level; the 391 m La Fossa cone and elastic layering are not resolved.
- **Static**: end-state displacements; no viscoelastic, poroelastic or time-dependent effects.
- **Ideal gas** ($\beta_{gas} = 1/P$) and **frozen phases** during pressurisation. The equilibrium (reactive) compressibility is reported as an upper bound — for the shallow reservoir it is 3.8× larger.
- **Full-space vs half-space**: the spheroid's β_c is a full-space expression (standard for ellipsoidal sources); the crack's is half-space. For the 2021 source (a/d ≈ 1) this plausibly underestimates β_c, making its results conservative.
- **Thin-crack condition**: 6 of the 9 penny configurations of the scheme violate it; they are flagged on the page and should be read as stiff-walled idealisations.
- **Pressure datum** of the shallow source is the single most sensitive choice (see `yang_overburden_km`).
- The 2021 source is interpreted by Di Traglia et al. (2023) as **hydrothermal**; applying a magmatic β_m to it is an extension of the framework, not a reconstruction of the event.

## Repository structure

```
lafossa-magma-compressibility/
├── notebooks/
│   └── LaFossa_Vulcano_uplift_EVo.ipynb   # the notebook (8 code cells)
├── docs/
│   ├── DATA_SOURCES.md                    # provenance of every input value
│   ├── METHODS.md                         # equations of the chain
│   └── example_output.html                # a full rendered run (open in a browser)
├── tests/
│   └── test_notebook.py                   # executes the notebook, checks the numbers
├── .github/workflows/tests.yml            # runs the test on every push
├── requirements.txt
├── environment.yml
├── CITATION.cff
├── CHANGELOG.md
├── LICENSE                                # GPL-3.0
└── README.md
```

## Running locally and testing

```bash
git clone https://github.com/USERNAME/lafossa-magma-compressibility.git
cd lafossa-magma-compressibility
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab notebooks/LaFossa_Vulcano_uplift_EVo.ipynb
```

Cell 1 clones EVo into the working folder (pinned commit `2487939`). To run the test suite:

```bash
pip install pytest nbclient nbformat ipykernel
pytest -v tests/
```

Tested with Python 3.12, NumPy 2.4, SciPy 1.17, pandas 3.0, Matplotlib 3.10, dmodelspy 0.2 and EVo 1.1.0.

## Citation

If you use this code, please cite the thesis (see [`CITATION.cff`](CITATION.cff); GitHub shows a *Cite this repository* button) and the underlying tools: EVo (Liggins et al. 2020, 2022), dMODELS (Battaglia et al. 2013) and the source models.

## Licence

**GPL-3.0-or-later.** The notebook imports EVo, which is distributed under GPL-3.0; licensing this repository under the same terms keeps the combined work compatible. EVo itself is not redistributed here — it is cloned from its own repository at run time. `dmodelspy` is installed from PyPI under its own terms.

## References

- Amoruso, A., & Crescentini, L. (2009). *J. Geophys. Res.*, 114, B02210.
- Battaglia, M., Cervelli, P. F., & Murray, J. R. (2013). dMODELS. *J. Volcanol. Geotherm. Res.*, 254, 1–4.
- Burgisser, A., Alletti, M., & Scaillet, B. (2015). *Comput. Geosci.*, 79, 1–14.
- Clocchiatti, R., et al. (1994). *Bull. Volcanol.*, 56, 466–486.
- Di Traglia, F., et al. (2023). *Geophys. Res. Lett.*, 50, e2023GL104952.
- Fialko, Y., Khazan, Y., & Simons, M. (2001). *Geophys. J. Int.*, 146, 181–190.
- Fusillo, R., et al. (2015). *Bull. Volcanol.*, 77, 76.
- Gioncada, A., et al. (1998). *Bull. Volcanol.*, 60, 286–306.
- Heap, M. J., et al. (2020). *J. Volcanol. Geotherm. Res.*, 390, 106684.
- Kilbride, B. M., Edmonds, M., & Biggs, J. (2016). *Nat. Commun.*, 7, 13744.
- Liggins, P., Shorttle, O., & Rimmer, P. B. (2020). *Earth Planet. Sci. Lett.*, 550, 116546.
- Liggins, P., et al. (2022). *J. Geophys. Res. Planets*, 127, e2021JE007123.
- Mogi, K. (1958). *Bull. Earthq. Res. Inst. Univ. Tokyo*, 36, 99–134.
- Newman, A. V., Dixon, T. H., & Gourmelen, N. (2006). *J. Volcanol. Geotherm. Res.*, 150, 244–269.
- Paonita, A., et al. (2013). *Geochim. Cosmochim. Acta*, 120, 158–178.
- Rivalta, E., & Segall, P. (2008). *Geophys. Res. Lett.*, 35, L04306.
- Segall, P. (2010). *Earthquake and Volcano Deformation*. Princeton University Press.
- Yang, X.-M., Davis, P. M., & Dieterich, J. H. (1988). *J. Geophys. Res.*, 93(B5), 4249–4257.

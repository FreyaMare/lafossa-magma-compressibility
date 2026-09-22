# Data sources and provenance

Every default value in the notebook is traced below to a specific table or statement in a published source. Values were extracted from the source documents programmatically; recalculated analyses were checked to sum to 100.00 ± 0.02 wt%.

## 1. Melt compositions (cell 4)

Gioncada et al. (1998), *Bull. Volcanol.* 60, 286–306, **Table 1** — bulk-rock analyses of the same samples used for the melt-inclusion volatile data. All iron is reported as Fe₂O₃ in the source and converted to FeO(tot) = 0.8998 × Fe₂O₃(tot) for EVo.

| Oxide (wt%) | Rhyolite | Trachyte | Latite | Shoshonite |
|---|---|---|---|---|
| Sample | GS91-50c | Palizzi pumices, TR column* | GS91-17 | GS91-66 |
| Unit | 1888–90 eruption | Palizzi pumices | Pietre Cotte | Vulcanello I |
| SiO₂ | 73.54 | 61.60 | 57.45 | 53.79 |
| TiO₂ | 0.13 | 0.61 | 0.61 | 0.70 |
| Al₂O₃ | 13.10 | 17.51 | 16.83 | 15.08 |
| FeO(tot) | 2.21 | 4.30 | 6.60 | 8.16 |
| MnO | 0.07 | 0.10 | 0.14 | 0.16 |
| MgO | 0.34 | 1.25 | 2.58 | 4.70 |
| CaO | 1.02 | 2.25 | 5.17 | 7.67 |
| Na₂O | 4.35 | 4.42 | 3.81 | 3.55 |
| K₂O | 4.95 | 7.25 | 5.67 | 4.89 |
| P₂O₅ | 0.04 | 0.22 | 0.43 | 0.39 |
| EVo solubility class | rhyolite | phonolite | phonolite | basalt |

\* The trachyte column carries no printed sample number in the original table; the adjacent identifier GS93-71 belongs to the Palizzi *latite* (SiO₂ 57.36). This was established by reconstructing the word coordinates of the printed table. An alternative trachyte with a printed ID (GS91-42a, SiO₂ 65.43) is noted in the code.

## 2. Temperatures (cell 3)

| Magma | Value | Basis | Source |
|---|---|---|---|
| Rhyolite | 1000 °C | rhyolites ~1000 °C; 1000–1030 °C | Clocchiatti et al. (1994) |
| Trachyte | 1075 °C | latites and trachytes 1050–1100 °C | Clocchiatti et al. (1994) |
| Latite | 1080 °C | 1080 ± 10 °C; also used in degassing models | Gioncada et al. (1998); Paonita et al. (2013) |
| Shoshonite | 1100 °C | Vulcanello microthermometry | Fusillo et al. (2015) |

## 3. Volatile budgets (cell 3, Scenario A)

| Species | Value | Measured range and basis | Source |
|---|---|---|---|
| H₂O rhyolite / trachyte | 1.25 wt% | 1.0–1.5 wt% dissolved in the 1888–90 magmas | Clocchiatti et al. (1994); Paonita et al. (2013) |
| H₂O latite | 1.35 wt% | 0.8–1.9 wt% in latite melt inclusions | Gioncada et al. (1998) |
| H₂O shoshonite | 0.85 wt% | 0.36–1.32 wt% in 18 Vulcanello inclusions | Fusillo et al. (2015) |
| CO₂ evolved magmas | 0.005 wt% | below detection (≤ 50 ppm) in every inclusion | Gioncada et al. (1998); Fusillo et al. (2015) |
| CO₂ shoshonite | 0.022 wt% | 220 ppm needed for the basalt to exsolve a 25 mol% CO₂ vapour at 100 MPa | Paonita et al. (2013), App. A.1 |
| S rhyolite | 0.02 wt% | below detection in groundmass; conservative | Gioncada et al. (1998) |
| S trachyte / latite | 0.07 / 0.10 wt% | ~700 / ~1000 ppm | Gioncada et al. (1998) |
| S shoshonite | 0.03 wt% | 100–500 ppm in Vulcanello inclusions | Fusillo et al. (2015) |

These budgets were trapped at shallow level after degassing, which is why the deep reservoirs come out undersaturated. Pre-degassing budgets can be explored by raising the H₂O and CO₂ levers (Scenario B of the thesis).

## 4. Storage levels and scenario (cell 5)

| Level | Depth | Resident / injected | V₀ (m³) | V_e (m³) | Basis |
|---|---|---|---|---|---|
| 2021 source | 0.598 km b.s.l. | rhyolite / trachyte | 8.83×10⁶ | 10⁵, 5×10⁵, 10⁶ | Di Traglia et al. (2023), Table S1 |
| Shallow | 2 km | rhyolite / trachyte | 5×10⁸ | 10⁶, 5×10⁶, 10⁷ | fluid-inclusion barometry 30–60 MPa (Clocchiatti et al. 1994) |
| Intermediate | 5 km | trachyte / latite | 5×10⁹ | 10⁶, 5×10⁶, 10⁷ | density barrier (Peccerillo et al. 2006; Paonita et al. 2013) |
| Deep | 12 km | latite / shoshonite | 5×10¹⁰ | 10⁶, 5×10⁶, 10⁷ | granulite–metapelite boundary (Zanon et al. 2003) |

## 5. Mechanical parameters (cell 2)

| Parameter | Value | Source |
|---|---|---|
| Spheroid semi-axes | 595 ± 60 / 59 ± 40 m (A = 0.099) | Di Traglia et al. (2023), Table S1, ν = 0.35 |
| Dip / azimuth | 69 ± 2° / 137 ± 5° | same |
| Source volume | 8.83×10⁶ m³ | same |
| k, ΔV, ΔP (validation targets) | 11.6×10⁻⁸ m⁻³; 73,108 ± 6,900 m³; 8.48 MPa | same |
| μ shallow / deep | 1 / 10 GPa | Heap et al. (2020), as adopted by Di Traglia et al. (2023) |
| ν shallow / deep | 0.35 / 0.25 | same |
| β_liquid | (0.8–1.2)×10⁻¹⁰ Pa⁻¹ | Spera (2000); Rivalta & Segall (2008) |

## 6. Notes on three published values

1. The main text of Di Traglia et al. (2023) gives a total volume change of 7.31 ± 0.69 × 10⁵ m³; Supporting Information Table S1 gives 73,108 ± 6,900 m³ and the SI text "about 73,000 m³". The SI value is consistent with the published pressure–volume factor and the observed displacements and is used here.
2. The crack factor k listed for ν = 0.35 in Table S3 is ≈46% above the trend of its own column; treated as a probable misprint.
3. The spheroid factor k listed for ν = 0.25 in Table S1 is printed as 3.91×10⁻³ m⁻³, three orders of magnitude above its neighbours; read as 3.91×10⁻⁸ m⁻³ it matches the geometry to 0.2%.

None of these affects the conclusions of the source publication.

## References

Clocchiatti et al. (1994) *Bull. Volcanol.* 56, 466–486 · Di Traglia et al. (2023) *GRL* 50, e2023GL104952 · Fusillo et al. (2015) *Bull. Volcanol.* 77, 76 · Gioncada et al. (1998) *Bull. Volcanol.* 60, 286–306 · Heap et al. (2020) *JVGR* 390, 106684 · Paonita et al. (2013) *GCA* 120, 158–178 · Peccerillo et al. (2006) *Geology* 34(1), 17–20 · Rivalta & Segall (2008) *GRL* 35, L04306 · Spera (2000) *Encyclopedia of Volcanoes*, 171–190 · Zanon et al. (2003) *J. Geophys. Res.* 108(B6), 2298.

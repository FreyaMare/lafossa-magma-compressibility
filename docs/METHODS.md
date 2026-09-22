# Methods: the seven-step chain

Equation numbers refer to Chapter 3 of the thesis.

## 1. Lithostatic pressure
$$P(z) = \rho_c\, g\, z \qquad (3.1)$$
$z$ is the depth below the ground surface; source depths for the deformation models are referred to the free surface of the half-space (≈ sea level). For the shallow source the pressure datum is a lever (`yang_overburden_km`).

## 2. Volatile equilibrium (EVo)
EVo (Liggins et al. 2020, 2022) solves the closed-system C–O–H–S equilibrium between melt and vapour: power-law solubilities of Burgisser et al. (2015), homogeneous gas equilibria (H₂/H₂O, CO/CO₂, S₂/SO₂/H₂S), fugacities $f_i = \gamma_i x_i P$, $f_{O_2}$ buffered at FMQ + ΔFMQ (Frost 1991) and coupled to the ferric–ferrous equilibrium (Kress & Carmichael 1991). In `FIND_SATURATION` mode EVo locates the saturation pressure $P_{sat}$ of the total volatile budget and decompresses to the reservoir pressure. If $P_{sat} < P$ the magma is undersaturated and $\varphi = 0$.

Gas volume fraction:
$$\varphi = \frac{w_g/\rho_g}{w_g/\rho_g + (1-w_g)/\rho_l} \qquad (3.7)$$

## 3. Magma compressibility
$$\beta_{gas} = 1/P \quad (3.10), \qquad \beta_m = \varphi\,\beta_{gas} + (1-\varphi)\,\beta_{liquid} \quad (3.12)$$
The equilibrium (reactive) compressibility, including re-dissolution of vapour, is reported as a diagnostic upper bound:
$$\beta_m^{eff} = -\,\Delta \ln \rho_{bulk} / \Delta P \qquad (3.13)$$

## 4. Chamber compressibility
$$\beta_c = \frac{1}{V_0}\frac{dV_c}{dP} \qquad (3.14)$$
- Sphere: $\beta_c = 3/(4\mu)$ (3.15), independent of size.
- Prolate spheroid, $A = b/a$ (Amoruso & Crescentini 2009; full space): $\beta_c = \frac{3}{4\mu}\left[\frac{A^2}{3} - 0.7A + 1.37\right]$ (3.17). Exact limits: 0.3% at the sphere, 2.8% at the needle ($1/\mu$).
- Penny-shaped crack: Fialko et al. (2001) half-space solution; full-space limit $\Delta V_c = 8(1-\nu)a^3\Delta P/(3\mu)$ (3.18), so $\beta_c = 8(1-\nu)a^3/(3\mu V_0)$ (3.19). Valid for $\bar w/(2a) \ll 1$ with $\bar w = V_0/(\pi a^2)$.

## 5–6. Volume partitioning
$$V_e = (\beta_c + \beta_m)\,V_0\,\Delta P \quad (3.20), \qquad \Delta P = \frac{V_e}{(\beta_c+\beta_m)V_0} \quad (3.21)$$
$$\Delta V_c = \frac{V_e}{r_V}, \qquad r_V = 1 + \frac{\beta_m}{\beta_c} \qquad (3.22)$$
For a sphere this reduces to $r_V = 1 + 4\mu\beta_m/3$ (Rivalta & Segall 2008).

## 7. Surface displacement
Mogi point source:
$$u_z(r) = \frac{(1-\nu)\,\Delta V_c\, d}{\pi\,(d^2 + r^2)^{3/2}} \qquad (3.23)$$
Yang et al. (1988) spheroid with Newman et al. (2006) corrections, and the Fialko et al. (2001) crack, via `dmodelspy`. All three are linear in source strength: each is evaluated once at a reference pressure and scaled by $\Delta V_c/\Delta V_{ref}$.

## Inverse use
For a target central uplift $u^*$: $V_e = V_e^{(3)}\, u^*/u_z^{(3)}(0)$; the required overpressure follows from (3.21) and is screened against a strength limit (default 10 MPa).

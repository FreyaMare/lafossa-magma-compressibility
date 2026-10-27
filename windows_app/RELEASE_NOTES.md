**Magma Compressibility and Surface Uplift** is a Windows desktop program that calculates how much of a magma volume injected into a reservoir is taken up by compressing the magma already stored there — mostly its gas bubbles — and how much lifts the ground surface. It works for any volcano, from the chemistry of the magma (thermodynamic degassing model **EVo**) to the surface uplift (**dMODELS** deformation sources).

Developed by **Freya Mohammadian** · [freya.mohammadian@gmail.com](mailto:freya.mohammadian@gmail.com) · [GitHub](https://github.com/FreyaMare) · [LinkedIn](https://www.linkedin.com/in/freya-mohammadian-14614a135)

### Download

| File | What it is |
|---|---|
| **`MagmaUplift_Setup_*.exe`** | Installer (recommended). No administrator rights needed; Start-menu entry; uninstall from *Settings ▸ Apps*. |
| `MagmaUplift_portable.zip` | The same program without installation: unzip and run `MagmaUplift.exe`. |
| `test_results.zip` | Results of the automatic tests of this build on Windows, with screenshots. |

Windows 10 or 11 (64-bit), about 300 MB of disk space. Python is not needed. Windows may warn *“Windows protected your PC”* because the installer is not code-signed: click **More info ▸ Run anyway**.

### Getting started

Click **Examples ▾** (La Fossa, Etna, Campi Flegrei, Kīlauea), press **▶ Run** (F5), and read the **Results** and **Report** tabs. The **User guide** tab explains every step, every table row and column, and how to describe your own volcano.

### What's new in 1.0.1

- New **About** window with the developer's contact details.
- Rewritten **User guide** for first-time users: quick start, every tab, your own volcano step by step, reservoir shapes, EVo modes, reading the results, reference tables and troubleshooting.
- Clear **tab names** (Magmas, Reservoirs, Manual EVo values, Settings, Results, Report, Uplift map, EVo calculator, User guide); texts no longer refer to notebook cell numbers.

### Verified

Each build is installed and tested on Windows by the repository's workflow: the four ready-made volcanoes and a test volcano that uses every EVo mode reproduce the notebook results to within 10⁻¹⁵ (rounding), and the EVo calculator, the uplift map and the window are checked.

### Licence

GPL-3.0-or-later. Contains EVo 1.1.0 (Liggins, Shorttle & Rimmer; GPL-3.0) and dmodelspy 0.2 (Python port of dMODELS, Battaglia, Cervelli & Murray; GPL-3.0). Source code: the [`windows_app`](https://github.com/FreyaMare/lafossa-magma-compressibility/tree/main/windows_app) folder of this repository.

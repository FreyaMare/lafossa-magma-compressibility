# Magma Compressibility and Surface Uplift — Windows program

Desktop version of the notebook *Magma_Compressibility_Uplift_AnyVolcano.ipynb*:
EVo (step 2) + magma and chamber compressibility + dMODELS deformation sources (steps 3–7), for any volcano.

---

## راهنمای سریع ساخت برنامه (فارسی)

1. **پایتون** را نصب کنید (فقط یک بار): نسخه‌ی 3.12، 3.13 یا 3.14 از
   https://www.python.org/downloads/windows/ — هنگام نصب گزینه‌ی **Add python.exe to PATH** را تیک بزنید.
   (یا در Command Prompt:  `winget install -e --id Python.Python.3.13`)
2. این پوشه را از حالت فشرده (zip) خارج کنید، مثلاً در `C:\MagmaUplift_build`
   (بهتر است مسیر پوشه کوتاه باشد و داخل OneDrive نباشد).
3. روی فایل **`build_windows.bat`** دوبار کلیک کنید. بار اول حدود ۴۰۰ مگابایت بسته دانلود می‌شود و ساخت
   حدود ۵ تا ۱۵ دقیقه طول می‌کشد. اسکریپت خودش محاسبات را قبل و بعد از ساخت آزمایش می‌کند.
4. برای ساختن فایل نصب (setup.exe) برنامه‌ی رایگان **Inno Setup** لازم است؛ اگر نصب نباشد اسکریپت می‌پرسد
   که آن را با winget نصب کند (کلید Y).
5. نتیجه در پوشه‌ی `output`:
   - `MagmaUplift_Setup_1.0.1.exe` — فایل نصب (بدون نیاز به دسترسی Administrator؛ میانبر در منوی Start،
     حذف از Settings ▸ Apps)
   - `MagmaUplift_portable.zip` — همان برنامه بدون نصب (از حالت فشرده خارج کنید و `MagmaUplift.exe` را اجرا کنید)

برنامه‌ی نصب‌شده به پایتون و اینترنت نیازی ندارد و می‌توانید فایل setup را به دیگران بدهید. چون فایل امضای
دیجیتال ندارد، ویندوز روی کامپیوتر دیگران ممکن است پیام «Windows protected your PC» نشان دهد:
**More info ▸ Run anyway**.

---

## Building (English)

Requirements: Windows 10/11 (64-bit), Python 3.12, 3.13 or 3.14 from python.org, internet for the first build,
about 3 GB of free disk space.

Double-click `build_windows.bat`. It

1. finds Python and creates a private environment `.venv-build` with the exact package versions of
   `requirements.txt` / `constraints.txt` (the versions the program was tested with);
2. runs the self-test of the calculation from the source code;
3. builds the program with PyInstaller (`MagmaUplift.spec`) into `dist\MagmaUplift`;
4. runs the self-test again inside the built program;
5. writes `output\MagmaUplift_portable.zip` and, with Inno Setup 6 (offered via winget if missing),
   the installer `output\MagmaUplift_Setup_1.0.1.exe` (`installer.iss`).

Command-line options of the program:

| Command | What it does |
|---|---|
| `MagmaUplift.exe` | opens the window (restores your last session) |
| `MagmaUplift.exe project.mcu` | opens a project file |
| `MagmaUplift.exe --selftest [file]` | thesis example, compared with the verified notebook results (≈ 10 s) |
| `MagmaUplift.exe --check-all [file]` | the four ready-made volcanoes, a test volcano using every EVo mode, the EVo calculator and the map (≈ 2 min) |

The result of `--selftest` / `--check-all` is written to `selftest_result.txt` / `check_all_result.txt` next to
the program (or to the file given).

Without building, the program also runs directly from this folder:
`python -m pip install -r requirements.txt` and then `python run_app.py`.

## Using the program

| Tab | Notebook cell | Contents |
|---|---|---|
| Magmas | 5 | one column per magma (fill-in table) |
| Reservoirs | 6 | one row per reservoir or geometry |
| Step 2 by hand | 8 | optional values that replace EVo for chosen reservoirs |
| Settings | 4, 7, 12, 14, 18 | crust, elasticity, observation points, EVo options, report options |
| Results | 11, 13 | the result table (main or all columns) |
| Report | 10–18 | every table, note and figure of the notebook; save as HTML or open in the browser |
| Map | 16 | uplift map of one reservoir |
| EVo calculator | 17 | one magma at any pressure |
| Guide | — | the notebook's introduction, input guide and references |

* **Examples ▾** loads La Fossa (thesis), Etna, Campi Flegrei or Kīlauea; **New** gives empty tables.
* Tables: double-click or type to edit; Ctrl+C / Ctrl+V copy and paste blocks of cells (also to and from Excel);
  Delete empties the selected cells; Ctrl+Z / Ctrl+Y undo and redo; grey text shows what an empty cell means;
  a red cell is not a number. *Text view…* shows a table as text and accepts a pasted one.
* **▶ Run** (F5) runs the calculation; an input error is shown in plain words and the program switches to the
  table concerned.
* **Save / Open** keep projects as `.mcu` files; the last session is restored automatically.
* **Export to Excel** writes the results, the EVo states, the input tables and the settings.

## How the program is built

`magma_uplift/nbcells.py` holds the 18 code cells of the notebook, copied verbatim (EVo 1.1.0 and dmodelspy 0.2
are embedded in cells 2 and 3). `magma_uplift/runner.py` runs them in one Python namespace like a Jupyter
kernel: the form fields take the values of the Settings tab, the fill-in tables come from the window, and the
displayed HTML and figures go into the report. The results are therefore identical to the notebook's
(checked bit for bit for all four volcanoes and the test volcano). `hiddenimports.json` lists the modules the
cells import at run time, which PyInstaller cannot see by itself.

## Licence

EVo (P. Liggins, O. Shorttle, P. B. Rimmer; github.com/pipliggins/EVo) and dmodelspy (W. Crawford, Python port of
dMODELS, Battaglia, Cervelli & Murray 2013) are distributed under the GNU General Public License v3; this program
contains them and is distributed under the GNU GPL v3 or later (LICENSE.txt). If you give the program to others,
give them access to this source folder as well (for example through your GitHub repository).

"""The User guide tab: how to use the program, written for first-time users."""
import html

from . import __version__
from .terms import TAB, app_text

CSS = """<style>
body{font-family:'Segoe UI',Arial,sans-serif;font-size:10.5pt;color:#1b2631}
h1{color:#ffffff;background-color:#1F4E79;font-size:17pt;margin:0;padding:10px}
h2{color:#1F4E79;font-size:13.5pt;margin-top:22px;margin-bottom:6px;border-bottom:2px solid #1F4E79}
h3{color:#2E5D8A;font-size:11.5pt;margin-top:14px;margin-bottom:4px}
p{margin-top:4px;margin-bottom:6px;line-height:140%}
li{margin-bottom:3px}
table.t{border-collapse:collapse;margin-top:4px;margin-bottom:8px}
table.t th{background-color:#2E5D8A;color:#ffffff;font-weight:600;padding:5px 8px;text-align:left}
table.t td{padding:5px 8px;border:1px solid #cdd6e0;vertical-align:top}
td.grp{background-color:#dfe8f2;color:#1F4E79;font-weight:bold}
td.k{font-family:Consolas,'DejaVu Sans Mono',monospace;color:#5b6b7b;font-size:9.5pt}
td.step{background-color:#1F4E79;color:#ffffff;font-weight:bold;font-size:14pt;text-align:center}
td.box{background-color:#eef4fb}
td.tip{background-color:#fff8e1}
td.warn{background-color:#fdf0ef}
span.btn{background-color:#e8edf3;font-weight:bold;color:#1F4E79}
span.req{color:#c0392b;font-weight:bold}
.small{color:#5b6b7b;font-size:9.5pt}
</style>"""


def _btn(s):
    return f'<span class="btn">&nbsp;{s}&nbsp;</span>'


def _table(header, rows, widths=None):
    h = "".join(f'<th{f" width={widths[i]}" if widths else ""}>{c}</th>' for i, c in enumerate(header))
    body = []
    for r in rows:
        if isinstance(r, str):
            body.append(f'<tr><td class="grp" colspan="{len(header)}">{r}</td></tr>')
        else:
            body.append("<tr>" + "".join(c if c.startswith("<td") else f"<td>{c}</td>" for c in r) + "</tr>")
    return f'<table class="t" width="100%" cellspacing="0">{"<tr>" + h + "</tr>"}{"".join(body)}</table>'


# meanings for rows and columns whose field has no help text
MEANING = {
    "T_C": "Temperature of the magma.", "H2O_wt": "Water content of the magma.",
    "CO2_wt": "Carbon dioxide content.", "S_wt": "Sulfur content.",
    "fO2_value": "Number that goes with the redox reference: log units above the buffer (FMQ, NNO, IW) or fO₂ in bar "
                 "(absolute).",
    "atomic_H_ppm": "Total hydrogen in magma + gas.", "atomic_C_ppm": "Total carbon in magma + gas.",
    "atomic_S_ppm": "Total sulfur in magma + gas.", "atomic_N_ppm": "Total nitrogen in magma + gas.",
    "gas_wt": "Mass fraction of gas already present at the start pressure.",
    "fH2_bar": "Fugacity of H₂ in the gas.", "fH2O_bar": "Fugacity of H₂O in the gas.",
    "fCO2_bar": "Fugacity of CO₂ in the gas.",
    "SIO2": "Major-element oxides of the melt, volatile-free (as in a microprobe analysis).",
    "fallback_H2O_coeff": "Only for the simple model used when EVo is switched off.",
    "fallback_CO2_coeff": "Only for the simple model used when EVo is switched off.",
    "source": "Where the values come from (free text, shown in the report).",
    "name": "Any name; every reservoir needs a different one.", "phi_vol%": "Vapour (gas) volume fraction in the magma.",
    "reservoir": "Name of a reservoir of the Reservoirs tab.", "rho_melt": "Density of the melt.",
    "fSO2_bar": "Fugacity of SO₂.", "fH2S_bar": "Fugacity of H₂S.",
}
REQUIRED = {"magmas": {"evo_class", "T_C", "beta_liquid", "rho_melt", "H2O_wt", "SIO2", "FEO"},
            "reservoirs": {"name", "shape", "depth_km", "V0_m3", "Ve_m3", "resident"},
            "step2": {"reservoir", "phi_vol%"}}
for _ox in ("TIO2", "AL2O3", "FEO", "MNO", "MGO", "CAO", "NA2O", "K2O", "P2O5", "NIO", "CR2O3"):
    MEANING[_ox] = "Oxide content of the melt, wt% (volatile-free)."


def _field_rows(fields, table, name_row=None):
    rows, group = [], None
    if name_row:
        rows.append(name_row)
    for f in fields:
        if f["group"] != group:
            group = f["group"]
            rows.append(html.escape(app_text(group)))
        u = f["unit"].split(",")[0]
        unit = f" ({u})" if u and u not in ("optional", "spheroid") else ""
        req = ' <span class="req">●</span>' if f["key"] in REQUIRED[table] else ""
        more = " <span class='small'>(Show more)</span>" if f["optional"] else ""
        meaning = html.escape(app_text(f["help"]) or MEANING.get(f["key"], ""))
        if f["kind"] == "choice":
            vals = ", ".join(c[1] if isinstance(c, (list, tuple)) else c for c in f["choices"])
            meaning += f" <span class='small'>Choices: {html.escape(vals)}.</span>"
        rows.append([f"{html.escape(f['label'])}{unit}{req}{more}", f'<td class="k">{html.escape(f["key"])}</td>',
                     meaning])
    return rows


def guide_html(specs):
    T = TAB
    mag, res, s2 = specs["magmas"]["fields"], specs["reservoirs"]["fields"], specs["step2"]["fields"]
    toc = [("start", "Quick start — your first calculation in five steps"), ("window", "The window: toolbar and tabs"),
           ("tables", "Working with the tables"), ("own", "Your own volcano, step by step"),
           ("shapes", "Choosing a reservoir shape"), ("modes", "How to describe the volatiles (EVo modes)"),
           ("results", "Reading the results"), ("chain", "What the program calculates"),
           ("ref", "Reference: every row and column of the tables"), ("help", "Problems and questions"),
           ("credits", "Methods, assumptions and references")]
    out = [CSS, "<h1>&nbsp;User guide — Magma Compressibility and Surface Uplift</h1>",
           f"<p class='small'>Version {__version__} · developed by Freya Mohammadian</p>"]
    out.append(
        "<p>When magma is pushed into a reservoir under a volcano, the ground above rises. But not all of the new magma "
        "makes room for itself by expanding the reservoir: part of it is absorbed by <b>squeezing the magma that is "
        "already there</b> — above all its gas bubbles, which are very compressible. Only the rest lifts the surface. "
        "This program calculates that split for any volcano, from the chemistry of the magma (with the thermodynamic "
        "model <b>EVo</b>) to the uplift you would measure at the surface. It answers questions such as "
        "<i>“How much does the ground rise if 10 million m³ of magma enter a reservoir at 5 km depth?”</i></p>")
    out.append("<p><b>Contents</b><br>" + "<br>".join(f'{i + 1}.&nbsp;<a href="#{a}">{t}</a>'
                                                     for i, (a, t) in enumerate(toc)) + "</p>")

    # ------------------------------------------------------------------ 1 quick start
    steps = [
        ("Load an example", f"Click {_btn('Examples ▾')} and choose a volcano: <b>La Fossa</b> (Vulcano, the worked "
                            "example of the thesis), <b>Etna</b>, <b>Campi Flegrei</b> or <b>Kīlauea</b>. The tables are "
                            "filled with published values. (At the very first start La Fossa is already loaded.)"),
        ("Look at the inputs", f"Open the <b>{T['magmas']}</b> tab (one column per magma) and the "
                               f"<b>{T['reservoirs']}</b> tab (one row per reservoir). You can change any value."),
        ("Run", f"Press {_btn('▶ Run')} in the toolbar (or the F5 key). The bar at the bottom shows the progress. "
                "Most volcanoes take 5–15 seconds; magmas very rich in CO₂ (Kīlauea) about one minute."),
        ("Read the answer", f"The program opens the <b>{T['results']}</b> tab: one line per reservoir with the gas "
                            f"fraction, the compressibilities, r<sub>V</sub> and the uplift. The <b>{T['report']}</b> "
                            "tab explains everything in detail, with tables and figures."),
        ("Keep your work", f"{_btn('Save')} stores everything in a project file (.mcu); {_btn('Export to Excel')} "
                           f"writes the results to a spreadsheet; {_btn('Save report')} writes the full report as a "
                           "web page you can open, print or send."),
    ]
    out.append(f'<h2><a name="start"></a>1. Quick start — your first calculation in five steps</h2>')
    out.append('<table width="100%" cellspacing="4" cellpadding="8">' + "".join(
        f'<tr><td class="step" width="44">{i + 1}</td><td class="box"><b>{t}</b><br>{d}</td></tr>'
        for i, (t, d) in enumerate(steps)) + "</table>")

    # ------------------------------------------------------------------ 2 the window
    out.append('<h2><a name="window"></a>2. The window: toolbar and tabs</h2><h3>Toolbar</h3>')
    out.append(_table(["Button", "What it does"], [
        [_btn("New (empty tables)"), "Clears all tables to describe a volcano of your own (Ctrl+N)."],
        [_btn("Examples ▾"), "Loads one of the ready-made volcanoes, compiled from published data."],
        [_btn("Open…") + " " + _btn("Save") + " " + _btn("Save as…"),
         "Opens or saves a project file (.mcu) with all tables and settings. Your last session also comes back "
         "automatically when you start the program again."],
        [_btn("▶ Run"), "Runs the whole calculation (F5)."],
        [_btn("Export to Excel…"), "Results, gas states, input tables and settings in one Excel workbook."],
        [_btn("Save report…"), "The complete report as a web page (HTML)."],
        [_btn("About"), "Version, author and credits."],
    ], widths=["32%", "68%"]))
    out.append("<h3>Tabs</h3>")
    out.append(_table(["Tab", "What you do there"], [
        "Inputs — what you type in",
        [f"<b>{T['magmas']}</b>", "Describe each magma: type, temperature, water and other volatiles, oxidation "
                                  "state and chemical composition. One column per magma."],
        [f"<b>{T['reservoirs']}</b>", "Describe each magma reservoir: shape, depth, volume, how much magma is "
                                      "injected, which magma fills it, and the stiffness of the surrounding rock. "
                                      "One row per reservoir."],
        [f"<b>{T['manual']}</b> <span class='small'>(optional)</span>",
         "Normally empty. Only if you want to replace EVo's gas calculation for a reservoir by your own numbers, "
         "e.g. from another model."],
        [f"<b>{T['settings']}</b>", "General values: crust density, default rock stiffness, distances at which the "
                                    "uplift is listed, EVo options and report options. The defaults are fine to "
                                    "start with."],
        "Outputs — what the program gives back",
        [f"<b>{T['results']}</b>", "The result table (main columns or all columns)."],
        [f"<b>{T['report']}</b>", "Everything in detail: input check, each calculation step, the full EVo output, "
                                  "uplift tables, detectability, figures. Can be saved or opened in your web browser."],
        [f"<b>{T['map']}</b>", "A map of the uplift around one reservoir. Choose the reservoir and press "
                               + _btn("Draw the map") + "."],
        [f"<b>{T['calc']}</b>", "Asks EVo about one magma at any pressure — handy to explore how much gas a "
                                "magma holds at a given depth. Press " + _btn("Calculate") + "."],
        [f"<b>{T['guide']}</b>", "This page."],
    ], widths=["26%", "74%"]))

    # ------------------------------------------------------------------ 3 tables
    out.append('<h2><a name="tables"></a>3. Working with the tables</h2><ul>'
               "<li><b>Edit</b> a cell by double-clicking it or simply by starting to type. Press Enter to confirm.</li>"
               "<li>Cells with a list of choices (e.g. <i>EVo solubility class</i>, <i>Shape</i>) open a drop-down list.</li>"
               "<li><b>Grey text</b> in an empty cell tells what the program uses when you leave it empty "
               "(<i>default</i> = the value in Settings).</li>"
               "<li>A <b>red cell</b> holds text that is not a number — correct it before running. Numbers can be "
               "written as <code>1e6</code>, <code>1.2e-10</code> or <code>5×10^6</code>.</li>"
               f"<li>{_btn('+ Add magma')} / {_btn('+ Add reservoir')} add an empty column or row. "
               f"{_btn('Copy …')} duplicates the magma or reservoir of the selected cell (a quick way to make a "
               f"variant), {_btn('Remove …')} deletes it.</li>"
               f"<li>{_btn('Show more rows')} / {_btn('Show optional columns')} reveal entries that are rarely needed.</li>"
               "<li><b>Excel:</b> select cells and press Ctrl+C / Ctrl+V to copy and paste blocks of cells, also "
               "between this program and Excel or Google Sheets. Delete empties the selected cells.</li>"
               f"<li><b>Undo</b> with Ctrl+Z or {_btn('↶ Undo')}, redo with Ctrl+Y.</li>"
               f"<li>{_btn('Text view…')} shows a whole table as text — to copy it into an e-mail or document, or to "
               "paste a complete table at once.</li>"
               "<li>If you rename a magma, the reservoirs that use it follow automatically.</li></ul>")

    # ------------------------------------------------------------------ 4 own volcano
    out.append('<h2><a name="own"></a>4. Your own volcano, step by step</h2>')
    own = [
        ("Start", f"Press {_btn('New (empty tables)')} — or, often easier, load the example whose magma is most "
                  "similar to yours and change its values."),
        (T["magmas"], "For each magma fill in at least the rows marked <span class='req'>●</span> in the reference "
                      "(section 9): a <b>name</b>, the <b>EVo solubility class</b> (basalt, phonolite or rhyolite — "
                      "choose by the SiO₂ content), <b>temperature</b>, <b>melt compressibility</b> (typically "
                      "1×10⁻¹⁰ Pa⁻¹) and <b>melt density</b>, the <b>H₂O</b> content (and CO₂ and S if known), the "
                      "<b>redox state</b> (e.g. FMQ and +1) and the <b>oxides</b> (at least SiO₂ and FeO)."),
        (T["reservoirs"], "For each reservoir give a <b>name</b>, the <b>shape</b> (section 5), the <b>depth</b> of "
                          "its centre in km, its <b>volume</b> V₀ in m³, one or more <b>injected volumes</b> Vₑ "
                          "(separated by ;) and the <b>resident</b> magma (a name from the Magmas tab). A penny-"
                          "shaped crack also needs its <b>radius</b>, a spheroid its <b>b/a</b> ratio."),
        (T["settings"], "Check the crust density (for the pressure), the default rock stiffness μ and ν, and the "
                        "distances (km) at which the uplift should be listed."),
        ("Run", f"Press {_btn('▶ Run')}. If something is missing or wrong, a message names the table, the "
                "magma or reservoir and the row or column, and the program opens that tab. Correct it and run again."),
        ("Save", f"{_btn('Save')} your project, then {_btn('Export to Excel…')} or {_btn('Save report…')}."),
    ]
    out.append('<table width="100%" cellspacing="4" cellpadding="8">' + "".join(
        f'<tr><td class="step" width="44">{chr(65 + i)}</td><td class="box"><b>{t}</b><br>{d}</td></tr>'
        for i, (t, d) in enumerate(own)) + "</table>")
    out.append('<table width="100%" cellpadding="8"><tr><td class="tip"><b>Tip.</b> To compare geometries, enter '
               "the same storage level several times with different shapes (as in the La Fossa example: the same "
               "depths as Mogi spheres and as penny-shaped cracks).</td></tr></table>")

    # ------------------------------------------------------------------ 5 shapes
    out.append('<h2><a name="shapes"></a>5. Choosing a reservoir shape</h2>')
    out.append(_table(["Shape", "Picture", "Use it when…", "Needs"], [
        ["<b>mogi</b>", "point-like sphere", "the reservoir is small compared with its depth; the classic first "
                                             "choice (Mogi 1958)", "depth, volume"],
        ["<b>sphere</b>", "sphere of finite size", "the reservoir is large compared with its depth "
                                                   "(McTigue 1987; radius/depth up to about 0.5)",
         "depth, volume (radius optional)"],
        ["<b>spheroid</b>", "elongated, cigar-like body", "the reservoir is elongated or inclined, e.g. a feeder "
                                                          "zone (Yang et al. 1988)", "depth, volume, b/a, dip, azimuth"],
        ["<b>penny</b>", "flat horizontal crack (sill)", "the magma is stored in a thin horizontal sheet "
                                                         "(Fialko et al. 2001)", "depth, volume, radius"],
    ], widths=["12%", "22%", "44%", "22%"]))

    # ------------------------------------------------------------------ 6 EVo modes
    out.append('<h2><a name="modes"></a>6. How to describe the volatiles (EVo modes)</h2>'
               "<p>The row <b>EVo mode</b> of the Magmas tab tells EVo what you know about the gas. If you are unsure, "
               "leave it empty: <i>saturation</i> is used, as in the thesis.</p>")
    out.append(_table(["EVo mode", "You know…", "Fill in"], [
        ["<b>saturation</b> (default)", "the <b>total</b> water, CO₂ and sulfur content of the magma, e.g. from melt "
                                        "inclusions", "H₂O (and CO₂, S, N or graphite) in wt%, and the redox state"],
        ["<b>atomic</b>", "the total <b>amount of each element</b> (H, C, S, N) in magma + gas",
         "Total H (and C, S, N) in ppm, and the redox state <span class='small'>(Show more rows)</span>"],
        ["<b>gas_at_P</b>", "how much <b>gas</b> is present at a certain pressure and its composition (fugacities)",
         "vapour mass fraction and, for the usual C–O–H–S gas, exactly 3 of: redox, fH₂, H₂O (as wt% or fH₂O), "
         "CO₂ (as wt% or fCO₂), S <span class='small'>(Show more rows)</span>"],
    ], widths=["18%", "40%", "42%"]))
    out.append("<p class='small'>Rules checked by the program: gas fugacities only in gas_at_P mode; H₂O and CO₂ each "
               "only once (as wt% or as fugacity); either a redox reference or the FeO/Fe₂O₃ split (redox reference = "
               "iron), not both. An absolute fO₂ in saturation or atomic mode is converted to the equivalent ΔFMQ, "
               "and the report says so.</p>")

    # ------------------------------------------------------------------ 7 results
    out.append('<h2><a name="results"></a>7. Reading the results</h2>')
    out.append(_table(["Column", "Meaning"], [
        ["<b>P_MPa</b>", "Pressure in the reservoir (MPa), from its depth: P = ρ·g·z."],
        ["<b>saturated</b>, <b>P_sat_MPa</b>", "Whether the magma holds gas bubbles at that pressure, and the pressure "
                                              "below which bubbles appear."],
        ["<b>phi</b>", "Gas (vapour) volume fraction, from 0 to 1."],
        ["<b>beta_m</b>, <b>beta_c</b>", "Compressibility of the magma and of the reservoir (Pa⁻¹): how easily each "
                                         "is squeezed."],
        ["<b>rV</b>", "Partitioning factor r<sub>V</sub> = 1 + β<sub>m</sub>/β<sub>c</sub>. "
                      "r<sub>V</sub> = 1: all injected magma lifts the ground. r<sub>V</sub> = 5: only one fifth does; "
                      "the rest is absorbed by compressing the magma already there."],
        ["<b>Ve…_m3</b>, <b>dVc…_m3</b>", "Injected volume, and the volume change of the reservoir "
                                          "ΔV<sub>c</sub> = V<sub>e</sub>/r<sub>V</sub> (m³)."],
        ["<b>uz…_mm</b>", "Uplift of the ground surface in mm, e.g. <i>uz1_0km_mm</i> = uplift for the first injected "
                          "volume, right above the reservoir (0 km); <i>uz1_2km_mm</i> = 2 km away."],
    ], widths=["24%", "76%"]))
    out.append("<p>The <b>Report</b> repeats these numbers with explanations, shows the full EVo output for every "
               "magma state, gives the injected volume needed to produce a detectable uplift, and draws the figures.</p>")

    # ------------------------------------------------------------------ 8 chain
    out.append('<h2><a name="chain"></a>8. What the program calculates</h2>')
    out.append(_table(["Step", "Quantity", "How it is calculated"], [
        ["1", "Pressure P", "P = ρ<sub>c</sub>·g·z, or given for a reservoir"],
        ["2", "Gas fraction φ, saturation pressure, gas composition, fugacities",
         "<b>EVo</b> (C–O–H–S–N equilibrium between melt and gas)"],
        ["3", "Magma compressibility β<sub>m</sub>",
         "β<sub>m</sub> = φ·β<sub>gas</sub> + (1 − φ)·β<sub>liquid</sub>, with β<sub>gas</sub> = 1/P"],
        ["4", "Reservoir compressibility β<sub>c</sub>", "sphere 3/(4μ); prolate spheroid (Amoruso &amp; Crescentini "
                                                       "2009); penny crack (Fialko et al. 2001); or given"],
        ["5", "Partitioning factor r<sub>V</sub>", "r<sub>V</sub> = 1 + β<sub>m</sub>/β<sub>c</sub>"],
        ["6", "Reservoir volume change ΔV<sub>c</sub>", "ΔV<sub>c</sub> = V<sub>e</sub>/r<sub>V</sub>"],
        ["7", "Surface uplift", "Mogi (1958) point sphere, McTigue (1987) finite sphere, Yang et al. (1988) "
                                "spheroid, Fialko et al. (2001) crack"],
    ], widths=["8%", "37%", "55%"]))

    # ------------------------------------------------------------------ 9 reference
    out.append('<h2><a name="ref"></a>9. Reference: every row and column of the tables</h2>'
               "<p><span class='req'>●</span> = needed. <i>(Show more)</i> = hidden until you tick "
               f"{_btn('Show more rows')} / {_btn('Show optional columns')}. The short key in grey is the name used in "
               "the text view, in Excel exports and in error messages.</p>")
    out.append(f"<h3>{T['magmas']} tab — one column per magma</h3>")
    out.append(_table(["Row", "Key", "Meaning"],
                      _field_rows(mag, "magmas", [f"Magma name <span class='req'>●</span>", '<td class="k">—</td>',
                                        "Any name, e.g. BASALT_1; used in the Reservoirs tab."]),
                      widths=["30%", "16%", "54%"]))
    out.append("<p class='small'>Expert: " + _btn("+ Add EVo setting row") + " adds a row for any EVo option (e.g. "
               "H2_MODEL, SULFIDE_CAPACITY, DP_MAX) that should differ for one magma from the EVo options in Settings.</p>")
    out.append(f"<h3>{T['reservoirs']} tab — one row per reservoir</h3>")
    out.append(_table(["Column", "Key", "Meaning"], _field_rows(res, "reservoirs"), widths=["30%", "16%", "54%"]))
    out.append(f"<h3>{T['manual']} tab (optional)</h3><p>Leave it empty to let EVo compute every reservoir. A row "
               "replaces EVo for the resident magma of one reservoir; only the vapour fraction φ is used in the "
               "calculation, the other columns are reported next to it.</p>")
    out.append(_table(["Column", "Key", "Meaning"], _field_rows(s2, "step2"), widths=["30%", "16%", "54%"]))

    # ------------------------------------------------------------------ 10 help
    out.append('<h2><a name="help"></a>10. Problems and questions</h2>')
    out.append(_table(["Situation", "What to do"], [
        ["A message <b>“Please correct the input”</b> appears",
         "It names the table, the magma or reservoir and the row or column, and the program opens that tab. Correct "
         "the value and press ▶ Run again."],
        ["The report says <b>“EVo could not run”</b> for a magma",
         "EVo found no solution for these inputs (e.g. too much gas or an unusual redox state). The program then uses "
         "a simple analytical model for that magma and marks it. Check the volatile contents and the redox state."],
        ["The calculation takes long", "Magmas rich in CO₂ need long decompression paths in EVo (Kīlauea: about one "
                                       "minute). Wait until the bar at the bottom disappears."],
        ["My values are gone", "Use Save / Open for projects. Your last session is restored automatically when you "
                               "start the program."],
        ["Is the program calculating correctly?",
         "Start <code>MagmaUplift.exe --selftest</code> from a command prompt: it repeats the thesis example and "
         "compares every number with the verified notebook; <code>--check-all</code> does the same for all volcanoes."],
    ], widths=["30%", "70%"]))

    # ------------------------------------------------------------------ 11 credits
    out.append('<h2><a name="credits"></a>11. Methods, assumptions and references</h2><ul>'
               "<li><b>EVo</b> — thermodynamic degassing model: Liggins, P., Shorttle, O. &amp; Rimmer, P. B. (2020), "
               "<i>Earth Planet. Sci. Lett.</i> 550, 116546; Liggins, P. et al. (2022), <i>J. Geophys. Res. Planets</i> "
               "127, e2021JE007123. Version 1.1.0, github.com/pipliggins/EVo, GPL-3.0.</li>"
               "<li><b>dMODELS</b> — Battaglia, M., Cervelli, P. F. &amp; Murray, J. R. (2013), <i>J. Volcanol. "
               "Geotherm. Res.</i> 254, 1–4; Python port dmodelspy 0.2 (W. Crawford), GPL-3.0.</li>"
               "<li><b>Deformation sources:</b> Mogi (1958); McTigue (1987, <i>JGR</i> 92); Yang et al. (1988, "
               "<i>JGR</i> 93) with Newman et al. (2006); Fialko et al. (2001, <i>GJI</i> 146).</li>"
               "<li><b>Compressibility framework:</b> Rivalta &amp; Segall (2008, <i>GRL</i> 35, L04306); Kilbride et "
               "al. (2016, <i>Nat. Commun.</i> 7, 13744); Segall (2010); Amoruso &amp; Crescentini (2009, <i>JGR</i> "
               "114, B02210).</li>"
               "<li><b>Solubility and redox models in EVo:</b> Burgisser et al. (2015); Gaillard et al. (2003); Eguchi "
               "&amp; Dasgupta (2018); Kress &amp; Carmichael (1991); Righter et al. (2013); Frost (1991); O'Neill "
               "(2002, 2020); Nash et al. (2019); Liu et al. (2007); Libourel et al. (2003); Spera (2000).</li>"
               "<li><b>La Fossa example:</b> Gioncada et al. (1998); Clocchiatti et al. (1994); Fusillo et al. (2015); "
               "Paonita et al. (2013); Di Traglia et al. (2023, <i>GRL</i> 50, e2023GL104952); Heap et al. (2020). "
               "The sources of the Etna, Campi Flegrei and Kīlauea values are listed in the Report (input check).</li>"
               "</ul><p><b>Assumptions.</b> Homogeneous, isotropic elastic half-space with a flat surface; static "
               "end-state displacements; ideal-gas β<sub>gas</sub> = 1/P with the gas composition frozen during "
               "pressurisation (EVo's equilibrium β<sub>m</sub> is reported as an upper bound); the spheroid "
               "compliance is a full-space expression, the crack compliance a half-space one; each reservoir is "
               "treated on its own.</p>")
    return "".join(out)

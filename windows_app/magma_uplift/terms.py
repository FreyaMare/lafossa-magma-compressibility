"""Words of the notebook → words of the window.

The calculation code comes from the notebook, whose texts point to notebook cells ("cell 5", "cells 4 and 7").
In the program those places are tabs, so every text shown in the window passes through app_text()."""
import re

TAB = {
    "magmas": "Magmas", "reservoirs": "Reservoirs", "manual": "Manual EVo values", "settings": "Settings",
    "results": "Results", "report": "Report", "map": "Uplift map", "calc": "EVo calculator", "guide": "User guide",
}

# notebook cell → where it lives in the program
CELL_PLACE = {1: "start-up", 2: "EVo", 3: "dMODELS", 4: TAB["settings"], 5: TAB["magmas"], 6: TAB["reservoirs"],
              7: TAB["settings"], 8: TAB["manual"], 9: "calculation engine", 10: TAB["report"], 11: TAB["report"],
              12: TAB["report"], 13: TAB["report"], 14: TAB["settings"], 15: TAB["report"], 16: TAB["map"],
              17: TAB["calc"], 18: TAB["report"]}
TABS = {TAB[k] for k in ("magmas", "reservoirs", "manual", "settings", "report", "map", "calc")}

# section titles of the program (the notebook's cell titles carry cell numbers and notebook wording)
TITLES = {
    4: "Project, crust and observation points",
    7: "EVo options shared by all magmas",
    10: "Input check — every magma and reservoir as it will be calculated",
    11: "Steps 1–6 — pressure, vapour fraction, compressibilities and volume partitioning",
    12: "Step 2 in detail — complete EVo input and output",
    13: "Step 7 — surface uplift for every injected volume",
    14: "Detectability — volume needed for a target uplift, and validity checks",
    15: "Figures and the complete results table",
    16: "Uplift map of one reservoir",
    17: "EVo calculator — one magma at any pressure",
    18: "Benchmark — the deformation code checked against a published inversion",
}

_SPECIAL = [
    (r"click cell 9 and\s+choose <i>Runtime ▸ Run after</i>", "press <b>▶ Run</b> (F5)"),
    (r"change the tables \(cells 5, 6, 8\) or the settings \(cells 4, 7, 14\)", "change the input tables or the Settings"),
    (r"(?:are )?listed in the guide above cell 5", "are listed in the User guide"),
    (r"the guide above cell 5", "the User guide"),
    (r"after the defaults of cells 4 and 7 are filled in", "after the defaults of the Settings tab are filled in"),
    (r"\(definitions in cell 12\)", "(definitions in the Report, section “Step 2 in detail”)"),
    (r"is in cell 12", "is in the Report, section “Step 2 in detail”"),
    (r"<code>WgT</code> of cell 7", "<code>WgT</code> (Settings, EVo options)"),
    (r"(?:the )?shared settings of cell 7", "the shared EVo options in Settings"),
    (r"EVo \(cell 2; ", "EVo ("),
    (r"EVo \(cell 2\)", "EVo"),
    (r"dMODELS sources \(cell 3\)", "dMODELS sources"),
    (r"\(embedded, cell 2\)|\(embedded dMODELS, cell 3\)", ""),
    (r"[Ee]mpty = cell 4", "empty = default in Settings"),
    (r"[Ee]mpty = cell 7", "empty = default in Settings"),
    (r"[Ee]mpty = cell 5", "empty = the magma's temperature"),
    (r"\bmanual \(cell 8\)", "manual values"),
    (r"\bthis notebook\b", "this program"),
    (r"\bThis notebook\b", "This program"),
    (r"\bthe notebook\b", "the program"),
    (r"\bThe notebook\b", "The program"),
    (r"\bNotebook wrapper\b", "Program settings"),
]
_CELLS = re.compile(r"(\()?\b[Cc]ells? (\d+)((?:(?:, | and |, and )\d+)*)(\))?")


def _names(nums):
    out = []
    for n in nums:
        p = CELL_PLACE.get(n, f"cell {n}")
        if p not in out:
            out.append(p)
    return out


def _cells(m):
    nums = [int(m.group(2))] + [int(x) for x in re.findall(r"\d+", m.group(3) or "")]
    names = _names(nums)
    tab = all(n in TABS for n in names)
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    if m.group(1) and m.group(4):                       # "(cell 5)" → "(Magmas tab)"
        return f"({joined}{' tab' if tab and len(names) == 1 else ' tabs' if tab else ''})"
    phrase = (f"the {joined} tab" if len(names) == 1 else f"the {joined} tabs") if tab else joined
    return (m.group(1) or "") + phrase + (m.group(4) or "")


def app_text(s):
    """Replaces the notebook's references to cells by the names of the program's tabs."""
    if not s or "ell" not in s and "otebook" not in s:
        return s
    for pat, rep in _SPECIAL:
        s = re.sub(pat, rep, s)
    return _CELLS.sub(_cells, s)


def hint_text(s):
    """Grey hints inside empty table cells: short words."""
    return {"cell 4": "default", "cell 7": "default", "cell 5": "magma T"}.get(s, app_text(s))

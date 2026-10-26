"""Runs the code cells of the notebook outside Jupyter.

The calculation is exactly the notebook's: the cells are executed verbatim (magma_uplift/nbcells.py)
in one Python namespace, as a Jupyter kernel would. Only three things are supplied from outside:
  * the form fields (#@param lines) take the values of the Settings tab,
  * the fill-in tables of cells 5, 6 and 8 come from the tables of the window,
  * everything a cell displays (HTML and figures) is collected into a report instead of a notebook page.
"""
import base64
import html
import io
import re
import sys
import time
import traceback
import types

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import nbcells  # noqa: E402

PARAM_RE = re.compile(r"^(?P<name>\w+)\s*=\s*(?P<value>.+?)\s*#@param\s*(?P<spec>.*)$")

# cells of the notebook and their role in the app
SETUP_CELLS = (1, 2, 3)                 # once, when the program starts
INPUT_CELLS = (4, 5, 6, 7, 8, 9)        # settings, tables (taken from the window), engine
REPORT_CELLS = (10, 11, 12, 13, 14, 15, 16, 17, 18)
MAP_CELL, CALC_CELL = 16, 17


# ----------------------------------------------------------------------------- output capture
class _Sink:
    def __init__(self):
        self.parts = []


_sink = _Sink()


class HTML:
    """Stand-in for IPython.display.HTML."""
    def __init__(self, data=None, **_):
        self.data = data or ""

    def _repr_html_(self):
        return self.data


def display(*objs, **_):
    """Stand-in for IPython.display.display: keeps the HTML of every object."""
    for o in objs:
        if hasattr(o, "_repr_html_"):
            h = o._repr_html_()
        elif hasattr(o, "to_html"):
            h = o.to_html()
        else:
            h = f"<pre>{html.escape(str(o))}</pre>"
        _sink.parts.append(h or "")


def _show_figures(*_, **__):
    """Stand-in for plt.show(): every open figure becomes a PNG in the report."""
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", facecolor="white")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        _sink.parts.append(f'<div class="lffig"><img src="data:image/png;base64,{b64}"></div>')
    plt.close("all")


def _install_display_module():
    ipy = types.ModuleType("IPython")
    disp = types.ModuleType("IPython.display")
    disp.display, disp.HTML = display, HTML
    ipy.display = disp
    ipy.get_ipython = lambda: None              # matplotlib asks for it
    ipy.version_info = (0, 0, 0)
    sys.modules["IPython"], sys.modules["IPython.display"] = ipy, disp
    sys.modules["ipywidgets"] = None          # the window has its own tables
    plt.show = _show_figures


# ----------------------------------------------------------------------------- tables from the window
class _Grid:
    """What cells 10 and later read from a fill-in table."""
    def __init__(self, key):
        self.key, self.table, self.synced_choice, self.edited = key, (["property"], []), None, False

    def as_table(self):
        return self.table

    def names(self):
        return []

    def show(self):
        pass


class _TableStub:
    """Replaces the ipywidgets tables of cells 5, 6 and 8: records their field lists and hands out the
    tables of the window."""
    specs, grids = {}, {}

    @classmethod
    def open(cls, key, fields, orient, item, start, loader, **kw):
        cls.specs[key] = dict(fields=fields, orient=orient, item=item, options=kw)
        return cls.grids.setdefault(key, _Grid(key))

    @staticmethod
    def start_all(choice):
        pass


# ----------------------------------------------------------------------------- form fields
def params_of(cell):
    """Form fields of a cell: list of dicts name, default, kind, options, description."""
    out, desc = [], []
    for line in nbcells.CELLS[cell].splitlines():
        if line.startswith("#@markdown"):
            desc.append(line[len("#@markdown"):].strip())
            continue
        m = PARAM_RE.match(line)
        if not m:
            continue
        spec, value = m.group("spec").strip(), eval(m.group("value"), {})
        if spec.startswith("["):
            kind, options = "choice", eval(spec, {})
        else:
            t = re.search(r'type:\s*"(\w+)"', spec)
            kind, options = (t.group(1) if t else "string"), None
        out.append(dict(name=m.group("name"), default=value, kind=kind, options=options,
                        description="\n".join(desc)))
        desc = []
    return out


def _with_params(src, values):
    def repl(line):
        m = PARAM_RE.match(line)
        if m and m.group("name") in values:
            v = values[m.group("name")]
            return f"{m.group('name')} = {v!r}  #@param {m.group('spec')}"
        return line
    return "\n".join(repl(line) for line in src.split("\n"))


# ----------------------------------------------------------------------------- runner
class CellError(Exception):
    def __init__(self, cell, message, input_error):
        super().__init__(message)
        self.cell, self.input_error = cell, input_error


class Notebook:
    """One namespace in which the cells run, like a Jupyter kernel."""

    def __init__(self):
        _install_display_module()
        self.ns = {"__name__": "__notebook__"}
        self.ready = False
        self.outputs = {}            # cell -> list of HTML parts of its last run
        self.css = ""

    # ------------------------------------------------------------------ helpers
    def _exec(self, cell, values=None):
        src = nbcells.CELLS[cell]
        if values:
            src = _with_params(src, values)
        _sink.parts = []
        try:
            exec(compile(src, f"<cell {cell}>", "exec"), self.ns)
        except BaseException as e:      # EVo stops with SystemExit subclasses
            plt.close("all")
            self.outputs[cell] = list(_sink.parts)
            input_error = type(e).__name__ == "InputError"
            msg = str(e) if input_error else "".join(traceback.format_exception_only(type(e), e)).strip()
            if not input_error:
                msg += "\n\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__)[-6:])
            raise CellError(cell, msg, input_error) from None
        self.outputs[cell] = list(_sink.parts)

    def setup(self, progress=None):
        """Cells 1–3: display tools, EVo and dMODELS (a few seconds)."""
        for c in SETUP_CELLS:
            if progress:
                progress(c, nbcells.TITLES[c])
            self._exec(c)
        self.css = self.ns["_CSS"]
        self.ns["TableEditor"] = _TableStub
        self._exec(4)                                # field lists and the ready-made volcanoes
        for c in (5, 6, 8):
            self._exec(c)
        self.examples = self.ns["EXAMPLES"]
        self.specs = _TableStub.specs
        self.labels = dict(empty=self.ns["EMPTY_TABLES"], saved=self.ns["SAVED_COPY"])
        self.ready = True

    def split_text(self, text):
        return self.ns["split_table_text"](text)

    # ------------------------------------------------------------------ runs
    def run(self, tables, settings, start_from, edited, cells=None, progress=None):
        """tables = {'magmas': (header, rows), 'reservoirs': …, 'step2': …};
        settings = {param name: value}. Runs the input cells and then `cells` (default: the report)."""
        for key, tab in tables.items():
            g = _TableStub.grids.setdefault(key, _Grid(key))
            g.table, g.synced_choice, g.edited = tab, start_from, edited
        values = dict(settings, START_FROM=start_from)
        self.ns["TableEditor"] = _TableStub
        t0 = time.time()
        for c in INPUT_CELLS + tuple(cells if cells is not None else REPORT_CELLS):
            if progress:
                progress(c, nbcells.TITLES[c])
            self._exec(c, values)
        return time.time() - t0

    def run_cell(self, cell, settings):
        self._exec(cell, settings)
        return self.outputs[cell]

    # ------------------------------------------------------------------ report
    def report_html(self, cells=REPORT_CELLS, title="Report", for_qt=False):
        parts = []
        for c in cells:
            if c not in self.outputs:
                continue
            parts.append(f'<h2 class="cellhead">{c}. {html.escape(nbcells.TITLES[c])}</h2>')
            parts += [p.replace(self.css, "") for p in self.outputs[c]]
        css = QT_CSS if for_qt else self.css.replace("<style>", "<style>\nbody{margin:18px;background:#fff}"
                                                     "\nh2.cellhead{font-family:Arial,sans-serif;color:#1F4E79;"
                                                     "border-bottom:2px solid #1F4E79;margin-top:28px}\n"
                                                     ".lffig img{max-width:100%}")
        return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>{css}</head>"
                f"<body>{''.join(parts)}</body></html>")


# A simplified style sheet for the report view inside the window (Qt understands only part of CSS);
# the saved / browser report keeps the full notebook styles.
QT_CSS = """<style>
body{font-family:Arial,Helvetica,sans-serif;font-size:10pt;color:#111}
h2.cellhead{color:#1F4E79;font-size:13pt;margin-top:18px}
.lfh{font-size:12pt;font-weight:bold;color:#ffffff;background-color:#1F4E79;padding:4px}
.lft{font-size:10.5pt;font-weight:bold;color:#1F4E79;margin-top:8px}
.lfc{font-size:9pt;color:#444444}
table.lf{border-collapse:collapse;font-size:9pt}
table.lf th{background-color:#2E5D8A;color:#ffffff;padding:3px;border:1px solid #9fb3c8}
table.lf td{padding:3px;border:1px solid #cdd6e0}
td.grp{background-color:#dfe8f2;font-weight:bold;color:#1F4E79}
td.bad{background-color:#fde3e1;color:#8a1c1c;font-weight:bold}
td.good{background-color:#e4f5e7;color:#15521f}
td.hi{background-color:#fff4d6;font-weight:bold}
td.dim{color:#888888}
.lfb{background-color:#eef4fb;padding:6px;margin:4px 0}
.warn{background-color:#fdf0ef}
.ok{background-color:#edf8f1}
</style>"""

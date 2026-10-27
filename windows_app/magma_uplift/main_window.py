"""Main window of the desktop program."""
import html
import json
import os
import re
import tempfile
import time
import traceback

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt, QThread, Signal, QAbstractTableModel, QModelIndex, QUrl, QStandardPaths, QSize
from PySide6.QtGui import QAction, QKeySequence, QDesktopServices, QIcon, QFont
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
                               QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton, QScrollArea, QTextBrowser,
                               QTableView, QFileDialog, QMessageBox, QProgressBar, QToolButton, QMenu, QHeaderView,
                               QSpinBox, QDialog, QDialogButtonBox, QSizePolicy, QApplication)

from . import nbcells, __version__
from .runner import params_of, CellError, REPORT_CELLS, MAP_CELL, CALC_CELL
from .table_editor import TableEditor
from .terms import TAB, TITLES, app_text, hint_text
from .guide import guide_html
from .about import AboutDialog
import copy

SETTINGS_CELLS = (4, 7, 12, 14, 18)
TABLE_KEYS = ("magmas", "reservoirs", "step2")
PROJECT_FILTER = "Magma uplift project (*.mcu);;All files (*)"

LABELS = {
    "PROJECT_NAME": "Project name", "rho_crust": "Crustal density ρ (kg m⁻³)", "g": "Gravity g (m s⁻²)",
    "default_mu_GPa": "Default shear modulus μ (GPa)", "default_nu": "Default Poisson ratio ν",
    "obs_distances_km": "Observation distances (km)", "profile_azimuth": "Profile azimuth (° from North)",
    "profile_max_km": "Profile length (km; 0 = automatic)", "step2_engine": "Engine for step 2",
    "RUN_TYPE": "Run type", "default_gas_system": "Default gas system", "FE_SYSTEM": "Iron redox system (FE_SYSTEM)",
    "S_SAT_WARN": "Warn at sulfide saturation (S_SAT_WARN)", "default_fO2_buffer": "Default redox reference",
    "default_fO2_value": "Default redox value", "P_START": "P_START (bar)", "DP_MIN": "DP_MIN (bar)",
    "DP_MAX": "DP_MAX (bar)", "MASS": "MASS (g)", "WgT": "WgT (trace vapour fraction)", "LOSS_FRAC": "LOSS_FRAC",
    "H2O_floor_ppm": "H₂O floor (ppm)", "CO2_floor_ppm": "CO₂ floor (ppm)", "S_floor_ppm": "S floor (ppm)",
    "P_STOP_integer_bar": "Round P_STOP to a whole bar", "P_STOP_retry_bumps_bar": "P_STOP retry offsets (bar)",
    "show_decompression_paths": "Show the full decompression paths", "show_evo_messages": "Show EVo's messages",
    "target_uplift_mm": "Target uplift (mm)", "max_admissible_dP_MPa": "Maximum admissible overpressure (MPa)",
    "run_benchmark": "Run the benchmark",
    "MAP_reservoir": "Reservoir", "MAP_volume_index": "Injected volume (1 = V1, …; 0 = the largest)",
    "MAP_half_width_km": "Half-width of the map (km; 0 = automatic)",
    "CALC_magma": "Magma", "CALC_P_MPa": "Pressure (MPa)", "CALC_change_T": "Change the temperature",
    "CALC_T_C": "Temperature (°C)", "CALC_change_volatiles": "Change the volatile contents",
    "CALC_H2O_wt": "H₂O (wt%)", "CALC_CO2_wt": "CO₂ (wt%)", "CALC_S_wt": "S (wt%)",
    "CALC_change_redox": "Change the redox state", "CALC_fO2_buffer": "Redox reference", "CALC_fO2_value": "Redox value",
}


def md_inline(s):
    """The little markdown of the notebook's form descriptions → HTML."""
    paras = [" ".join(x.split()) for x in re.split(r"\n\s*---\s*", "\n" + s.strip()) if x.strip()]
    s = "<br>".join(html.escape(x) for x in paras)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    return s


# ============================================================================= settings forms
class ParamForm(QWidget):
    """The form fields (#@param) of notebook cells as a form."""
    changed = Signal()

    def __init__(self, cells, skip=(), combos=None, parent=None):
        super().__init__(parent)
        self.widgets, self.kinds = {}, {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        combos = combos or {}
        for cell in cells:
            box = QGroupBox(TITLES.get(cell, nbcells.TITLES[cell]))
            box.setStyleSheet("QGroupBox{font-weight:bold;color:#1F4E79;margin-top:10px}"
                              "QGroupBox::title{subcontrol-origin:margin;left:8px}")
            form = QFormLayout(box)
            form.setLabelAlignment(Qt.AlignRight)
            for p in params_of(cell):
                if p["name"] in skip:
                    continue
                if p["description"]:
                    d = QLabel(md_inline(app_text(p["description"])))
                    d.setWordWrap(True)
                    d.setStyleSheet("color:#333;font-weight:normal;margin-top:6px")
                    form.addRow(d)
                w = self._widget(p, combos.get(p["name"]))
                lab = QLabel(LABELS.get(p["name"], p["name"]))
                lab.setStyleSheet("font-weight:normal;color:#111")
                lab.setToolTip(p["name"])
                form.addRow(lab, w)
            lay.addWidget(box)
        lay.addStretch(1)

    def _widget(self, p, combo_source):
        name, kind, v = p["name"], p["kind"], p["default"]
        self.kinds[name] = kind
        if kind == "boolean":
            w = QCheckBox()
            w.setChecked(bool(v))
            w.toggled.connect(self.changed)
        elif kind == "choice":
            w = QComboBox()
            for o in p["options"]:
                w.addItem(app_text(str(o)), str(o))          # shown text / value used by the calculation
            w.setCurrentIndex(max(w.findData(str(v)), 0))
            w.currentIndexChanged.connect(self.changed)
        elif combo_source is not None:
            w = QComboBox()
            w.setEditable(True)
            w.setProperty("source", combo_source)
            w.setEditText(str(v))
            w.lineEdit().setPlaceholderText("empty = the first one")
            w.currentTextChanged.connect(self.changed)
        else:
            w = QLineEdit(str(v) if v is not None else "")
            w.setMaximumWidth(420)
            w.textChanged.connect(self.changed)
        self.widgets[name] = w
        return w

    def refresh_combos(self, sources):
        for name, w in self.widgets.items():
            src = w.property("source") if isinstance(w, QComboBox) else None
            if src:
                cur = w.currentText()
                w.blockSignals(True)
                w.clear()
                w.addItems([""] + sources.get(src, []))
                w.setEditText(cur)
                w.blockSignals(False)

    def values(self):
        """Typed values; raises ValueError naming the field when a number is not a number."""
        out = {}
        for name, w in self.widgets.items():
            kind = self.kinds[name]
            if kind == "boolean":
                out[name] = w.isChecked()
            elif isinstance(w, QComboBox):
                out[name] = w.currentText() if w.isEditable() else w.currentData()
            else:
                t = w.text().strip()
                if kind in ("number", "integer"):
                    try:
                        out[name] = int(float(t)) if kind == "integer" else float(t)
                    except ValueError:
                        raise ValueError(f"“{LABELS.get(name, name)}” must be a number (now: '{t}').") from None
                else:
                    out[name] = t
        return out

    def set_values(self, vals):
        for name, v in vals.items():
            w = self.widgets.get(name)
            if w is None:
                continue
            w.blockSignals(True)
            if isinstance(w, QCheckBox):
                w.setChecked(bool(v))
            elif isinstance(w, QComboBox):
                if w.isEditable():
                    w.setEditText(str(v))
                elif w.findData(str(v)) >= 0:
                    w.setCurrentIndex(w.findData(str(v)))
            else:
                w.setText(f"{v:g}" if isinstance(v, float) else str(v))
            w.blockSignals(False)


# ============================================================================= results table
class FrameModel(QAbstractTableModel):
    def __init__(self, df=None):
        super().__init__()
        self.df = df if df is not None else pd.DataFrame()

    def set(self, df):
        self.beginResetModel()
        self.df = df
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.df)

    def columnCount(self, parent=QModelIndex()):
        return len(self.df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role not in (Qt.DisplayRole, Qt.TextAlignmentRole):
            return None
        v = self.df.iat[index.row(), index.column()]
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignRight | Qt.AlignVCenter) if isinstance(v, (float, int, np.floating, np.integer)) \
                and not isinstance(v, (bool, np.bool_)) else int(Qt.AlignLeft | Qt.AlignVCenter)
        if isinstance(v, (bool, np.bool_)):
            return "yes" if v else "no"
        if isinstance(v, (float, np.floating)):
            if not np.isfinite(v):
                return "—"
            a = abs(v)
            return "0" if v == 0 else (f"{v:.5g}" if 1e-3 <= a < 1e6 else f"{v:.4e}")
        return str(v)

    def headerData(self, s, orient, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        return str(self.df.columns[s]) if orient == Qt.Horizontal else str(s + 1)


# ============================================================================= background work
class Worker(QThread):
    progress = Signal(int, str)
    done = Signal(object)
    failed = Signal(object)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        try:
            self.done.emit(self.fn(lambda c, t: self.progress.emit(c, t)))
        except Exception as e:                              # noqa: BLE001
            self.failed.emit(e)


# ============================================================================= main window
class MainWindow(QMainWindow):
    def __init__(self, nb, icon=None):
        super().__init__()
        self.nb = nb
        self.path, self.start_from, self.edited = None, None, False
        self.dirty_since_run, self.worker = True, None
        self.setWindowIcon(icon or QIcon())
        self.resize(1360, 860)

        # ------------------------------------------------ tables
        self.editors = {k: TableEditor(k, _app_spec(nb.specs[k]), nb.split_text) for k in TABLE_KEYS}
        mag, res, s2 = (self.editors[k] for k in TABLE_KEYS)
        res.ref_sources["magmas"] = mag.names
        s2.ref_sources["reservoirs"] = res.names
        mag.renamed.connect(lambda o, n: res.rename_ref("magmas", o, n))
        res.renamed.connect(lambda o, n: s2.rename_ref("reservoirs", o, n))
        for ed in self.editors.values():
            ed.changed.connect(self._tables_changed)

        # ------------------------------------------------ settings, map, calculator
        self.settings = ParamForm(SETTINGS_CELLS, skip=("START_FROM",))
        self.settings.changed.connect(self._mark_dirty)
        self.map_form = ParamForm((MAP_CELL,), combos={"MAP_reservoir": "reservoirs"})
        self.calc_form = ParamForm((CALC_CELL,), combos={"CALC_magma": "magmas"})

        # ------------------------------------------------ tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._wrap(mag, "Magmas", "One column per magma: type, temperature, volatiles, redox state "
                                    "and composition. An empty cell means “not given” — the grey text shows what is "
                                    "used instead. Every row is explained in the User guide."), TAB["magmas"])
        self.tabs.addTab(self._wrap(res, "Magma reservoirs", "One row per reservoir, or per geometry you want to "
                                    "compare: shape, depth, volume, injected volumes, the magma that fills it and the "
                                    "stiffness of the host rock."), TAB["reservoirs"])
        self.tabs.addTab(self._wrap(s2, "Manual EVo values (optional)", "Normally empty: EVo then computes the gas "
                                    "content of every reservoir. Add a row only to replace EVo's result for one "
                                    "reservoir with your own values (only the vapour fraction φ enters the "
                                    "calculation)."), TAB["manual"])
        self.tabs.addTab(self._scroll(self.settings), TAB["settings"])
        self.tabs.addTab(self._results_tab(), TAB["results"])
        self.tabs.addTab(self._report_tab(), TAB["report"])
        self.tabs.addTab(self._cell_tab(self.map_form, "Draw the map", self.draw_map), TAB["map"])
        self.tabs.addTab(self._cell_tab(self.calc_form, "Calculate", self.calculate), TAB["calc"])
        self.tabs.addTab(self._guide_tab(), TAB["guide"])
        for i, tip in enumerate(["Input: the magmas", "Input: the magma reservoirs",
                                 "Input (optional): your own values instead of EVo's gas calculation",
                                 "Input: general settings and EVo options", "Output: the result table",
                                 "Output: the full report with figures", "Output: uplift map of one reservoir",
                                 "Tool: EVo for one magma at any pressure", "How to use the program"]):
            self.tabs.setTabToolTip(i, tip)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.setCentralWidget(self.tabs)
        self._toolbar()
        self.prog = QProgressBar()
        self.prog.setMaximumWidth(260)
        self.prog.setVisible(False)
        self.statusBar().addPermanentWidget(self.prog)

    # ================================================================== layout helpers
    @staticmethod
    def _wrap(w, title, text):
        box = QWidget()
        lay = QVBoxLayout(box)
        lay.setContentsMargins(4, 4, 4, 4)
        lab = QLabel(f"<span style='font-size:12pt;font-weight:600;color:#1F4E79'>{title}</span>"
                     f"<br><span style='color:#333'>{text}</span>")
        lab.setWordWrap(True)
        lab.setStyleSheet("padding:4px 6px")
        lay.addWidget(lab)
        lay.addWidget(w, 1)
        return box

    @staticmethod
    def _scroll(w):
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(w)
        return sa

    def _browser(self):
        b = QTextBrowser()
        b.setOpenExternalLinks(True)
        return b

    def _results_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        top = QHBoxLayout()
        self.res_cols = QComboBox()
        self.res_cols.addItems(["Main columns", "All columns"])
        self.res_cols.currentIndexChanged.connect(self._fill_results)
        b = QPushButton("Export everything to Excel…")
        b.clicked.connect(self.export_excel)
        self.res_info = QLabel("Run the calculation (▶ Run, F5) to see the results.")
        top.addWidget(QLabel("Show:"))
        top.addWidget(self.res_cols)
        top.addWidget(b)
        top.addStretch(1)
        lay.addLayout(top)
        lay.addWidget(self.res_info)
        self.res_model = FrameModel()
        self.res_view = QTableView()
        self.res_view.setModel(self.res_model)
        self.res_view.setAlternatingRowColors(True)
        self.res_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        lay.addWidget(self.res_view, 1)
        return w

    def _report_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        top = QHBoxLayout()
        b1, b2 = QPushButton("Save the report (HTML)…"), QPushButton("Open the report in the web browser")
        b1.clicked.connect(self.save_report)
        b2.clicked.connect(self.open_report)
        top.addWidget(b1)
        top.addWidget(b2)
        top.addWidget(QLabel("  The web-browser view shows the report in its full layout."))
        top.addStretch(1)
        lay.addLayout(top)
        self.report = self._browser()
        self.report.setHtml("<p style='color:#555'>Press ▶ Run (F5). The full report appears here: the input "
                            "check, every calculation step, the complete EVo output, the uplift tables, "
                            "detectability and the figures.</p>")
        lay.addWidget(self.report, 1)
        return w

    def _cell_tab(self, form, button, slot):
        w = QWidget()
        lay = QHBoxLayout(w)
        left = QVBoxLayout()
        left.addWidget(form)
        b = QPushButton(button)
        b.setStyleSheet("font-weight:bold;padding:6px")
        b.clicked.connect(slot)
        left.addWidget(b)
        left.addStretch(1)
        holder = QWidget()
        holder.setLayout(left)
        holder.setMaximumWidth(560)
        out = self._browser()
        form.output = out
        lay.addWidget(holder)
        lay.addWidget(out, 1)
        return w

    def _guide_tab(self):
        b = self._browser()
        b.setOpenExternalLinks(False)
        b.setOpenLinks(True)
        b.setHtml(guide_html(self.nb.specs))
        return b

    def _toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextOnly)

        def act(text, slot, key=None, tip=None):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if key:
                a.setShortcut(QKeySequence(key))
            if tip:
                a.setToolTip(tip)
            tb.addAction(a)
            return a
        act("New (empty tables)", self.new_empty, "Ctrl+N")
        ex = QToolButton()
        ex.setText("Examples ▾")
        ex.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(ex)
        for name in self.nb.examples:
            menu.addAction(name, lambda n=name: self.load_example(n))
        ex.setMenu(menu)
        tb.addWidget(ex)
        act("Open…", self.open_project, "Ctrl+O")
        act("Save", self.save_project, "Ctrl+S")
        act("Save as…", lambda: self.save_project(as_new=True), "Ctrl+Shift+S")
        tb.addSeparator()
        self.run_action = act("▶ Run", self.run_all, "F5", "Run the whole calculation (F5)")
        f = self.run_action.font()
        f.setBold(True)
        self.run_action.setFont(f)
        tb.addSeparator()
        act("Export to Excel…", self.export_excel)
        act("Save report…", self.save_report)
        tb.addSeparator()
        act("About", self.about)

    # ================================================================== state
    def _tables_changed(self):
        self.edited = True
        self._mark_dirty()

    def _mark_dirty(self):
        self.dirty_since_run = True
        self._title()

    def _title(self):
        name = os.path.basename(self.path) if self.path else (self.start_from or "untitled")
        star = " *" if self.edited else ""
        self.setWindowTitle(f"Magma compressibility & surface uplift — {name}{star}")

    def _tab_changed(self, i):
        sources = {"magmas": self.editors["magmas"].names(), "reservoirs": self.editors["reservoirs"].names()}
        sources = {k: [n for n in v if n] for k, v in sources.items()}
        self.map_form.refresh_combos(sources)
        self.calc_form.refresh_combos(sources)

    def tables(self):
        return {k: ed.as_table() for k, ed in self.editors.items()}

    def all_settings(self):
        return dict(self.settings.values(), **self.map_form.values(), **self.calc_form.values())

    def _confirm_replace(self):
        if not self.edited:
            return True
        r = QMessageBox.question(self, "Replace the tables?",
                                 "The tables hold changes that are not saved in a project file. Replace them? "
                                 "(Undo in each table can bring them back.)")
        return r == QMessageBox.Yes

    def load_example(self, name, ask=True):
        if ask and not self._confirm_replace():
            return
        ex = self.nb.examples[name]
        for k, ed in self.editors.items():
            ed.push_undo()
            ed.load_text({"magmas": ex["MAGMAS"], "reservoirs": ex["RESERVOIRS"]}.get(k, ""))
            ed.rebuild()
        self.start_from, self.edited, self.path = name, False, None
        self._mark_dirty()
        self._title()
        self.statusBar().showMessage(f"Loaded: {name}", 6000)

    def new_empty(self):
        if not self._confirm_replace():
            return
        for ed in self.editors.values():
            ed.push_undo()
            ed._blank()
            ed.rebuild()
        self.start_from, self.edited, self.path = self.nb.labels["empty"], False, None
        self._mark_dirty()
        self.tabs.setCurrentIndex(0)

    # ================================================================== project files
    def project_dict(self):
        return dict(app="MagmaUplift", version=1, start_from=self.start_from, edited=self.edited,
                    tables={k: dict(header=h, rows=r) for k, (h, r) in self.tables().items()},
                    settings=self.all_settings())

    def apply_project(self, d):
        for k, ed in self.editors.items():
            t = d.get("tables", {}).get(k)
            if t is None:
                ed._blank()
            else:
                ed.load_table(t["header"], t["rows"])
            ed.rebuild()
        vals = d.get("settings", {})
        for form in (self.settings, self.map_form, self.calc_form):
            form.set_values(vals)
        self.start_from = d.get("start_from")
        self.edited = bool(d.get("edited"))
        self._mark_dirty()

    def open_project(self):
        if not self._confirm_replace():
            return
        p, _ = QFileDialog.getOpenFileName(self, "Open a project", "", PROJECT_FILTER)
        if not p:
            return
        try:
            self.apply_project(json.load(open(p, encoding="utf-8")))
        except Exception as e:                       # noqa: BLE001
            return QMessageBox.warning(self, "Open", f"This file could not be read:\n{e}")
        self.path, self.edited = p, False
        self._title()

    def save_project(self, as_new=False):
        p = self.path
        if as_new or not p:
            p, _ = QFileDialog.getSaveFileName(self, "Save the project", self.path or "my_volcano.mcu", PROJECT_FILTER)
            if not p:
                return False
            if not os.path.splitext(p)[1]:
                p += ".mcu"
        try:
            d = self.project_dict()
        except ValueError as e:
            QMessageBox.warning(self, "Save", str(e))
            return False
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self.path, self.edited = p, False
        self._title()
        self.statusBar().showMessage(f"Saved {p}", 6000)
        return True

    @staticmethod
    def session_file():
        d = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, "last_session.mcu")

    def restore_session(self):
        p = self.session_file()
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                self.apply_project(d)
                self.path = d.get("path") if d.get("path") and os.path.exists(d.get("path")) else None
                self._title()
                self.statusBar().showMessage("Your last session has been restored.", 8000)
                return True
            except Exception:                          # noqa: BLE001
                pass
        return False

    def closeEvent(self, e):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(self, "Busy", "Please wait until the calculation has finished.")
            e.ignore()
            return
        try:
            d = self.project_dict()
            d["path"] = self.path
            json.dump(d, open(self.session_file(), "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:                              # noqa: BLE001
            pass
        e.accept()

    # ================================================================== running
    def _start(self, fn, on_done, label):
        if self.worker is not None and self.worker.isRunning():
            return
        try:
            tables, settings = self.tables(), self.all_settings()
        except ValueError as e:
            self.tabs.setCurrentIndex(3)
            return QMessageBox.warning(self, "Settings", str(e))
        self.prog.setVisible(True)
        self.prog.setRange(0, 18)
        self.run_action.setEnabled(False)
        self.statusBar().showMessage(label)
        start = self.start_from or self.nb.labels["empty"]
        self.worker = Worker(lambda progress: fn(tables, settings, start, progress))
        self.worker.progress.connect(lambda c, t: (self.prog.setValue(c),
                                                   self.statusBar().showMessage(
                                                       f"{label}  {TITLES.get(c, t)}")))
        self.worker.done.connect(lambda r: self._finished(r, on_done))
        self.worker.failed.connect(self._failed)
        self.worker.start()

    def _end(self):
        self.prog.setVisible(False)
        self.run_action.setEnabled(True)

    def run_all(self):
        def job(tables, settings, start, progress):
            return self.nb.run(tables, settings, start, self.edited, progress=progress)
        self._start(job, self._show_all, "Calculating…")

    def _finished(self, result, on_done):
        self._end()
        on_done(result)

    def _failed(self, e):
        self._end()
        self._show_report(partial=True)
        if isinstance(e, CellError) and e.input_error:
            msg = str(e)
            tab = 0 if ("Magma" in msg and "Reservoir table" not in msg) else 1
            if "Step-2 table" in msg:
                tab = 2
            self.tabs.setCurrentIndex(tab)
            QMessageBox.warning(self, "Please correct the input", msg)
        else:
            cell = (f"“{TITLES.get(e.cell, nbcells.TITLES[e.cell])}”" if isinstance(e, CellError)
                    else "the calculation")
            QMessageBox.critical(self, "Calculation stopped", f"The calculation stopped in {cell}:\n\n{e}")
        self.statusBar().showMessage("Stopped — see the message.", 10000)

    def _show_all(self, seconds):
        self.dirty_since_run = False
        self._show_report()
        self._fill_results()
        for form, cell in ((self.map_form, MAP_CELL), (self.calc_form, CALC_CELL)):
            form.output.setHtml(self._cell_html(cell))
        self.statusBar().showMessage(f"Done in {seconds:.1f} s.", 10000)
        self.tabs.setCurrentIndex(4)

    def _cell_html(self, cell):
        return self.nb.report_html(cells=(cell,), for_qt=True)

    def _show_report(self, partial=False):
        self.report.setHtml(self.nb.report_html(for_qt=True))

    def _fill_results(self):
        res = self.nb.ns.get("res")
        if not isinstance(res, pd.DataFrame):
            return
        if self.res_cols.currentIndex() == 0:
            main = ["name", "shape", "depth_km", "P_MPa", "T_C", "saturated", "P_sat_MPa", "phi", "beta_m", "beta_c", "rV"]
            extra = [c for c in res.columns if re.match(r"(Ve|dVc)\d+_m3$", c) or re.match(r"uz\d+_0km_mm$", c)]
            res = res[[c for c in main if c in res.columns] + extra]
        self.res_model.set(res.reset_index(drop=True))
        self.res_info.setText(f"<b>{len(res)} reservoir configurations.</b> phi = vapour volume fraction; "
                              "β in Pa⁻¹; r<sub>V</sub> = 1 + β<sub>m</sub>/β<sub>c</sub>; Ve = injected volume, "
                              "dVc = chamber volume change (m³); uz = uplift (mm) at the given distance. "
                              "The Report tab explains every column.")

    def _cell_job(self, cell, form):
        def job(tables, settings, start, progress):
            if self.dirty_since_run:
                self.nb.run(tables, settings, start, self.edited, progress=progress)
            self.nb.run_cell(cell, settings)
            return cell
        return job

    def draw_map(self):
        self._start(self._cell_job(MAP_CELL, self.map_form), self._cell_done, "Drawing the map…")

    def calculate(self):
        self._start(self._cell_job(CALC_CELL, self.calc_form), self._cell_done, "EVo is calculating…")

    def _cell_done(self, cell):
        if self.dirty_since_run:
            self._show_all(0)
        self.dirty_since_run = False
        form = self.map_form if cell == MAP_CELL else self.calc_form
        form.output.setHtml(self._cell_html(cell))
        self.tabs.setCurrentIndex(6 if cell == MAP_CELL else 7)
        self.statusBar().showMessage("Done.", 5000)

    # ================================================================== export
    def _need_results(self):
        if not isinstance(self.nb.ns.get("res"), pd.DataFrame):
            QMessageBox.information(self, "No results yet", "Run the calculation first (▶ Run, F5).")
            return False
        return True

    def save_report(self):
        if not self._need_results():
            return
        p, _ = QFileDialog.getSaveFileName(self, "Save the report", "report.html", "Web page (*.html)")
        if p:
            open(p, "w", encoding="utf-8").write(self.nb.report_html(title=self.nb.ns.get("PROJECT", "Report")))
            self.statusBar().showMessage(f"Saved {p}", 6000)

    def open_report(self):
        if not self._need_results():
            return
        p = os.path.join(tempfile.gettempdir(), f"magma_uplift_report_{int(time.time())}.html")
        open(p, "w", encoding="utf-8").write(self.nb.report_html(title=self.nb.ns.get("PROJECT", "Report")))
        QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def export_excel(self):
        if not self._need_results():
            return
        p, _ = QFileDialog.getSaveFileName(self, "Export to Excel", "results.xlsx", "Excel workbook (*.xlsx)")
        if not p:
            return
        try:
            self.write_excel(p)
        except Exception as e:                       # noqa: BLE001
            return QMessageBox.warning(self, "Export", f"The file could not be written:\n{e}")
        self.statusBar().showMessage(f"Saved {p}", 6000)

    def write_excel(self, p):
        ns = self.nb.ns
        states = []
        for s in ns.get("STEP2_STATES", {}).values():
            row = dict(reservoirs="; ".join(s.get("labels", [])), role=s.get("role"), magma=s.get("comp"),
                       P_MPa=s.get("P"), T_C=s.get("T"))
            row.update({k: v for k, v in s["st"].items() if isinstance(v, (int, float, str, bool, np.floating, np.integer))
                        or v is None})
            states.append(row)
        with pd.ExcelWriter(p, engine="openpyxl") as xw:
            ns["res"].to_excel(xw, sheet_name="Results", index=False)
            if states:
                pd.DataFrame(states).to_excel(xw, sheet_name="EVo states (step 2)", index=False)
            for k, sheet in (("magmas", "Magmas"), ("reservoirs", "Reservoirs"), ("step2", "Step 2 by hand")):
                h, r = self.editors[k].as_table()
                pd.DataFrame(r, columns=h).to_excel(xw, sheet_name=sheet, index=False)
            sv = self.all_settings()
            pd.DataFrame({"setting": list(sv), "value": [str(v) for v in sv.values()]}).to_excel(
                xw, sheet_name="Settings", index=False)

    def about(self):
        AboutDialog(self).exec()


def _app_spec(spec):
    """Field lists of the tables with the program's wording (cell numbers → tab names)."""
    sp = copy.deepcopy(spec)
    for f in sp["fields"]:
        f["help"], f["group"] = app_text(f["help"]), app_text(f["group"])
        f["hint"] = hint_text(f["hint"])
    return sp

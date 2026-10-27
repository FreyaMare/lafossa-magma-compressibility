"""Fill-in tables of the window (magmas, reservoirs, step 2 by hand).

The values are kept as text in `items` (one dict per magma / reservoir / row) and `extra` (rows or
columns that are not in the field list, e.g. expert EVo keys); the QTableWidget only shows them.
as_table() gives the same (header, rows) as the notebook's fill-in tables, which cells 10 and later read.
"""
import copy
import re

import numpy as np
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QKeySequence, QBrush, QGuiApplication, QPalette
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QPushButton,
                               QStyledItemDelegate, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
                               QStyleOptionViewItem, QStyle, QInputDialog)

BLUE, GROUP_BG, NAME_BG, BAD_BG = QColor("#1F4E79"), QColor("#dfe8f2"), QColor("#eef4fb"), QColor("#fde3e1")
HINT = QColor("#9aa5b1")
NAME = "__name__"


def numlike(s, many=False):
    """Empty, or readable as a number (or as numbers separated by ;) — the notebook's rule."""
    parts = re.split(r"[;\s]+", str(s).strip()) if many else [str(s)]
    for p in parts:
        p = (p.strip().replace("−", "-").replace("×10^", "e").replace("x10^", "e")
             .replace("·10^", "e").replace("*10^", "e").replace(" ", ""))
        if p in ("", "-", "—", "–"):
            continue
        try:
            if not np.isfinite(float(p)):
                return False
        except ValueError:
            return False
    return True


def _choices(f):
    return [tuple(c) if isinstance(c, (tuple, list)) else (c, c) for c in f["choices"]]


class _Delegate(QStyledItemDelegate):
    """Editors by field kind (drop-down lists, name suggestions, text) and grey hints in empty cells."""

    def __init__(self, ed):
        super().__init__(ed.table)
        self.ed = ed

    def createEditor(self, parent, option, index):
        f = self.ed.field_at(index.row(), index.column())
        if f is not None and f["kind"] == "choice":
            cb = QComboBox(parent)
            for lab, val in [("—", "")] + _choices(f):
                cb.addItem(lab, val)
            cb.activated.connect(lambda *_: (self.commitData.emit(cb), self.closeEditor.emit(cb)))
            QTimer.singleShot(0, cb.showPopup)
            return cb
        if f is not None and f["kind"] == "ref":
            cb = QComboBox(parent)
            cb.setEditable(True)
            cb.addItems([""] + self.ed.ref_names(f["ref"]))
            cb.activated.connect(lambda *_: (self.commitData.emit(cb), self.closeEditor.emit(cb)))
            return cb
        le = QLineEdit(parent)
        if f is not None:
            le.setPlaceholderText(f.get("hint", ""))
        return le

    def setEditorData(self, editor, index):
        val = index.data(Qt.EditRole) or ""
        if isinstance(editor, QComboBox) and not editor.isEditable():
            i = editor.findData(val)
            if i < 0:
                hit = [k for k in range(editor.count()) if str(editor.itemData(k)).lower() == val.lower()]
                if hit:
                    i = hit[0]
                else:
                    editor.addItem(val, val)
                    i = editor.count() - 1
            editor.setCurrentIndex(i)
        elif isinstance(editor, QComboBox):
            editor.setEditText(val)
        else:
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox) and not editor.isEditable():
            model.setData(index, editor.currentData() or "", Qt.EditRole)
        elif isinstance(editor, QComboBox):
            model.setData(index, editor.currentText().strip(), Qt.EditRole)
        else:
            model.setData(index, editor.text().strip(), Qt.EditRole)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if index.data(Qt.DisplayRole):
            return
        f = self.ed.field_at(index.row(), index.column())
        hint = (f or {}).get("hint") or ("—" if f is not None and f["kind"] == "choice" else "")
        if hint:
            painter.save()
            painter.setPen(HINT)
            painter.drawText(option.rect.adjusted(5, 0, -3, 0), Qt.AlignVCenter | Qt.AlignLeft, hint)
            painter.restore()


class _Table(QTableWidget):
    """QTableWidget with Excel-style copy, paste and delete."""

    def __init__(self, ed):
        super().__init__()
        self.ed = ed

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Copy):
            self.ed.copy_selection()
        elif e.matches(QKeySequence.Paste):
            self.ed.paste()
        elif e.matches(QKeySequence.Undo):
            self.ed.undo()
        elif e.matches(QKeySequence.Redo):
            self.ed.redo()
        elif e.key() in (Qt.Key_Delete, Qt.Key_Backspace) and not self.state() == QAbstractItemView.EditingState:
            self.ed.clear_selection()
        else:
            super().keyPressEvent(e)


class TableEditor(QWidget):
    changed = Signal()
    renamed = Signal(str, str)          # old name, new name (magmas or reservoirs)

    def __init__(self, key, spec, split_text, parent=None):
        super().__init__(parent)
        self.key, self.split_text = key, split_text
        self.fields, self.orient, self.item = spec["fields"], spec["orient"], spec["item"]
        opts = spec.get("options", {})
        self.fmap = {f["key"]: f for f in self.fields}
        self.lower = {f["key"].lower(): f["key"] for f in self.fields}
        self.name_key = NAME if self.orient == "cols" else self.fields[0]["key"]
        self.extra_label = opts.get("extra_label")
        self.more_label = opts.get("more_label", "Show more rows")
        self.min_items = opts.get("min_items", 1)
        self.items, self.extra = [], []
        self.show_all, self.ref_sources = False, {}
        self._undo, self._redo, self._busy = [], [], False
        self.row_keys, self.col_keys = [], []

        # ------------------------------------------------ buttons
        bar = QHBoxLayout()
        word = self.item
        self.b_add = QPushButton(f"+ Add {word}")
        self.b_copy = QPushButton(f"Copy {word}")
        self.b_del = QPushButton(f"Remove {word}")
        self.b_add.setToolTip(f"Add an empty {word}")
        self.b_copy.setToolTip(f"Copy the {word} of the selected cell")
        self.b_del.setToolTip(f"Remove the {word} of the selected cell")
        self.b_add.clicked.connect(self.add_item)
        self.b_copy.clicked.connect(self.copy_current)
        self.b_del.clicked.connect(self.remove_current)
        for b in (self.b_add, self.b_copy, self.b_del):
            bar.addWidget(b)
        if self.extra_label:
            b = QPushButton(self.extra_label.replace("+ ", "+ "))
            b.setToolTip("A row for any EVo setting that should differ for one magma (expert)")
            b.clicked.connect(self.add_extra)
            bar.addWidget(b)
        self.cb_more = None
        if any(f["optional"] for f in self.fields):
            self.cb_more = QCheckBox(self.more_label)
            self.cb_more.setToolTip("Show the optional rows/columns even when they are empty")
            self.cb_more.toggled.connect(self._toggle_more)
            bar.addWidget(self.cb_more)
        bar.addStretch(1)
        self.b_undo, self.b_redo = QPushButton("↶ Undo"), QPushButton("↷ Redo")
        self.b_undo.clicked.connect(self.undo)
        self.b_redo.clicked.connect(self.redo)
        self.b_text = QPushButton("Text view…")
        self.b_text.setToolTip("The whole table as text: copy it, or paste a table from Excel / Google Sheets / text")
        self.b_text.clicked.connect(self.text_dialog)
        self.b_clear = QPushButton("Empty table")
        self.b_clear.clicked.connect(self.clear_all)
        for b in (self.b_undo, self.b_redo, self.b_text, self.b_clear):
            bar.addWidget(b)

        self.status = QLabel()
        self.status.setStyleSheet("color:#1F4E79;padding:2px 0")
        self.table = _Table(self)
        self.table.setItemDelegate(_Delegate(self))
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked |
                                   QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.table.itemChanged.connect(self._item_changed)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setDefaultSectionSize(24)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.addLayout(bar)
        lay.addWidget(self.status)
        lay.addWidget(self.table, 1)
        self._blank()
        self.rebuild()

    # ================================================================== data
    def _blank(self):
        self.extra = []
        self.items = [({NAME: ""} if self.orient == "cols" else {}) for _ in range(self.min_items)]

    def load_table(self, header, rows):
        """(header, rows) as in the notebook's text tables → items."""
        items, extra = [], []

        def slot(name):
            k = self.lower.get(name.strip().lower())
            if k:
                return k
            if name.strip() not in extra:
                extra.append(name.strip())
            return ("x", extra.index(name.strip()))
        if self.orient == "cols":
            items = [{NAME: n.strip()} for n in header[1:]]
            for r in rows:
                if not r or not r[0].strip():
                    continue
                s = slot(r[0])
                for it, v in zip(items, r[1:]):
                    if v.strip():
                        it[s] = v.strip()
        else:
            slots = [slot(h) if h.strip() else None for h in header]
            for r in rows:
                it = {s: v.strip() for s, v in zip(slots, r) if s is not None and v.strip()}
                if it:
                    items.append(it)
        self.items, self.extra = items, extra
        while len(self.items) < self.min_items:
            self.items.append({NAME: ""} if self.orient == "cols" else {})

    def load_text(self, text):
        self.load_table(*self.split_text(text)) if str(text).strip() else self._blank()

    @staticmethod
    def _filled(it):
        return any(str(v).strip() for v in it.values())

    def names(self):
        return [str(it.get(self.name_key, "")).strip() for it in self.items]

    def as_table(self):
        keys = [f["key"] for f in self.fields]
        xs = [(j, k) for j, k in enumerate(self.extra) if k.strip()]
        its = [it for it in self.items if self._filled(it)]
        val = lambda it, k: str(it.get(k, "")).strip()
        if self.orient == "cols":
            header = ["property"] + [val(it, NAME) for it in its]
            rows = [[k] + [val(it, k) for it in its] for k in keys]
            rows += [[k.strip()] + [val(it, ("x", j)) for it in its] for j, k in xs]
        else:
            header = keys + [k.strip() for _, k in xs]
            rows = [[val(it, k) for k in keys] + [val(it, ("x", j)) for j, _ in xs] for it in its]
        return header, rows

    def to_text(self):
        header, rows = self.as_table()
        if self.orient == "cols":
            rows = [r for r in rows if any(r[1:]) or not self.fmap.get(r[0], {}).get("optional", False)]
        else:
            keep = [j for j, h in enumerate(header)
                    if any(r[j] for r in rows) or (h in self.fmap and not self.fmap[h]["optional"])]
            header, rows = [header[j] for j in keep], [[r[j] for j in keep] for r in rows]
        tab = [[c.replace("|", "/") for c in r] for r in [header] + rows]
        w = [min(24, max(len(r[j]) for r in tab)) for j in range(len(header))]
        return "\n".join(" | ".join(c.ljust(w[j]) for j, c in enumerate(r)).rstrip() for r in tab)

    def state(self):
        return copy.deepcopy((self.items, self.extra))

    def set_state(self, st, push=True):
        if push:
            self.push_undo()
        self.items, self.extra = copy.deepcopy(st[0]), copy.deepcopy(st[1])
        self.rebuild()
        self.changed.emit()

    # ================================================================== undo
    def push_undo(self):
        self._undo.append(self.state())
        self._undo = self._undo[-200:]
        self._redo.clear()
        self._update_buttons()

    def undo(self):
        if self._undo:
            self._redo.append(self.state())
            self.items, self.extra = self._undo.pop()
            self.rebuild()
            self.changed.emit()

    def redo(self):
        if self._redo:
            self._undo.append(self.state())
            self.items, self.extra = self._redo.pop()
            self.rebuild()
            self.changed.emit()

    def _update_buttons(self):
        self.b_undo.setEnabled(bool(self._undo))
        self.b_redo.setEnabled(bool(self._redo))

    # ================================================================== structure edits
    def _current_item(self):
        r, c = self.table.currentRow(), self.table.currentColumn()
        if self.orient == "cols":
            i = c - 1
        else:
            i = r
        return i if 0 <= i < len(self.items) else None

    def _unique(self, name):
        used = {n.upper() for n in self.names()}
        base, i, new = name, 2, name
        while new.upper() in used:
            new = f"{base}_{i}" if self.orient == "cols" else f"{base} ({i})"
            i += 1
        return new

    def add_item(self):
        self.push_undo()
        self.items.append({NAME: ""} if self.orient == "cols" else {})
        self.rebuild()
        n = len(self.items)
        if self.orient == "cols":
            self.table.setCurrentCell(0, n)
        else:
            self.table.setCurrentCell(n - 1, 0)
        self.changed.emit()

    def copy_current(self):
        i = self._current_item()
        if i is None:
            return QMessageBox.information(self, "Copy", f"Click a cell of the {self.item} to copy first.")
        self.push_undo()
        new = copy.deepcopy(self.items[i])
        if str(new.get(self.name_key, "")).strip():
            new[self.name_key] = self._unique(str(new[self.name_key]).strip())
        self.items.insert(i + 1, new)
        self.rebuild()
        self.changed.emit()

    def remove_current(self):
        i = self._current_item()
        if i is None:
            return QMessageBox.information(self, "Remove", f"Click a cell of the {self.item} to remove first.")
        self.push_undo()
        del self.items[i]
        if len(self.items) < self.min_items:
            self.items.append({NAME: ""} if self.orient == "cols" else {})
        self.rebuild()
        self.changed.emit()

    def add_extra(self):
        key, ok = QInputDialog.getText(self, "EVo setting for one magma",
                                       "Name of the EVo setting (e.g. H2_MODEL, SULFIDE_CAPACITY, DP_MAX):")
        if ok and key.strip():
            self.push_undo()
            self.extra.append(key.strip())
            self.rebuild()
            self.changed.emit()

    def clear_all(self):
        self.push_undo()
        self._blank()
        self.rebuild()
        self.changed.emit()

    def _toggle_more(self, on):
        self.show_all = on
        self.rebuild()

    # ================================================================== names shared between tables
    def ref_names(self, ref):
        src = self.ref_sources.get(ref)
        return [n for n in (src() if src else []) if n]

    def rename_ref(self, ref, old, new):
        """Another table renamed `old` to `new`: follow it in the columns that refer to that table."""
        o = old.strip().upper()
        if not o or not new.strip():
            return
        hit = False
        for it in self.items:
            for f in self.fields:
                if f.get("ref") == ref and str(it.get(f["key"], "")).strip().upper() == o:
                    it[f["key"]] = new.strip()
                    hit = True
        if hit:
            self.rebuild()
            self.changed.emit()

    # ================================================================== drawing
    def _visible(self, f):
        return (not f["optional"]) or self.show_all or any(str(it.get(f["key"], "")).strip() for it in self.items)

    def field_at(self, r, c):
        """Field dict of a cell (None for labels and group rows)."""
        if self.orient == "cols":
            if c == 0 or r >= len(self.row_keys):
                return None
            k = self.row_keys[r]
        else:
            if c >= len(self.col_keys):
                return None
            k = self.col_keys[c]
        if k == NAME:
            return dict(key=NAME, kind="text", hint="NAME", optional=False)
        if isinstance(k, tuple) and k[0] == "x":
            return dict(key=k, kind="text", hint="", optional=False)
        return self.fmap.get(k) if isinstance(k, str) else None

    def _cell_item(self, value, f):
        it = QTableWidgetItem(value)
        if f is not None and f["kind"] in ("num", "list") and not numlike(value, f["kind"] == "list"):
            it.setBackground(BAD_BG)
            it.setToolTip("Not a number")
        return it

    def rebuild(self):
        self._busy = True
        t = self.table
        t.clear()
        t.clearSpans()
        if self.orient == "cols":
            self._build_cols()
        else:
            self._build_rows()
        self._busy = False
        self._update_buttons()
        self._show_status()

    def _build_cols(self):
        t, n = self.table, len(self.items)
        rows = [NAME]
        group = None
        for f in self.fields:
            if not self._visible(f):
                continue
            if f["group"] != group:
                group = f["group"]
                rows.append(("group", group))
            rows.append(f["key"])
        if self.extra:
            rows.append(("group", "Extra rows — an EVo setting for one magma only (expert)"))
            rows += [("x", j) for j in range(len(self.extra))]
        self.row_keys = rows
        t.setColumnCount(n + 1)
        t.setRowCount(len(rows))
        t.setHorizontalHeaderLabels(["Property"] + [f"{self.item.capitalize()} {i + 1}" for i in range(n)])
        t.verticalHeader().setVisible(False)
        bold = QFont()
        bold.setBold(True)
        for r, k in enumerate(rows):
            if isinstance(k, tuple) and k[0] == "group":
                it = QTableWidgetItem(k[1])
                it.setFlags(Qt.ItemIsEnabled)
                it.setBackground(GROUP_BG)
                it.setForeground(BLUE)
                it.setFont(bold)
                t.setItem(r, 0, it)
                t.setSpan(r, 0, 1, n + 1)
                continue
            if k == NAME:
                lab = QTableWidgetItem(f"{self.item.capitalize()} name")
                lab.setFont(bold)
            elif isinstance(k, tuple):
                lab = QTableWidgetItem(self.extra[k[1]])
                lab.setToolTip("EVo setting key — double-click to rename")
                lab.setForeground(QColor("#b35c00"))
            else:
                f = self.fmap[k]
                unit = f" ({f['unit']})" if f["unit"] else ""
                lab = QTableWidgetItem(f"{f['label']}{unit}   [{k}]")
                lab.setToolTip(f["help"] or f["label"])
            if not (isinstance(k, tuple) and k[0] == "x"):
                lab.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            t.setItem(r, 0, lab)
            for i, item in enumerate(self.items):
                cell = self._cell_item(str(item.get(k, "")), self.field_at(r, i + 1))
                if k == NAME:
                    cell.setFont(bold)
                    cell.setForeground(BLUE)
                    cell.setBackground(NAME_BG)
                t.setItem(r, i + 1, cell)
        hh = t.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Interactive)
        t.setColumnWidth(0, 330)
        for i in range(n):
            t.setColumnWidth(i + 1, 140)

    def _build_rows(self):
        t = self.table
        cols = [f["key"] for f in self.fields if self._visible(f)] + [("x", j) for j in range(len(self.extra))]
        self.col_keys = cols
        t.setRowCount(len(self.items))
        t.setColumnCount(len(cols))
        t.verticalHeader().setVisible(True)
        for c, k in enumerate(cols):
            if isinstance(k, tuple):
                h = QTableWidgetItem(f"{self.extra[k[1]]}\n(unknown column)")
                h.setForeground(QColor("#b35c00"))
                h.setToolTip("Not a known column — it will be reported when the calculation runs. "
                             "Remove it with Text view or Empty table.")
                width = 110
            else:
                f = self.fmap[k]
                h = QTableWidgetItem(f"{f['label']}\n{f['unit']}" if f["unit"] else f"{f['label']}\n")
                h.setToolTip(f"{f['group']} · {k}\n{f['help'] or f['label']}")
                width = max(64, int((f["width"] or 70) * 1.05))
            t.setHorizontalHeaderItem(c, h)
            t.setColumnWidth(c, width)
        for r, item in enumerate(self.items):
            for c, k in enumerate(cols):
                t.setItem(r, c, self._cell_item(str(item.get(k, "")), self.field_at(r, c)))
        t.horizontalHeader().setMinimumHeight(40)

    def _show_status(self):
        n = sum(1 for it in self.items if self._filled(it))
        self.status.setText(f"<b>{n} {self.item}{'' if n == 1 else 's'}</b> · double-click or type to edit · "
                            "grey text = what an empty cell means · Ctrl+C / Ctrl+V copy and paste blocks "
                            "(also from Excel) · Delete clears the selected cells")

    # ================================================================== cell edits
    def _slot(self, r, c):
        """(item index, key) of a data cell, or None."""
        if self.orient == "cols":
            if c == 0:
                k = self.row_keys[r] if r < len(self.row_keys) else None
                return ("extra-key", k[1]) if isinstance(k, tuple) and k[0] == "x" else None
            k = self.row_keys[r]
            if isinstance(k, tuple) and k[0] == "group":
                return None
            return (c - 1, k)
        return (r, self.col_keys[c])

    def _item_changed(self, cell):
        if self._busy:
            return
        s = self._slot(cell.row(), cell.column())
        if s is None:
            return
        new = cell.text().strip()
        if s[0] == "extra-key":
            self.push_undo()
            self.extra[s[1]] = new
            self.changed.emit()
            return
        i, k = s
        old = str(self.items[i].get(k, ""))
        if new == old.strip():
            return
        self.push_undo()
        self.items[i][k] = new
        f = self.field_at(cell.row(), cell.column())
        self._busy = True
        if f is not None and f["kind"] in ("num", "list"):
            bad = not numlike(new, f["kind"] == "list")
            cell.setBackground(BAD_BG if bad else QBrush())
            cell.setToolTip("Not a number" if bad else "")
        self._busy = False
        self._show_status()
        if k == self.name_key and old.strip() and new and old.strip().upper() not in {x.upper() for x in self.names()}:
            self.renamed.emit(old.strip(), new)
        self.changed.emit()

    def _data_cells(self, rect_rows, rect_cols):
        return [(r, c) for r in rect_rows for c in rect_cols if self._slot(r, c) not in (None,)]

    def clear_selection(self):
        cells = [(i.row(), i.column()) for i in self.table.selectedIndexes()]
        cells = [(r, c) for r, c in cells if self._slot(r, c) is not None and self._slot(r, c)[0] != "extra-key"]
        if not cells:
            return
        self.push_undo()
        for r, c in cells:
            i, k = self._slot(r, c)
            self.items[i].pop(k, None)
        self.rebuild()
        self.changed.emit()

    def copy_selection(self):
        rng = self.table.selectedRanges()
        if not rng:
            return
        g = rng[0]
        lines = []
        for r in range(g.topRow(), g.bottomRow() + 1):
            if self.orient == "cols" and isinstance(self.row_keys[r], tuple) and self.row_keys[r][0] == "group":
                continue
            vals = []
            for c in range(g.leftColumn(), g.rightColumn() + 1):
                it = self.table.item(r, c)
                vals.append(it.text() if it else "")
            lines.append("\t".join(vals))
        QGuiApplication.clipboard().setText("\n".join(lines))

    def paste(self):
        text = QGuiApplication.clipboard().text()
        if not text.strip():
            return
        block = [ln.split("\t") for ln in text.rstrip("\n").split("\n")]
        r0, c0 = max(self.table.currentRow(), 0), max(self.table.currentColumn(), 0)
        self.push_undo()
        if self.orient == "cols":
            data_rows = [r for r in range(r0, len(self.row_keys))
                         if not (isinstance(self.row_keys[r], tuple) and self.row_keys[r][0] == "group")]
            c0 = max(c0, 1)
            for bi, vals in enumerate(block):
                if bi >= len(data_rows):
                    break
                r = data_rows[bi]
                for bj, v in enumerate(vals):
                    i = c0 - 1 + bj
                    while i >= len(self.items):
                        self.items.append({NAME: ""})
                    s = self._slot(r, i + 1)
                    if s and s[0] != "extra-key":
                        self.items[s[0]][s[1]] = v.strip()
        else:
            for bi, vals in enumerate(block):
                i = r0 + bi
                while i >= len(self.items):
                    self.items.append({})
                for bj, v in enumerate(vals):
                    c = c0 + bj
                    if c < len(self.col_keys):
                        self.items[i][self.col_keys[c]] = v.strip()
        self.rebuild()
        self.changed.emit()

    # ================================================================== text view
    def text_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"{self.item.capitalize()} table as text")
        dlg.resize(1000, 560)
        lay = QVBoxLayout(dlg)
        lab = QLabel("<b>Copy</b> this text to keep a copy of the table. <b>Paste</b> a table here — a block copied "
                     "from Excel or Google Sheets, or text with <code>|</code> between the cells, laid out like "
                     "the text shown — and press <i>Apply</i>.")
        lab.setWordWrap(True)
        ed = QPlainTextEdit()
        ed.setLineWrapMode(QPlainTextEdit.NoWrap)
        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        ed.setFont(f)
        ed.setPlainText(self.to_text())
        msg = QLabel()
        bb = QDialogButtonBox()
        b_apply = bb.addButton("Apply to the table", QDialogButtonBox.AcceptRole)
        b_copy = bb.addButton("Copy all", QDialogButtonBox.ActionRole)
        bb.addButton(QDialogButtonBox.Close)
        b_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(ed.toPlainText()))
        bb.rejected.connect(dlg.reject)

        def apply():
            try:
                header, rows = self.split_text(ed.toPlainText())
            except ValueError as e:
                msg.setText(f"<span style='color:#c0392b'>Not applied: {e}</span>")
                return
            if not header or not rows or (self.orient == "cols" and len(header) < 2):
                msg.setText("<span style='color:#c0392b'>Not applied: the text needs a header line and at least "
                            "one more line.</span>")
                return
            if self.orient == "rows" and not any(h.strip().lower() in self.lower for h in header):
                msg.setText("<span style='color:#c0392b'>Not applied: none of the column names in the first line "
                            "is known.</span>")
                return
            self.push_undo()
            self.load_table(header, rows)
            self.rebuild()
            self.changed.emit()
            dlg.accept()
        b_apply.clicked.connect(apply)
        lay.addWidget(lab)
        lay.addWidget(ed, 1)
        lay.addWidget(msg)
        lay.addWidget(bb)
        dlg.exec()

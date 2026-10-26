"""Start the program:  MagmaUplift.exe [project.mcu]              the window
                    MagmaUplift.exe --selftest [result.txt]    quick check of the calculation (thesis example)
                    MagmaUplift.exe --check-all [result.txt]   all volcanoes, all EVo modes, calculator, map
                    MagmaUplift.exe --smoke                    opens the window, runs, closes (build test)"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LAFOSSA = "La Fossa, Vulcano (Italy) — thesis"


def resource(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(HERE))
    return os.path.join(base, rel)


def default_settings():
    from .runner import params_of
    s = {p["name"]: p["default"] for c in (4, 7, 12, 14, 16, 17, 18) for p in params_of(c)}
    s.pop("START_FROM")
    return s


def selftest(out_path=None):
    """Runs the thesis example and compares every result with the values of the verified notebook."""
    import numpy as np
    from .runner import Notebook
    t0 = time.time()
    lines, ok = [], True
    try:
        nb = Notebook()
        nb.setup()
        ex = nb.examples[LAFOSSA]
        tables = {"magmas": nb.split_text(ex["MAGMAS"]), "reservoirs": nb.split_text(ex["RESERVOIRS"]),
                  "step2": ([f["key"] for f in nb.specs["step2"]["fields"]], [])}
        nb.run(tables, default_settings(), LAFOSSA, False)
        res = nb.ns["res"]
        ref = json.load(open(os.path.join(HERE, "selftest_reference.json"), encoding="utf-8"))
        worst = 0.0
        for col, vals in ref["columns"].items():
            a, b = np.asarray(vals, float), res[col].astype(float).to_numpy()
            both_nan = np.isnan(a) & np.isnan(b)
            rel = np.where(both_nan, 0.0, np.abs(a - b) / np.maximum(np.abs(a), 1e-300))
            w = float(np.nanmax(rel)) if np.isfinite(rel).all() else float("inf")
            worst = max(worst, w)
            if not w <= 1e-6:
                ok = False
                lines.append(f"  column {col}: largest relative difference {w:.3g}")
        lines.insert(0, f"Self-test (thesis example, {len(res)} reservoirs, {len(ref['columns'])} result columns): "
                        f"{'PASSED' if ok else 'FAILED'}; largest relative difference {worst:.2e}; "
                        f"{time.time() - t0:.1f} s")
    except Exception as e:                                  # noqa: BLE001
        import traceback
        ok = False
        lines = ["Self-test FAILED with an error:", traceback.format_exc()]
    _write("\n".join(lines), out_path, "selftest_result.txt")
    return 0 if ok else 1


def _write(text, out_path, default_name):
    if out_path is None:
        out_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.getcwd(),
                                default_name)
    try:
        open(out_path, "w", encoding="utf-8").write(text + "\n")
    except OSError:
        pass
    try:
        print(text)
    except Exception:                                       # noqa: BLE001
        pass


def check_all(out_path=None):
    """Runs the four ready-made volcanoes and a test volcano that uses every EVo mode, the EVo calculator and
    the map, and compares r_V and the uplift with the verified notebook (about two minutes)."""
    import numpy as np
    from .runner import Notebook, CellError
    lines, ok, t00 = [], True, time.time()
    nb = Notebook()
    nb.setup()
    cases = json.load(open(os.path.join(HERE, "check_cases.json"), encoding="utf-8"))
    s2_header = [f["key"] for f in nb.specs["step2"]["fields"]]
    for name, c in cases.items():
        t0 = time.time()
        if "example" in c:
            ex = nb.examples[c["example"]]
            mag, res_t, s2, start = ex["MAGMAS"], ex["RESERVOIRS"], "", c["example"]
        else:
            mag, res_t, s2, start = c["MAGMAS"], c["RESERVOIRS"], c["STEP2"], nb.labels["empty"]
        tables = {"magmas": nb.split_text(mag), "reservoirs": nb.split_text(res_t),
                  "step2": nb.split_text(s2) if s2.strip() else (s2_header, [])}
        try:
            nb.run(tables, dict(default_settings(), **c.get("settings", {})), start, False)
            res = nb.ns["res"]
            d = max(float(np.max(np.abs(res["rV"].to_numpy() - np.asarray(c["rV"])) / np.asarray(c["rV"]))),
                    float(np.max(np.abs(res["uz1_0km_mm"].to_numpy() - np.asarray(c["uz"])) / np.abs(np.asarray(c["uz"])))))
            good = d <= 1e-6
            lines.append(f"{'ok    ' if good else 'FAILED'} {name}: {len(res)} reservoirs, largest relative difference "
                         f"{d:.1e}, {time.time() - t0:.0f} s")
            ok &= good
        except CellError as e:
            ok = False
            lines.append(f"FAILED {name}: cell {e.cell}: {e}")
    try:
        out = nb.run_cell(17, dict(default_settings(), CALC_magma=list(nb.ns["MAGMA"])[0], CALC_P_MPa=20.0))
        out += nb.run_cell(16, default_settings())
        lines.append(f"ok     EVo calculator and map: {sum('<img' in p for p in out)} figures")
    except CellError as e:
        ok = False
        lines.append(f"FAILED calculator / map: {e}")
    lines.insert(0, f"Full check: {'PASSED' if ok else 'FAILED'} ({time.time() - t00:.0f} s)")
    _write("\n".join(lines), out_path, "check_all_result.txt")
    return 0 if ok else 1


def smoke(seconds=600):
    """Opens the window, runs the thesis example and closes again (used to test a built program)."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from .runner import Notebook
    from .main_window import MainWindow
    app = QApplication(sys.argv[:1])
    nb = Notebook()
    nb.setup()
    w = MainWindow(nb)
    w.load_example(LAFOSSA, ask=False)
    w.resize(1500, 900)
    w.show()
    state = {"code": 1}

    def finished(*_):
        state["code"] = 0 if w.res_model.rowCount() == 13 else 1
        shots = os.environ.get("MAGMA_SMOKE_SHOTS")          # folder for screenshots of the main tabs
        if shots:
            os.makedirs(shots, exist_ok=True)
            for i, name in ((0, "magmas"), (1, "reservoirs"), (3, "settings"), (4, "results"), (5, "report")):
                w.tabs.setCurrentIndex(i)
                app.processEvents()
                w.grab().save(os.path.join(shots, f"{i}_{name}.png"))
        app.quit()
    QTimer.singleShot(200, lambda: (w.run_all(), w.worker.finished.connect(lambda: QTimer.singleShot(300, finished))))
    QTimer.singleShot(seconds * 1000, app.quit)
    app.exec()
    _write(f"Window test: {'PASSED' if state['code'] == 0 else 'FAILED'}", None, "smoke_result.txt")
    return state["code"]


def main():
    for stream in ("stdout", "stderr"):          # a window program has no console: give prints somewhere to go
        if getattr(sys, stream) is None:
            setattr(sys, stream, open(os.devnull, "w", encoding="utf-8"))
    args = sys.argv[1:]
    for flag, fn in (("--selftest", selftest), ("--check-all", check_all)):
        if flag in args:
            i = args.index(flag)
            out = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("--") else None
            sys.exit(fn(out))
    if "--smoke" in args:
        sys.exit(smoke())
    project = next((a for a in args if a.lower().endswith(".mcu") and os.path.exists(a)), None)

    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QPixmap, QFont
    from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
    from .runner import Notebook
    from .main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("MagmaUplift")
    app.setOrganizationName("MagmaUplift")
    app.setStyle("Fusion")
    f = app.font()
    f.setPointSizeF(max(f.pointSizeF(), 9.5))
    app.setFont(f)
    icon = QIcon(resource(os.path.join("assets", "app.png")))
    app.setWindowIcon(icon)
    splash = QSplashScreen(QPixmap(resource(os.path.join("assets", "splash.png"))))
    splash.show()

    def progress(c, title):
        splash.showMessage(f"Loading … cell {c}: {title}", Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        app.processEvents()
    try:
        nb = Notebook()
        nb.setup(progress)
    except Exception as e:                                  # noqa: BLE001
        splash.close()
        QMessageBox.critical(None, "Start-up failed", f"The calculation code could not be loaded:\n\n{e}")
        sys.exit(1)
    w = MainWindow(nb, icon)
    if project:
        try:
            w.apply_project(json.load(open(project, encoding="utf-8")))
            w.path, w.edited = project, False
            w._title()
        except Exception as e:                              # noqa: BLE001
            QMessageBox.warning(w, "Open", f"{project} could not be read:\n{e}")
            w.load_example(LAFOSSA, ask=False)
    elif not w.restore_session():
        w.load_example(LAFOSSA, ask=False)
    w.show()
    splash.finish(w)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

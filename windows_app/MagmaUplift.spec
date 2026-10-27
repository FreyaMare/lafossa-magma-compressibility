# -*- mode: python ; coding: utf-8 -*-
# PyInstaller recipe of the Windows program (run by build_windows.bat:  pyinstaller --noconfirm --clean MagmaUplift.spec)
import json, sys

# The notebook cells are stored as text and run with exec(), so PyInstaller cannot see what they import.
# hiddenimports.json lists every module they import (recorded by running all test cases).
hidden = json.load(open("hiddenimports.json"))

a = Analysis(
    ["run_app.py"],
    pathex=["."],
    datas=[("assets", "assets"), ("LICENSE.txt", "."),
           ("magma_uplift/selftest_reference.json", "magma_uplift"),
           ("magma_uplift/check_cases.json", "magma_uplift")],
    hiddenimports=hidden,
    excludes=["tkinter", "IPython", "ipywidgets", "ipykernel", "jupyter_client", "jupyter_core", "notebook",
              "nbformat", "PyQt5", "PyQt6", "PySide2", "pytest", "sphinx", "numpy.f2py.tests"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="MagmaUplift",
    console=False,                 # a window program (no black console window)
    icon="assets/app.ico",
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="MagmaUplift")

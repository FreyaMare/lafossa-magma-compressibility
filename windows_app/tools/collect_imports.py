"""Write hiddenimports.json: every module the notebook cells import at run time.

The cells are stored as text and run with exec(), so PyInstaller cannot see their imports. This script runs
the full check (all volcanoes, every EVo mode, calculator, map) in a fresh Python and records sys.modules.
Run it from the windows_app folder after changing the notebook or the package versions:
    python tools/collect_imports.py
"""
import json
import pathlib
import subprocess
import sys
import tempfile

APP = pathlib.Path(__file__).resolve().parents[1]
CODE = r'''
import sys, json, importlib.util
sys.path.insert(0, {app!r})
from magma_uplift.app import check_all
check_all({tmp!r})
skip = {{"evo_local", "dmodels_local", "magma_uplift", "IPython", "ipywidgets", "__main__", "__mp_main__",
        "PIL", "nbformat", "jupyter_core", "jupyter_client", "ipykernel", "tornado", "zmq", "setuptools", "pip",
        "PyInstaller", "markdown", "traitlets", "charset_normalizer", "fcntl", "grp", "pwd", "posix", "termios",
        "resource", "pty", "tty", "syslog", "readline", "curses", "posixpath", "crypt", "nis", "spwd", "encodings"}}
out = []
for name in sorted(sys.modules):
    top = name.split(".")[0]
    if top in skip or top.startswith("_") or sys.modules[name] is None or name == "collections.abc":
        continue
    try:
        if importlib.util.find_spec(name) is None:
            continue
    except Exception:
        continue
    out.append(name)
json.dump(out, open({out!r}, "w"), indent=0)
print(len(out), "modules")
'''
with tempfile.TemporaryDirectory() as d:
    code = CODE.format(app=str(APP), tmp=str(pathlib.Path(d) / "check.txt"), out=str(APP / "hiddenimports.json"))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:])

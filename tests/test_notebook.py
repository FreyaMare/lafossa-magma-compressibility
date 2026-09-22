"""Execute the notebook end to end and check its numbers against the thesis results.

Run with:  pytest -v tests/
Set LAFOSSA_EVO_DIR=/path/to/EVo to reuse an existing EVo checkout instead of cloning.
"""
import json
import os
import pathlib

import nbformat
import numpy as np
import pytest
from nbclient import NotebookClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "LaFossa_Vulcano_uplift_EVo.ipynb"

# Reference values (Scenario A, thesis Chapter 5), row order of `res`:
# Mogi 2/5/12 km, Yang 2021, Penny a=0.5 (2/5/12), a=1 (2/5/12), a=2 (2/5/12)
REF_RV = [2.600000, 2.466667, 2.333333, 11.939244, 3.381570, 22.988474, 200.992341,
          1.284984, 3.738892, 25.992391, 1.029156, 1.334071, 4.117585]
REF_UZ0 = [229.5504, 38.71337, 7.105131, 42.19532, 332.2557, 8.225651, 0.164682,
           744.7670, 49.11771, 1.266856, 598.4658, 123.5135, 7.835061]
REF_PSAT = {"RHYOLITE": 29.8, "TRACHYTE": 53.7, "LATITE": 55.9}

PROBE = """
import json
print("LAFOSSA_JSON" + json.dumps({
    "rV": res.rV.tolist(),
    "uz0": res.uz3_0km_mm.tolist(),
    "phi": res.phi.tolist(),
    "engine": res.engine.tolist(),
    "psat": {r.chamber: float(r.P_sat_MPa) for _, r in res.iterrows()},
}))
"""


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    work = tmp_path_factory.mktemp("run")
    evo_dir = os.environ.get("LAFOSSA_EVO_DIR")
    if evo_dir:
        (work / "EVo").symlink_to(pathlib.Path(evo_dir).resolve())
    before = {p.name for p in work.iterdir()}

    nb = nbformat.read(NOTEBOOK, as_version=4)
    nb.cells.append(nbformat.v4.new_code_cell(PROBE))
    NotebookClient(nb, timeout=1200, kernel_name="python3",
                   resources={"metadata": {"path": str(work)}}).execute()

    errors = [o for c in nb.cells if c.cell_type == "code" for o in c.outputs
              if o.output_type == "error"]
    text = "".join(o.get("text", "") for o in nb.cells[-1].outputs)
    data = json.loads(text.split("LAFOSSA_JSON", 1)[1])
    after = {p.name for p in work.iterdir()}
    return dict(nb=nb, errors=errors, data=data, new_files=after - before - {"EVo"})


def test_runs_without_errors(run):
    assert not run["errors"], run["errors"]


def test_evo_used_everywhere(run):
    assert all(e.startswith("EVo") for e in run["data"]["engine"]), run["data"]["engine"]


def test_partitioning_factor(run):
    np.testing.assert_allclose(run["data"]["rV"], REF_RV, rtol=1e-5)


def test_central_uplift(run):
    np.testing.assert_allclose(run["data"]["uz0"], REF_UZ0, rtol=1e-5)


def test_saturation_state(run):
    phi = run["data"]["phi"]
    assert abs(phi[3] - 0.15541) < 1e-3          # shallow rhyolite is gas-bearing
    assert all(p == 0 for i, p in enumerate(phi) if i != 3)
    for comp, ref in REF_PSAT.items():
        assert abs(run["data"]["psat"][comp] - ref) < 0.2


def test_outputs_are_on_page_only(run):
    assert not run["new_files"], f"notebook wrote files: {run['new_files']}"
    n_png = sum("image/png" in o.get("data", {}) for c in run["nb"].cells
                if c.cell_type == "code" for o in c.outputs)
    assert n_png == 3

"""CI checks for the metaclasses topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"meta_{name}", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "type(A) is type: True" in out
    assert "'json': 'JsonPlugin'" in out and "'csvplugin': 'CsvPlugin'" in out
    assert "subclassing Config -> Config is sealed" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_metaclass_conflict():
    scen = _load("scenarios")
    assert scen.s1_build() == ["Job"]
    assert "metaclass conflict" in scen.s1_break()
    assert scen.s1_fix() == ["Job"]


def test_s2_kwargs_not_forwarded():
    scen = _load("scenarios")
    assert scen.s2_build() == {"/": "Home", "/about": "About"}
    assert "unexpected keyword argument" in scen.s2_break()
    assert scen.s2_fix() == {"/": "Home"}


def test_s3_abstract_intermediates():
    scen = _load("scenarios")
    assert scen.s3_build() == ["Square"]
    assert scen.s3_break() == ["Polygon", "Square"]
    assert scen.s3_fix() == ["Square"]


def test_s4_metaclass_as_base():
    scen = _load("scenarios")
    assert scen.s4_build() == "made-by-Meta"
    assert "TypeError" in scen.s4_break()
    assert scen.s4_fix() == "made-by-Meta"

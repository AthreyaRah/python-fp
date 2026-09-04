"""CI checks for the inheritance & MRO topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"mro_{name}", HERE / f"{name}.py")
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
    assert "D.__mro__: ['D', 'B', 'C', 'A', 'object']" in out
    assert "D().who(): D -> B -> C -> A" in out
    assert "init trace: ['B', 'C', 'A']" in out
    assert "isinstance(d, (B, C)): True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_missing_super_init():
    scen = _load("scenarios")
    assert scen.s1_build() == "Rex knows ['sit']"
    assert "AttributeError" in scen.s1_break()
    assert scen.s1_fix() == "Rex knows ['sit']"


def test_s2_hardcoded_base_call():
    scen = _load("scenarios")
    assert scen.s2_build() == ["Child", "Left", "Right", "Base"]
    assert scen.s2_break().count("Base") == 2
    assert scen.s2_fix() == ["Child", "Left", "Right", "Base"]


def test_s3_inconsistent_mro():
    scen = _load("scenarios")
    assert scen.s3_build()[:2] == ["R", "P"]
    assert "TypeError" in scen.s3_break()
    assert scen.s3_fix()[:2] == ["R", "P"]


def test_s4_method_from_init():
    scen = _load("scenarios")
    assert scen.s4_build() == 6
    assert "AttributeError" in scen.s4_break()
    assert scen.s4_fix() == 12

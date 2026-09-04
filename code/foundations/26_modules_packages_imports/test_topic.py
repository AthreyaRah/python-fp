"""CI checks for the modules & packages topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"mods_{name}", HERE / f"{name}.py")
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
    assert "shapes.circle_area(2) = 12.566" in out
    assert "shapes.square.area(4) = 16" in out
    assert "shapes.__all__ = ['circle_area', 'square_area']" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_circular_import():
    scen = _load("scenarios")
    assert scen.s1_build() == "A calls B"
    assert "partially initialized" in scen.s1_break()
    assert scen.s1_fix() == "A calls B"


def test_s2_relative_import_script():
    scen = _load("scenarios")
    assert scen.s2_build() == "hi"
    assert "attempted relative import" in scen.s2_break()
    assert scen.s2_fix() == "hi"


def test_s3_star_import():
    scen = _load("scenarios")
    assert scen.s3_build() == ["VERSION", "public_api"]
    assert scen.s3_break() is True        # os and sys leaked
    assert scen.s3_fix() == ["VERSION", "public_api"]


def test_s4_import_binds_top():
    scen = _load("scenarios")
    assert scen.s4_build() == 15
    assert "NameError" in scen.s4_break()
    assert scen.s4_fix() == 15

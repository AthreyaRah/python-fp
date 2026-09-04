"""CI checks for the dataclasses & __slots__ topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    mod_name = f"dc_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "repr : Point(x=1, y=2, label='origin')" in out
    assert "independent lists: ['x'] []" in out
    assert "mutating frozen -> FrozenInstanceError" in out
    assert "__post_init__ derived fahrenheit: 77.0" in out
    assert "Vec3 has __dict__? False" in out
    assert "typo caught by slots:" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_mutable_default():
    scen = _load("scenarios")
    assert scen.s1_build() == (["apple"], [])
    assert "ValueError" in scen.s1_break()
    assert scen.s1_fix() == (["apple"], [])


def test_s2_frozen():
    scen = _load("scenarios")
    assert scen.s2_build() == scen.Money(750)
    assert "FrozenInstanceError" in scen.s2_break()
    assert scen.s2_fix() == scen.Money(750)


def test_s3_unhashable():
    scen = _load("scenarios")
    assert scen.s3_build() == 2
    assert "unhashable" in scen.s3_break()
    assert scen.s3_fix() == 2


def test_s4_slots_typo():
    scen = _load("scenarios")
    assert scen.s4_build() == "caught: AttributeError"
    assert scen.s4_break() == (3, True)      # typo silently created a dead attr
    assert scen.s4_fix() == "retries=5"

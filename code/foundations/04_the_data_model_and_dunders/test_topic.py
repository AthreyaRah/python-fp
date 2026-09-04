"""CI checks for the data model & dunders topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    mod_name = f"dm_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod  # dataclass() needs the module in sys.modules
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "a + b        -> Vector(4.0, 6.0)" in out
    assert "sum([a, b])  -> Vector(4.0, 6.0)" in out
    assert "list(a)      -> [1.0, 2.0]" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_eq_without_hash():
    scen = _load("scenarios")
    assert scen.s1_build() == 2
    assert "unhashable" in scen.s1_break()
    assert scen.s1_fix() == 2


def test_s2_str_without_repr():
    scen = _load("scenarios")
    assert "Money(cents=150)" in scen.s2_build()
    assert scen.s2_break() is True  # container shows the useless default repr
    assert "$1.50" in scen.s2_fix()


def test_s3_add_negotiation():
    scen = _load("scenarios")
    assert repr(scen.s3_build()) == "Weight(17)"
    assert "TypeError" in scen.s3_break()
    assert repr(scen.s3_fix()) == "Weight(15)"


def test_s4_hash_mutation():
    scen = _load("scenarios")
    assert scen.s4_build() is True
    assert scen.s4_break() is False  # object lost in the set after mutation
    assert scen.s4_fix() is True

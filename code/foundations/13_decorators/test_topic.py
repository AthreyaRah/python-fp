"""CI checks for the decorators topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"deco_{name}", HERE / f"{name}.py")
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
    assert "slow_square(9) = 81" in out
    assert "name = slow_square | doc = Square n, slowly." in out
    assert "flaky() -> ok on attempt 3" in out
    assert "decorator ran for announced (at def time" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_wraps():
    scen = _load("scenarios")
    assert scen.s1_build() == ("greet", "Say hi.")
    assert scen.s1_break() == ("wrapper", None)
    assert scen.s1_fix() == ("greet", "Say hi.")


def test_s2_factory_not_called():
    scen = _load("scenarios")
    assert scen.s2_build() == "abc"
    assert "TypeError" in scen.s2_break()
    assert scen.s2_fix() == "abc"


def test_s3_decorator_returns_none():
    scen = _load("scenarios")
    assert scen.s3_build() == 42
    assert "NoneType" in scen.s3_break()
    assert scen.s3_fix() == 42


def test_s4_stacking_order():
    scen = _load("scenarios")
    val, cache = scen.s4_build()
    assert val == 12.0 and cache == {"book": 12.0}
    val, cache = scen.s4_break()
    assert val == 12.0 and cache == {"book": 10.0}   # cached the pre-tax value
    val, cache = scen.s4_fix()
    assert val == 12.0 and cache == {"book": 12.0}

"""CI checks for the generators topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"gen_{name}", HERE / f"{name}.py")
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
    assert "body has NOT run yet" in out
    assert "flatten nested list: [1, 2, 3, 4, 5, 6]" in out
    assert "pipeline running totals: [12, 19, 24]" in out
    assert "generator's return value: 3" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_deferred_validation():
    scen = _load("scenarios")
    assert "call time" in scen.s1_build()
    assert "only on first use" in scen.s1_break()
    assert "call time" in scen.s1_fix()


def test_s2_single_pass():
    scen = _load("scenarios")
    a, b = scen.s2_build()
    assert a == [0, 1, 4, 9, 16] and b == [0, 1, 4, 9, 16]
    first, second = scen.s2_break()
    assert first == [0, 1, 4, 9, 16] and second == []
    c, d = scen.s2_fix()
    assert c == d == [0, 1, 4, 9, 16]


def test_s3_cleanup_on_break():
    scen = _load("scenarios")
    assert scen.s3_build() == ["cleaned up"]
    assert scen.s3_break() == []            # finally not run yet
    assert scen.s3_fix() == ["cleaned up"]


def test_s4_return_value():
    scen = _load("scenarios")
    produced, count = scen.s4_build()
    assert produced == [10, 20, 30] and count == 3
    assert scen.s4_break() == 30            # last yielded value, not the return
    assert scen.s4_fix() == 3

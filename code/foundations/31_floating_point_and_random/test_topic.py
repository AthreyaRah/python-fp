"""CI checks for the floating point & random topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"fp_{name}", HERE / f"{name}.py")
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
    assert "0.1 + 0.2 == 0.3?    = False" in out
    assert "math.isclose(...)    = True" in out
    assert "manual += loop       = 2.0" in out
    assert "math.fsum            = 3.0" in out
    assert "round(0.5), round(1.5), round(2.5): 0 2 2" in out
    assert out.count("Random(42)") == 2


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_accumulated_error():
    scen = _load("scenarios")
    assert scen.s1_build() == 3.0
    assert scen.s1_break() == 2.0
    assert scen.s1_fix() == 3.0


def test_s2_shared_global_random():
    scen = _load("scenarios")
    assert len(scen.s2_build()) == 4
    assert scen.s2_break() is True     # interference changed the sequence
    assert scen.s2_fix() is True


def test_s3_sample_too_large():
    scen = _load("scenarios")
    assert scen.s3_build() == 10
    assert "ValueError" in scen.s3_break()
    assert scen.s3_fix() == 10


def test_s4_bankers_rounding():
    scen = _load("scenarios")
    assert scen.s4_build() == "3"
    assert scen.s4_break() == (0, 2, 2)
    assert scen.s4_fix() == [1, 2, 3]

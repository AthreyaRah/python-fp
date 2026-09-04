"""CI checks for the GIL / races topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"gil_{name}", HERE / f"{name}.py")
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
    assert "Bytecode for `counter += 1`" in out
    assert "safe_counter:" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_counter_race():
    scen = _load("scenarios")
    assert scen.s1_build() == scen.THREADS * scen.N
    got, expected = scen.s1_break()
    assert got < expected
    assert scen.s1_fix() == (expected, expected)


def test_s2_check_then_act():
    scen = _load("scenarios")
    assert scen.s2_build() == 1
    assert scen.s2_break() > 1
    assert scen.s2_fix() == 1


def test_s3_deadlock():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert scen.s3_break() is True  # deadlock detected via timeout
    assert scen.s3_fix() is True


def test_s4_atomicity():
    scen = _load("scenarios")
    built, expected = scen.s4_build()
    assert built == expected  # append is atomic
    got, expected = scen.s4_break()
    assert got < expected  # += is not
    assert scen.s4_fix() == (expected, expected)

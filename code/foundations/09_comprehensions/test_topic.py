"""CI checks for the comprehensions topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"comp_{name}", HERE / f"{name}.py")
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
    assert "list : [0, 1, 4, 9, 16, 25]" in out
    assert "flatten: [1, 2, 3, 4, 5, 6]" in out
    assert "is 'v' defined out here? False" in out
    assert "generator expression   :" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_generator_single_pass():
    scen = _load("scenarios")
    assert scen.s1_build() == (30, 16)
    first, second = scen.s1_break()
    assert first == [0, 1, 4, 9, 16] and second == []
    assert scen.s1_fix() == (30, 16)


def test_s2_closure_capture():
    scen = _load("scenarios")
    assert scen.s2_build() == [0, 1, 2, 3]
    assert scen.s2_break() == [3, 3, 3, 3]
    assert scen.s2_fix() == [0, 1, 2, 3]


def test_s3_clause_order():
    scen = _load("scenarios")
    assert scen.s3_build() == [1, 2, 3, 4, 5, 6]
    assert "NameError" in scen.s3_break()
    assert scen.s3_fix() == [1, 2, 3, 4]


def test_s4_short_circuit():
    scen = _load("scenarios")
    assert scen.s4_build() == (True, 5)     # genexp: stopped after 5 checks
    assert scen.s4_break() == (True, 100)   # list comp: all 100 ran
    assert scen.s4_fix() == (True, 5)

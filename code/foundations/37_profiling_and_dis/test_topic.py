"""CI checks for the profiling topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    mod_name = f"prof_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod   # timeit setup does `from __main__ import ...` fallback
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "'x in set'" in out and "x faster)" in out
    assert "block took" in out
    assert "cProfile top (by tottime): " in out and "has_dupes" in out
    assert "bytecode for `return x + 1`" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_setup_runs_once():
    scen = _load("scenarios")
    assert scen.s1_build() == 1
    assert scen.s1_break() == 50    # the builder ran every iteration
    assert scen.s1_fix() == 1


def test_s2_timeit_namespace():
    scen = _load("scenarios")
    assert scen.s2_build() >= 0
    assert "NameError" in scen.s2_break()
    assert scen.s2_fix() >= 0


def test_s3_timeit_disables_gc():
    scen = _load("scenarios")
    assert scen.s3_build() == [True, True, True]
    assert scen.s3_break() == [False, False, False]   # GC off during measurement
    assert scen.s3_fix() == [True, True, True]


def test_s4_micro_vs_algorithm():
    scen = _load("scenarios")
    slow_ops, fast_ops = scen.s4_build()
    assert slow_ops > 50_000 and fast_ops < 500
    assert scen.s4_break() is True     # micro version stays O(n^2)
    assert scen.s4_fix() is True

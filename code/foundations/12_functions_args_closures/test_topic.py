"""CI checks for the functions & closures topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"fn_{name}", HERE / f"{name}.py")
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
    assert "add10(5) = 15" in out
    assert "free vars: ('n',)" in out
    assert "counter: 1 2 3" in out
    assert "'args': (3, 4)" in out and "'kwargs': {'extra': 6}" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_late_binding():
    scen = _load("scenarios")
    assert scen.s1_build() == [0, 10, 20, 30]
    assert scen.s1_break() == [30, 30, 30, 30]
    assert scen.s1_fix() == [0, 10, 20, 30]


def test_s2_nonlocal():
    scen = _load("scenarios")
    assert scen.s2_build() == 15
    assert "UnboundLocalError" in scen.s2_break()
    assert scen.s2_fix() == 15


def test_s3_kwargs_typo():
    scen = _load("scenarios")
    assert scen.s3_build() == 15.0
    assert scen.s3_break() == 3.0     # typo ignored, default used
    assert scen.s3_fix() == 15.0


def test_s4_ambiguous_positional():
    scen = _load("scenarios")
    assert scen.s4_build() == (1920, 1080)
    assert scen.s4_break() == (1080, 1920)   # silently swapped
    assert scen.s4_fix() == (1920, 1080)

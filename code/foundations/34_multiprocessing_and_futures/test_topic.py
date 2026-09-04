"""CI checks for the multiprocessing & futures topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

HERE = Path(__file__).parent
_SKIP = pytest.mark.skipif(sys.platform == "win32", reason="scenarios use the 'fork' context")


def _load(name: str):
    mod_name = f"mpf_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@_SKIP
def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "serial   : [1, 4, 9, 16]" in out
    assert "processes: [1, 4, 9, 16]" in out
    assert "worker exception re-raised on .result():" in out and "division by zero" in out


@_SKIP
def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


@_SKIP
def test_s1_threads_vs_processes():
    scen = _load("scenarios")
    assert scen.s1_build() > 0
    assert scen.s1_break() is True     # processes clearly faster for CPU work
    assert scen.s1_fix() > 0


@_SKIP
def test_s2_unpicklable():
    scen = _load("scenarios")
    assert scen.s2_build() == [1, 4, 9, 16]
    assert "Error" in scen.s2_break()
    assert scen.s2_fix() == [1, 4, 9]


@_SKIP
def test_s3_no_shared_state():
    scen = _load("scenarios")
    assert scen.s3_build() == 55
    assert scen.s3_break() == 0        # parent's global untouched
    assert scen.s3_fix() == 10


@_SKIP
def test_s4_unretrieved_exception():
    scen = _load("scenarios")
    assert scen.s4_build() == "caught: worker failed"
    assert scen.s4_break() == "nothing"       # exception silently swallowed
    assert scen.s4_fix() == "3 errors surfaced"

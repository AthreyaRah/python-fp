"""CI checks for the testing-with-pytest topic (a test suite about test suites)."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"tst_{name}", HERE / f"{name}.py")
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
    assert "passed" in out and "failed" not in out.split("result:")[-1]


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_shared_state():
    scen = _load("scenarios")
    assert scen.s1_build() == (2, 0)
    assert scen.s1_break() == (1, 1)     # test_b fails after test_a
    assert scen.s1_fix() == (2, 0)


def test_s2_float_compare():
    scen = _load("scenarios")
    assert scen.s2_build() == (1, 0)
    assert scen.s2_break() == (0, 1)
    assert scen.s2_fix() == (1, 0)


def test_s3_fixture_teardown():
    scen = _load("scenarios")
    assert scen.s3_build() == (2, 0)
    assert scen.s3_break() == (1, 1)     # teardown assertion fails
    assert scen.s3_fix() == (2, 0)


def test_s4_no_assertion():
    scen = _load("scenarios")
    assert scen.s4_build() == (1, 0)
    assert scen.s4_break() == (1, 0)     # GREEN despite the bug
    assert scen.s4_fix() == (0, 1)       # assertion catches it

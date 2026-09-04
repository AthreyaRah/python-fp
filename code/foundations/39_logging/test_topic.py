"""CI checks for the logging topic."""

from __future__ import annotations

import importlib.util
import io
import logging
from contextlib import redirect_stdout
from pathlib import Path

import pytest

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"log_{name}", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _restore_logging():
    root = logging.getLogger()
    saved = list(root.handlers), root.level
    yield
    root.handlers[:], root.level = list(saved[0]), saved[1]


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "demo INFO app started" in out
    assert "demo WARNING disk at 91%" in out
    assert "contains 'Traceback': True" in out
    assert "Expensive.__str__ calls at INFO level: 0" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_basicconfig_late():
    scen = _load("scenarios")
    assert scen.s1_build() is True
    assert scen.s1_break() is True      # DEBUG stayed hidden
    assert scen.s1_fix() is True


def test_s2_fstring_in_log():
    scen = _load("scenarios")
    assert scen.s2_build() == 0
    assert scen.s2_break() == 1         # f-string rendered a dropped message
    assert scen.s2_fix() == 0


def test_s3_exception_traceback():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert scen.s3_break() is True      # no traceback in the log
    assert scen.s3_fix() is True


def test_s4_duplicate_handlers():
    scen = _load("scenarios")
    assert scen.s4_build() == 3
    assert scen.s4_break() == 6         # handlers stacked up
    assert scen.s4_fix() == 3

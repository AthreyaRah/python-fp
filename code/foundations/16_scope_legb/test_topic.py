"""CI checks for the scope & namespaces topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"scope_{name}", HERE / f"{name}.py")
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
    assert "inner sees: local" in out
    assert "inner_reads_enclosing sees: enclosing" in out
    assert "after global_needs_declaring: VALUE = reassigned via global" in out
    assert "timeout=30" in out
    assert "is 'n' visible here? False" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_shadow_builtin():
    scen = _load("scenarios")
    assert scen.s1_build() == 60
    assert "not callable" in scen.s1_break()
    assert scen.s1_fix() == 63


def test_s2_class_body_scope():
    scen = _load("scenarios")
    assert scen.s2_build() == 30
    assert "NameError" in scen.s2_break()
    assert scen.s2_fix() == 30


def test_s3_reassigning_global():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert scen.s3_break() == 0     # UnboundLocalError; module global untouched
    assert scen.s3_fix() == 2


def test_s4_comprehension_scope():
    scen = _load("scenarios")
    assert scen.s4_build() == 2
    assert "NameError" in scen.s4_break()
    assert scen.s4_fix() == 2

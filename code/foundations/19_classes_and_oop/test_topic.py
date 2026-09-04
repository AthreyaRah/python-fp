"""CI checks for the classes & OOP topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"oop_{name}", HERE / f"{name}.py")
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
    assert "'deposit' in instance dict? False | in class dict? True" in out
    assert "after two deposits of 25: 100" in out
    assert "from_record: Account(owner='Cy', balance=300)" in out
    assert "set balance to -5 -> balance cannot be negative" in out
    assert "Account.open_count = 4" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_class_attr_shadowing():
    scen = _load("scenarios")
    assert scen.s1_build() == (3, 3)
    assert scen.s1_break() == (1, 0)     # instance shadows; class counter stuck
    assert scen.s1_fix() == (3, 3)


def test_s2_missing_self():
    scen = _load("scenarios")
    assert scen.s2_build() == 42
    assert "TypeError" in scen.s2_break()
    assert scen.s2_fix() == 42


def test_s3_readonly_property():
    scen = _load("scenarios")
    assert scen.s3_build() == "Grace/Hopper"
    assert "AttributeError" in scen.s3_break()
    assert scen.s3_fix() == "Grace Hopper"


def test_s4_init_returns():
    scen = _load("scenarios")
    assert scen.s4_build() == 3
    assert "TypeError" in scen.s4_break()
    assert scen.s4_fix() == (0, 0)

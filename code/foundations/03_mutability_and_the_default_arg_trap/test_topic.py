"""CI checks for the mutability topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"mut_{name}", HERE / f"{name}.py")
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
    assert "str  += : same object? False" in out
    assert "list += : same object? True" in out
    assert "bad('a'): ['a']\n" in out
    assert "bad('b'): ['a', 'b']\n" in out
    assert "bad('c'): ['a', 'b', 'c']\n" in out
    assert "good('a'): ['a']\ngood('b'): ['b']\n" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_iadd_in_tuple():
    scen = _load("scenarios")
    assert scen.s1_build() == (["a", "b", "c"], "meta")
    assert scen.s1_break() == (["a", "b", "c"], "meta")  # mutated despite TypeError
    assert scen.s1_fix() == (["a", "b", "c"], "meta")


def test_s2_mutable_default():
    scen = _load("scenarios")
    assert scen.s2_build() == [{"a": 1}, {"b": 2}]
    assert scen.s2_break()[0] == {"a": 1, "b": 2, "c": 3}
    assert scen.s2_fix() is True


def test_s3_unhashable_key():
    scen = _load("scenarios")
    assert scen.s3_build() == {(0, 0): 2, (1, 2): 1}
    assert "unhashable" in scen.s3_break()
    assert scen.s3_fix() == {(0, 0): 1, frozenset({"a", "b"}): 2}


def test_s4_class_attribute():
    scen = _load("scenarios")
    assert scen.s4_build() == (["apple"], [])
    a_items, b_items, shared = scen.s4_break()
    assert b_items == ["apple"] and shared is True
    assert scen.s4_fix() == (["apple"], [])

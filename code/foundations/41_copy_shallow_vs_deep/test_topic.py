"""CI checks for the copy: shallow vs deep topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"cp_{name}", HERE / f"{name}.py")
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
    assert "shallow: ['a', 'b', 'c']" in out
    assert "deep   : ['a', 'b']" in out
    assert "cycle deep-copied: True | b is not a: True" in out
    assert "internal sharing kept: True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_shallow_nested():
    scen = _load("scenarios")
    assert scen.s1_build() == (["viewer"], {"rate": 10})
    assert scen.s1_break() == (["viewer", "editor"], {"rate": 100})
    assert scen.s1_fix() == (["viewer"], {"rate": 10})


def test_s2_uncopyable_resource():
    scen = _load("scenarios")
    assert scen.s2_build() is True
    assert "TypeError" in scen.s2_break()
    assert scen.s2_fix() is True


def test_s3_memo_per_call():
    scen = _load("scenarios")
    assert scen.s3_build() is True     # linked inside one deepcopy
    assert scen.s3_break() is True     # separate calls -> not linked
    assert scen.s3_fix() is True


def test_s4_copy_shares_attrs():
    scen = _load("scenarios")
    assert scen.s4_build() == (["apple"], ["apple", "banana"])
    a_items, b_items, shared = scen.s4_break()
    assert a_items == ["apple", "banana"] and shared is True
    assert scen.s4_fix() == (["apple"], ["apple", "banana"])

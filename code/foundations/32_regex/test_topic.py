"""CI checks for the regex topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"re_{name}", HERE / f"{name}.py")
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
    assert "match(r'\\d+', ...):    None" in out
    assert "search(r'\\d+', ...):   123" in out
    assert "greedy <.*> : ['<a><b>']" in out
    assert "lazy   <.*?>: ['<a>', '<b>']" in out
    assert "sub with a function: prices: 20, 40, 60" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_match_anchors():
    scen = _load("scenarios")
    assert scen.s1_build() == "123"
    assert scen.s1_break() is None
    assert scen.s1_fix() == "123"


def test_s2_catastrophic_backtracking():
    scen = _load("scenarios")
    assert scen.s2_build() < 0.05
    assert scen.s2_break() is True     # evil pattern hugely slower than safe one
    assert scen.s2_fix() < 0.05        # linear even at 1000 chars


def test_s3_raw_string():
    scen = _load("scenarios")
    assert scen.s3_build() == ["cat"]
    assert scen.s3_break() == []       # \b was a backspace char
    assert scen.s3_fix() == ["cat"]


def test_s4_greedy():
    scen = _load("scenarios")
    assert scen.s4_build() == ['"alpha"', '"beta"']
    assert scen.s4_break() == ['"alpha" and "beta"']
    assert scen.s4_fix() == ['"alpha"', '"beta"']

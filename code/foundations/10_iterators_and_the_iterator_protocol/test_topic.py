"""CI checks for the iterators topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"iter_{name}", HERE / f"{name}.py")
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
    assert "StopIteration: done" in out
    assert "list is its own iterator? False" in out
    assert "an iterator is its own iterator? True" in out
    assert "Countdown(4): [4, 3, 2, 1]" in out
    assert "iter(callable, sentinel): [0, 1, 2, 3, 4]" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_consumed_iterator():
    scen = _load("scenarios")
    header, data = scen.s1_build()
    assert header == ("id", "name") and len(data) == 2
    assert scen.s1_break() == (3, 0)
    assert scen.s1_fix() == (3, 3)


def test_s2_iter_returns_self():
    scen = _load("scenarios")
    assert len(scen.s2_build()) == 9
    assert scen.s2_break() == [(1, 2), (1, 3)]
    assert len(scen.s2_fix()) == 9


def test_s3_leaked_stopiteration():
    scen = _load("scenarios")
    assert scen.s3_build() == [3, 7]
    assert "RuntimeError" in scen.s3_break()
    assert scen.s3_fix() == [3]


def test_s4_peek_consumes():
    scen = _load("scenarios")
    assert scen.s4_build() == [10, 20, 30, 40]
    assert scen.s4_break() == [20, 30, 40]
    assert scen.s4_fix() == [10, 20, 30, 40]

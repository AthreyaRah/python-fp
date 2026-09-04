"""CI checks for the memory model & weakref topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"mem_{name}", HERE / f"{name}.py")
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
    assert "adding 2 references raised the count by: 2" in out
    assert "with gc off, cycle still alive after del: True" in out
    assert "after gc.collect(), alive: False" in out
    assert "after del,   ref() -> None" in out
    assert "gone once nothing else refers to it: False" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_reference_cycle():
    scen = _load("scenarios")
    assert scen.s1_build() is True
    alive_before_gc, freed_after_gc = scen.s1_break()
    assert alive_before_gc is True and freed_after_gc is True
    assert scen.s1_fix() is True


def test_s2_weakref_unreferenced():
    scen = _load("scenarios")
    assert scen.s2_build() == "Parent"
    assert scen.s2_break() is None
    assert scen.s2_fix() == "Parent"


def test_s3_dict_cache_leak():
    scen = _load("scenarios")
    assert scen.s3_build() <= 5        # weak keys let the Parents go
    assert scen.s3_break() == 100      # plain dict pins all 100
    assert scen.s3_fix() <= 5


def test_s4_del_cleanup():
    scen = _load("scenarios")
    assert scen.s4_build() == ["explicit:2"]
    assert scen.s4_break() == []       # __del__ deferred, nothing flushed yet
    assert scen.s4_fix() == ["ctx:2"]

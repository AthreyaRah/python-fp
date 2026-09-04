"""CI checks for the execution & import model topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"execmodel_{name}", HERE / f"{name}.py")
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
    assert "[greeter.py body is running]" in out
    assert out.count("[greeter.py body is running]") == 1  # imported once
    assert "greet('world') -> hello, world" in out


def test_scenarios_run():
    scen = _load("scenarios")
    real_tabnanny = sys.modules.get("tabnanny")
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            scen.main()
        assert buf.getvalue().count("🔨 build") == 4
    finally:
        if real_tabnanny is not None:
            sys.modules["tabnanny"] = real_tabnanny


def test_s1_module_body_runs_once():
    scen = _load("scenarios")
    assert scen.s1_build() == 99          # reload re-ran the body
    assert scen.s1_break() == 1           # plain re-import: stale cached value
    assert scen.s1_fix() == 2


def test_s2_main_guard():
    scen = _load("scenarios")
    assert scen.s2_build() == []          # import did not run main()
    assert scen.s2_break() == ["did work"]  # no guard: side effect on import
    assert scen.s2_fix() == []


def test_s3_import_time_work():
    scen = _load("scenarios")
    assert scen.s3_build() == sum(i * i for i in range(10_000))
    did_work, table = scen.s3_break()
    assert did_work is True and table == sum(i * i for i in range(10_000))
    assert scen.s3_fix() == sum(i * i for i in range(10_000))


def test_s4_stdlib_shadowing():
    scen = _load("scenarios")
    real_tabnanny = sys.modules.get("tabnanny")
    try:
        assert scen.s4_build() is True
        assert "IS_THE_REAL_STDLIB_MODULE=False" in scen.s4_break()
        assert scen.s4_fix() is True
    finally:
        scen._restore_tabnanny()
        if real_tabnanny is not None:
            sys.modules["tabnanny"] = real_tabnanny

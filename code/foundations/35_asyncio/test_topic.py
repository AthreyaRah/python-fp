"""CI checks for the asyncio topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"aio_{name}", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    import asyncio

    buf = io.StringIO()
    with redirect_stdout(buf):
        asyncio.run(demo.main())
    out = buf.getvalue()
    assert "sequential awaits : 0.3" in out
    assert "asyncio.gather    : 0.1" in out
    assert "TaskGroup results : ['t0 (0.05s)', 't1 (0.05s)', 't2 (0.05s)', 't3 (0.05s)']" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_never_awaited():
    scen = _load("scenarios")
    assert scen.s1_build() == "done"
    assert scen.s1_break() == "never ran"
    assert scen.s1_fix() == "ran"


def test_s2_blocking_freezes_loop():
    scen = _load("scenarios")
    assert scen.s2_build() < 0.2
    assert scen.s2_break() is True     # 5 blocking sleeps ran serially
    assert scen.s2_fix() is True


def test_s3_sequential_awaits():
    scen = _load("scenarios")
    assert scen.s3_build() < 0.2
    assert scen.s3_break() is True     # ~0.3s
    assert scen.s3_fix() is True


def test_s4_fire_and_forget():
    scen = _load("scenarios")
    assert scen.s4_build() == ["t0", "t1", "t2"]
    assert scen.s4_break() == "main returned, slow done: False"
    assert scen.s4_fix() == "main returned, slow done: True"

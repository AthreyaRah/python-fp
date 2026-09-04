"""CI checks for the functools topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"ft_{name}", HERE / f"{name}.py")
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
    assert "fib(30) = 832040" in out
    assert "from_hex('ff') = 255" in out
    assert "describe: int 10 (even)" in out
    assert "second access: 10 (no recompute)" in out
    assert out.count("(computing total...)") == 1
    assert "v1 < v2: True | v1 >= v2: False" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_hashable_args():
    scen = _load("scenarios")
    assert scen.s1_build() == 28
    assert "unhashable" in scen.s1_break()
    assert scen.s1_fix() == 14


def test_s2_cached_property_stale():
    scen = _load("scenarios")
    assert scen.s2_build() == 10
    assert scen.s2_break() == 6      # stale cached value
    assert scen.s2_fix() == 10


def test_s3_reduce_empty():
    scen = _load("scenarios")
    assert scen.s3_build() == 0
    assert "TypeError" in scen.s3_break()
    assert scen.s3_fix() == 60


def test_s4_partial_positional():
    scen = _load("scenarios")
    assert scen.s4_build() == 255
    assert "TypeError" in scen.s4_break()
    assert scen.s4_fix() == 255

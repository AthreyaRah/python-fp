"""CI checks for the idioms & anti-patterns topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"idi_{name}", HERE / f"{name}.py")
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
    assert "zip vs range(len): True" in out
    assert "unpacking: 1 [2, 3, 4] 5" in out
    assert "swap without a temp: 2 1" in out
    assert "comprehension vs map/filter/lambda: True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_range_len():
    scen = _load("scenarios")
    assert scen.s1_build() == ["a=1", "b=2", "c=3"]
    assert "IndexError" in scen.s1_break()
    assert scen.s1_fix() == ["a=1", "b=2"]


def test_s2_not_vs_is_none():
    scen = _load("scenarios")
    assert scen.s2_build() == 100.0
    discounted, zero = scen.s2_break()
    assert discounted == 75.0 and zero == 100.0
    assert scen.s2_fix() == 100.0


def test_s3_type_vs_isinstance():
    scen = _load("scenarios")
    assert scen.s3_build() == [1, 2, 3, 4]
    assert scen.s3_break() != [1, 2, 3, 4]      # the Rows subclass wasn't flattened
    assert scen.s3_fix() == [1, 2, 3, 4]


def test_s4_map_filter_one_pass():
    scen = _load("scenarios")
    assert scen.s4_build() == (120, 64)
    total, leftover = scen.s4_break()
    assert total == 120 and leftover == []
    assert scen.s4_fix() == (120, 64)

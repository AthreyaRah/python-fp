"""CI checks for the numeric types topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"num_{name}", HERE / f"{name}.py")
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
    assert "0.1 + 0.2 == 0.3 -> False" in out
    assert "Decimal('0.1')*3 == 0.3 -> True" in out
    assert " -7 // 2 =  -4" in out
    assert "nan == nan -> False" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_money_float():
    scen = _load("scenarios")
    assert scen.s1_build() == 10_000
    assert scen.s1_break() is False        # float accumulation drifts
    assert scen.s1_fix() is True


def test_s2_nan_guard():
    scen = _load("scenarios")
    assert scen.s2_build() == [1.5, 2.0, 3.5]
    assert len(scen.s2_break()) == 5       # the == nan guard matched nothing
    assert scen.s2_fix() == [1.5, 2.0, 3.5]


def test_s3_floor_division():
    scen = _load("scenarios")
    assert scen.s3_build() == 10
    assert scen.s3_break() == (-1, 59)     # floor, not truncation
    assert scen.s3_fix() == (0, -1)


def test_s4_decimal_from_float():
    scen = _load("scenarios")
    assert scen.s4_build() == Decimal("0.3")
    assert scen.s4_break() is False        # Decimal(0.1) != Decimal("0.1")
    assert scen.s4_fix() is True

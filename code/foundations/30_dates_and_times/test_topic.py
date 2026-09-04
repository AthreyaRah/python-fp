"""CI checks for the dates & times topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"dt_{name}", HERE / f"{name}.py")
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
    assert "aware - naive ->" in out and "can't subtract" in out
    assert "naive subtraction: 2.0 h" in out
    assert "via UTC: 1.0 h" in out
    assert "days until 2024-12-25: 359" in out
    assert "parsed back equal: True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_naive_vs_aware():
    scen = _load("scenarios")
    assert scen.s1_build() == 2.0
    assert "can't subtract" in scen.s1_break()
    assert scen.s1_fix() == 2.0


def test_s2_utcnow_naive():
    scen = _load("scenarios")
    assert scen.s2_build() is True
    assert scen.s2_break() is True     # naive epoch disagrees with aware
    assert scen.s2_fix() is True


def test_s3_same_tzinfo_subtraction():
    scen = _load("scenarios")
    assert scen.s3_build() == 1.0     # real elapsed via UTC
    assert scen.s3_break() == 2.0     # wall-clock difference, DST gap ignored
    assert scen.s3_fix() == 1.0


def test_s4_parse_no_tz():
    scen = _load("scenarios")
    assert scen.s4_build() is True
    assert "can't compare" in scen.s4_break()
    assert scen.s4_fix() is True

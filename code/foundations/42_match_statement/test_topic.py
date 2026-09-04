"""CI checks for the match statement topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    mod_name = f"mat_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "status: ['ok', 'redirect', 'client error', 'server error', 'unknown']" in out
    assert "'go north'" in out and "moving north" in out
    assert "taking sword, shield" in out
    assert "'origin'" in out and "'on the diagonal at 4'" in out
    assert "key ESC (extra: ['shift'])" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_bare_name_capture():
    scen = _load("scenarios")
    assert scen.s1_build() == ["ok", "missing", "other"]
    broke = scen.s1_break()
    assert all(r.startswith("captured OK=") for r in broke)   # everything matched case 1
    assert scen.s1_fix() == ["ok", "missing", "other"]


def test_s2_irrefutable_not_last():
    scen = _load("scenarios")
    assert scen.s2_build() == "compiles"
    assert "SyntaxError" in scen.s2_break()
    assert scen.s2_fix() == "compiles"


def test_s3_sequence_vs_string():
    scen = _load("scenarios")
    assert scen.s3_build() == "move -> north"
    assert scen.s3_break() == "fell through to _"
    assert scen.s3_fix() == "move -> north"


def test_s4_positional_class_pattern():
    scen = _load("scenarios")
    assert scen.s4_build() == "y-axis at 5"
    assert "TypeError" in scen.s4_break()
    assert scen.s4_fix() == "origin"

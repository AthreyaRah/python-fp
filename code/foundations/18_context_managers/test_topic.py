"""CI checks for the context managers topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"ctx_{name}", HERE / f"{name}.py")
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
    assert "Timer measured" in out
    assert "<outer>" in out and "</outer>" in out and "<inner>" in out
    assert "exception propagated, but </guarded> still printed" in out
    assert "opened 3 files" in out
    assert "suppress(FileNotFoundError): carried on" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_manual_close_leaks():
    scen = _load("scenarios")
    assert scen.s1_build() == ["closed"]
    assert scen.s1_break() == []          # file never closed
    assert scen.s1_fix() == ["closed"]


def test_s2_contextmanager_finally():
    scen = _load("scenarios")
    assert scen.s2_build() == ["open", "close"]
    assert scen.s2_break() == ["open"]    # cleanup skipped on exception
    assert scen.s2_fix() == ["open", "close"]


def test_s3_exit_suppresses():
    scen = _load("scenarios")
    assert scen.s3_build() == "propagated: real error"
    assert scen.s3_break() == "swallowed: the exception vanished"
    assert scen.s3_fix() == "propagated: real error"


def test_s4_reuse_one_shot():
    scen = _load("scenarios")
    assert scen.s4_build() == ["a", "b"]
    assert "Error" in scen.s4_break()      # RuntimeError or AttributeError
    assert scen.s4_fix() == ["x", "y"]

"""CI checks for the exceptions topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"exc_{name}", HERE / f"{name}.py")
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
    assert "eafp -> 1" in out and "eafp -> missing" in out
    assert "10: else (ok, result=10)" in out
    assert "0: except (division failed)" in out
    assert "__cause__ is the original: KeyError('port')" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_broad_except():
    scen = _load("scenarios")
    assert scen.s1_build() == 12.5
    assert scen.s1_break() == 0.0           # AttributeError swallowed
    assert "AttributeError" in scen.s1_fix()


def test_s2_return_in_finally():
    scen = _load("scenarios")
    assert scen.s2_build() == "propagated: disk gone"
    assert scen.s2_break() == "ok"          # exception discarded by finally's return
    assert scen.s2_fix() == "propagated: disk gone"


def test_s3_chaining():
    scen = _load("scenarios")
    assert scen.s3_build() == ("KeyError", "'retries'")
    assert scen.s3_break() is None          # __cause__ not set
    kind, msg = scen.s3_fix()
    assert kind == "KeyError" and "missing" in msg


def test_s4_half_applied():
    scen = _load("scenarios")
    assert scen.s4_build() == {"balance": 100, "log": []}
    assert scen.s4_break() == {"balance": -50, "log": []}
    assert scen.s4_fix() == {"balance": 100, "log": []}

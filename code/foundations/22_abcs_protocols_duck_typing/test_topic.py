"""CI checks for the ABCs, Protocols & duck typing topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"abc_{name}", HERE / f"{name}.py")
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
    assert "total_size(BytesIO): 5" in out
    assert "isinstance(exp, Exporter): True" in out
    assert "Pair supports 'in': True" in out and "index: 1" in out
    assert "isinstance([1,2,3], Sized): True" in out
    assert "isinstance(42, Sized): False" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_incomplete_abc():
    scen = _load("scenarios")
    assert scen.s1_build() == "get('a') -> 1"
    assert "Can't instantiate abstract class" in scen.s1_break()
    assert "instantiated" in scen.s1_fix()


def test_s2_protocol_runtime():
    scen = _load("scenarios")
    assert scen.s2_build() is True
    assert "runtime_checkable" in scen.s2_break()
    assert scen.s2_fix() is True


def test_s3_shallow_check():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert "isinstance says True, call fails: TypeError" in scen.s3_break()
    assert scen.s3_fix() is True


def test_s4_subclass_dict():
    scen = _load("scenarios")
    assert scen.s4_build() == {"name": "Ada", "city": "London"}
    broke = scen.s4_break()
    assert "CITY" in broke and "TITLE" in broke     # update/__init__ bypassed override
    assert scen.s4_fix() == {"title": "Dr", "city": "London"}

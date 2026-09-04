"""CI checks for the descriptors topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"desc_{name}", HERE / f"{name}.py")
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
    assert "o.quantity = 3 | o.price = 10" in out
    assert "o.quantity = -1 -> quantity must be positive, got -1" in out
    assert "c.greet is bound: True" in out
    assert "instance dict shadows non-data" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_state_on_descriptor():
    scen = _load("scenarios")
    assert scen.s1_build() == (1, 2)
    assert scen.s1_break() == (2, 2)     # shared descriptor object
    assert scen.s1_fix() == (1, 2)


def test_s2_non_data_shadowed():
    scen = _load("scenarios")
    assert scen.s2_build() == "computed"
    assert scen.s2_break() == "manual"   # instance dict shadows non-data descriptor
    assert scen.s2_fix() == "computed"


def test_s3_shared_storage_key():
    scen = _load("scenarios")
    assert scen.s3_build() == (4, 9)
    assert scen.s3_break() == (9, 9)     # both descriptors wrote to _value
    assert scen.s3_fix() == (4, 9)


def test_s4_descriptor_on_instance():
    scen = _load("scenarios")
    assert scen.s4_build() == "GET via descriptor"
    assert scen.s4_break() == "Loud"     # __get__ never fired
    assert scen.s4_fix() == "GET via descriptor"

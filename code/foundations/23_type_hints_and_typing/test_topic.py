"""CI checks for the type hints & typing topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"th_{name}", HERE / f"{name}.py")
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
    assert "add('x', 'y') = xy" in out
    assert "first([10, 20]) = 10" in out
    assert "first([]) = None" in out
    assert "make_row: {'id': 7, 'name': 'Ada', 'active': True}" in out
    assert "opening in 'w'" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_annotation_not_enforced():
    scen = _load("scenarios")
    assert scen.s1_build() == [0, 1, 2]
    assert "TypeError" in scen.s1_break()
    assert scen.s1_fix() == [0, 1, 2]


def test_s2_annotation_vs_none():
    scen = _load("scenarios")
    assert scen.s2_build() == [1]
    assert "AttributeError" in scen.s2_break()
    assert scen.s2_fix() == [1]


def test_s3_annotations_are_strings():
    scen = _load("scenarios")
    assert scen.s3_build() == {"a": "int", "b": "str", "return": "bool"}
    assert set(scen.s3_break().values()) == {"str"}     # raw annotations are strings
    assert set(scen.s3_fix().values()) == {"type"}      # get_type_hints -> real classes


def test_s4_optional_vs_default():
    scen = _load("scenarios")
    assert scen.s4_build() == "hello stranger"
    assert "TypeError" in scen.s4_break()
    assert scen.s4_fix() == "hello stranger"

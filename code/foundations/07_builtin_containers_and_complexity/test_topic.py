"""CI checks for the container internals & complexity topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"cont_{name}", HERE / f"{name}.py")
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
    assert "x in list ->" in out and "x in set  ->" in out
    assert "dict iterates in insertion order: ['z', 'a', 'm', 'b']" in out
    assert "hash([1,2,3]) -> unhashable type: 'list'" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_membership():
    scen = _load("scenarios")
    assert isinstance(scen.s1_build(), float)
    assert scen.s1_break() is True         # list version much slower
    assert scen.s1_fix() == [2, 1]


def test_s2_remove_while_iterating():
    scen = _load("scenarios")
    assert scen.s2_build() == [1, 3, 5]
    assert scen.s2_break() == [1, 2, 3]    # a 2 leaked through
    assert scen.s2_fix() == [1, 3, 5]


def test_s3_insert_front():
    scen = _load("scenarios")
    assert isinstance(scen.s3_build(), float)
    assert scen.s3_break() is True         # insert(0) far slower than deque
    assert scen.s3_fix() == [4, 3, 2, 1, 0]


def test_s4_dedup_order():
    scen = _load("scenarios")
    assert scen.s4_build() == ["b", "a", "c", "d"]
    assert scen.s4_break() is True         # set loses order, dict keeps it
    assert scen.s4_fix() == [3, 1, 2, 4]

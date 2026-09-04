"""CI checks for the names & references topic.

Asserts the demo runs and that each scenario's `break` genuinely misbehaves
while its `fix` genuinely works.
"""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"names_refs_{name}", HERE / f"{name}.py")
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
    assert "same object? True" in out
    assert "x == y -> True | x is y -> False" in out
    assert "default_shared_reference: [1]\n" in out
    assert "default_shared_reference: [1, 2]\n" in out
    assert "default_shared_reference: [1, 2, 3]\n" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_scenario_1_aliasing():
    scen = _load("scenarios")
    assert scen.s1_build() == [1, 2, 3]
    assert scen.s1_break() == [1, 2, 3, 4]  # snapshot mutated via the alias
    assert scen.s1_fix() is True


def test_scenario_2_identity():
    scen = _load("scenarios")
    assert scen.s2_build() is True
    assert scen.s2_break() == [False, False]  # `is` on 1000 fails
    assert scen.s2_fix() is True


def test_scenario_3_rebind_vs_mutate():
    scen = _load("scenarios")
    assert scen.s3_build() == [1, 2, 3]
    assert scen.s3_break() == [0.25, 0.5, 1.0]  # only the return value changed
    assert scen.s3_fix() == [0.25, 0.5, 1.0]


def test_scenario_4_mutable_default():
    scen = _load("scenarios")
    assert scen.s4_build() == [[1], [2], [3]]
    assert scen.s4_break() == [[1, 2, 3], [1, 2, 3], [1, 2, 3]]  # shared list
    assert scen.s4_fix() is True

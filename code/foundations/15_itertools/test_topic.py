"""CI checks for the itertools topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"it_{name}", HERE / f"{name}.py")
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
    assert "islice(count(1, 2), 5): [1, 3, 5, 7, 9]" in out
    assert "chain.from_iterable: [1, 2, 3, 4, 5]" in out
    assert "running max: [10, 10, 12, 12, 15, 15]" in out
    assert "pairwise diffs: [2, -1, 5, 0, -7]" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_groupby_unsorted():
    scen = _load("scenarios")
    assert scen.s1_build() == {"a": ["ant", "arc", "auk"], "b": ["bat", "bee"], "c": ["cat"]}
    assert scen.s1_break() == 1        # only the last 'a' run survived
    assert scen.s1_fix() == [3, 2, 1]


def test_s2_groupby_lifetime():
    scen = _load("scenarios")
    assert scen.s2_build() == [
        ("a", ["ant", "arc", "auk"]),
        ("b", ["bat", "bee"]),
        ("c", ["cat"]),
    ]
    assert scen.s2_break() == [[], [], []]
    assert scen.s2_fix() == [["ant", "arc", "auk"], ["bat", "bee"], ["cat"]]


def test_s3_chain_from_iterable():
    scen = _load("scenarios")
    assert scen.s3_build() == [1, 2, 3, 4, 5]
    assert scen.s3_break() == [[1, 2], [3, 4], [5]]
    assert scen.s3_fix() == [1, 2, 3, 4, 5]


def test_s4_zip_shortest():
    scen = _load("scenarios")
    assert scen.s4_build() == {"id": 1, "name": "Ada", "email": None, "city": None}
    assert scen.s4_break() == {"id": 1, "name": "Ada"}
    assert scen.s4_fix() == {"id": 1, "name": "Ada", "email": None, "city": None}

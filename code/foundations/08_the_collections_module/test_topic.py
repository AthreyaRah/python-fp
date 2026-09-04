"""CI checks for the collections module topic."""

from __future__ import annotations

import importlib.util
import io
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"coll_{name}", HERE / f"{name}.py")
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
    assert "defaultdict(list): {'eng': ['Ada', 'Cy'], 'data': ['Bo', 'Di']}" in out
    assert "most_common(2): [('the', 4)," in out
    assert "deque(maxlen=3) as it fills:" in out and "[3, 4, 5]" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_defaultdict_read_inserts():
    scen = _load("scenarios")
    assert scen.s1_build() == 1
    assert scen.s1_break() == 3     # membership check inserted 'b' and 'c'
    assert scen.s1_fix() == 1


def test_s2_counter_subtract():
    scen = _load("scenarios")
    assert scen.s2_build() == Counter(pear=1, plum=1)
    broke = dict(scen.s2_break())
    assert broke["apple"] == 0 and broke["plum"] == -2
    assert scen.s2_fix() == [("pear", 1)]


def test_s3_deque_maxlen():
    scen = _load("scenarios")
    assert scen.s3_build() == [3, 4, 5]
    assert scen.s3_break() == 100   # 150 events silently dropped
    assert scen.s3_fix() == 250


def test_s4_namedtuple_immutable():
    scen = _load("scenarios")
    assert scen.s4_build() == scen.Config("localhost", 9000)
    assert "AttributeError" in scen.s4_break()
    assert scen.s4_fix().port == 9000

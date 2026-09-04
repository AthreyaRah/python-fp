"""CI checks for the serialization topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    mod_name = f"ser_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[mod_name] = mod  # pickle needs the module importable by name
    spec.loader.exec_module(mod)
    return mod


def test_demo_runs():
    demo = _load("demo")
    buf = io.StringIO()
    with redirect_stdout(buf):
        demo.main()
    out = buf.getvalue()
    assert "round trip equal: True" in out
    assert "(key is now str, tuple is now list)" in out
    assert 'with default=str: {"created": "2024-05-01"}' in out
    assert "restored: Config(retries=3)" in out
    assert "unpacked: (42, 3.5, b'TEMP')" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_json_datetime():
    scen = _load("scenarios")
    assert "2024-01-01" in scen.s1_build()
    assert "not JSON serializable" in scen.s1_break()
    assert scen.s1_fix()["at"].startswith("2024-01-01")


def test_s2_json_string_keys():
    scen = _load("scenarios")
    assert scen.s2_build() == [(2020, 15), (2021, 22), (2022, 30)]
    assert scen.s2_break() == {"2020": 15, "2021": 22}
    assert scen.s2_fix() == {2020: 15, 2021: 22}


def test_s3_pickle_executes():
    scen = _load("scenarios")
    assert scen.s3_build() == []       # json executes nothing
    assert scen.s3_break() == ["payload ran during unpickling"]
    assert scen.s3_fix() == ["cache"]


def test_s4_csv_strings():
    scen = _load("scenarios")
    assert isinstance(scen.s4_build(), int)
    assert isinstance(scen.s4_break(), str)
    assert isinstance(scen.s4_fix(), int)

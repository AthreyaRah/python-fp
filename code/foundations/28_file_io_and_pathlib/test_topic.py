"""CI checks for the file I/O & pathlib topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"fio_{name}", HERE / f"{name}.py")
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
    assert "name: summary.csv | stem: summary | suffix: .csv" in out
    assert "with_suffix('.parquet'): reports/2024/summary.parquet" in out
    assert "glob('*.txt')      : ['a.txt']" in out
    assert "rglob('*.txt')     : ['a.txt', 'c.txt', 'd.txt']" in out
    assert "binary round-trips exactly: True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_relative_path():
    scen = _load("scenarios")
    assert scen.s1_build() == "[app]"
    assert "FileNotFoundError" in scen.s1_break()
    assert scen.s1_fix() == "[app]"


def test_s2_binary_in_text_mode():
    scen = _load("scenarios")
    assert scen.s2_build() is True
    assert "UnicodeDecodeError" in scen.s2_break()
    assert scen.s2_fix() is True


def test_s3_atomic_write():
    scen = _load("scenarios")
    assert scen.s3_build() == "old contents\n"     # crash left the original intact
    assert scen.s3_break() == "new line a\n"       # truncated + incomplete
    assert scen.s3_fix() == "x\ny\nz\n"


def test_s4_missing_parent():
    scen = _load("scenarios")
    assert scen.s4_build() is True
    assert "FileNotFoundError" in scen.s4_break()
    assert scen.s4_fix() is True

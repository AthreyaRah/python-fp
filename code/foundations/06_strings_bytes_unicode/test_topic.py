"""CI checks for the strings, bytes & Unicode topic."""

from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"sbu_{name}", HERE / f"{name}.py")
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
    assert "len(s) = 4 code points" in out
    assert "encode utf-8    -> b'caf\\xc3\\xa9'  (5 bytes)" in out
    assert "encode latin-1  -> b'caf\\xe9'  (4 bytes)" in out
    assert "nfc == nfd ->" in out and "after normalizing both to NFC, equal? -> True" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


def test_s1_codec_mismatch():
    scen = _load("scenarios")
    assert scen.s1_build() == "café ☕ π"
    assert "UnicodeDecodeError" in scen.s1_break()
    assert scen.s1_fix() == "café ☕ π"


def test_s2_byte_truncation():
    scen = _load("scenarios")
    assert scen.s2_build() == "café ☕"
    assert "UnicodeDecodeError" in scen.s2_break()
    assert scen.s2_fix() == "caf"  # incomplete tail dropped


def test_s3_normalization():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert scen.s3_break() is False  # NFD string not found in an NFC-keyed set
    assert scen.s3_fix() is True


def test_s4_str_bytes_mixing():
    scen = _load("scenarios")
    assert scen.s4_build() == "received: Hi"
    assert scen.s4_break() == "received: b'Hi'"  # the repr leaked in
    assert scen.s4_fix() == "received: Hi"

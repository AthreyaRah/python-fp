"""CI checks for the environments & packaging topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"pkg_{name}", HERE / f"{name}.py")
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
    assert "name/version   : demo-app 0.2.0" in out
    assert "dependencies   : ['httpx>=0.27', 'rich']" in out
    assert "definitely-not-installed not installed" in out
    assert "import '_pytest' comes from: ['pytest']" in out


def test_scenarios_run():
    scen = _load("scenarios")
    real_tabnanny = sys.modules.get("tabnanny")
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            scen.main()
        assert buf.getvalue().count("🔨 build") == 4
    finally:
        if real_tabnanny is not None:
            sys.modules["tabnanny"] = real_tabnanny


def test_s1_shadowing():
    scen = _load("scenarios")
    real = sys.modules.get("tabnanny")
    try:
        assert scen.s1_build() is True
        assert scen.s1_break() is True     # our file was imported
        assert scen.s1_fix() is True
    finally:
        scen._restore("tabnanny")
        if real is not None:
            sys.modules["tabnanny"] = real


def test_s2_binary_mode():
    scen = _load("scenarios")
    assert scen.s2_build() == {"project": {"name": "x", "version": "1.0"}}
    assert "binary mode" in scen.s2_break()
    assert scen.s2_fix() == {"project": {"name": "x", "version": "1.0"}}


def test_s3_no_writer():
    scen = _load("scenarios")
    assert 'version = "0.3.0"' in scen.s3_build()
    assert "AttributeError" in scen.s3_break()
    assert scen.s3_fix() == {"name": "demo", "version": "0.3.0"}


def test_s4_import_vs_dist_name():
    scen = _load("scenarios")
    assert scen.s4_build() is True
    assert "PackageNotFoundError" in scen.s4_break()
    assert scen.s4_fix() is True

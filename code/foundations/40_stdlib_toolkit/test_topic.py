"""CI checks for the stdlib toolkit topic."""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

HERE = Path(__file__).parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"tk_{name}", HERE / f"{name}.py")
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
    assert "limit is an int: True" in out
    assert "Color.RED is Color.RED: True" in out
    assert "WRITE in it: True" in out
    assert "child stdout: hello from a child" in out
    assert "without check=True, a failure is just a returncode: 3" in out


def test_scenarios_run():
    scen = _load("scenarios")
    buf = io.StringIO()
    with redirect_stdout(buf):
        scen.main()
    assert buf.getvalue().count("🔨 build") == 4


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX shell syntax in the demo")
def test_s1_shell_injection():
    scen = _load("scenarios")
    assert scen.s1_build() == "real contents"
    assert scen.s1_break() == "injected command executed"
    assert scen.s1_fix() == "real contents"


def test_s2_check_true():
    scen = _load("scenarios")
    with pytest.raises(Exception):
        scen.s2_build()          # check=True on a failing command raises
    assert "code continued" in scen.s2_break()
    assert "CalledProcessError" in scen.s2_fix()


def test_s3_enum_value():
    scen = _load("scenarios")
    assert scen.s3_build() is True
    assert scen.s3_break() is True    # plain Enum member != "admin"
    assert scen.s3_fix() is True


def test_s4_argparse_strings():
    scen = _load("scenarios")
    assert scen.s4_build() == 10
    assert scen.s4_break() == "55"
    assert scen.s4_fix() == 10

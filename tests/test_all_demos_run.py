"""Every code/foundations/<topic>/demo.py must run to completion with exit code 0.

This is the guarantee behind "copy, run, read the output" on every page.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DEMOS = sorted((REPO / "code" / "foundations").glob("*/demo.py"))
SCENARIOS = sorted((REPO / "code" / "foundations").glob("*/scenarios.py"))


def _id(path: Path) -> str:
    return str(path.relative_to(REPO))


@pytest.mark.parametrize("script", DEMOS, ids=[_id(p) for p in DEMOS])
def test_demo_runs(script: Path):
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, f"{_id(script)} failed:\n{proc.stdout}\n{proc.stderr}"


@pytest.mark.parametrize("script", SCENARIOS, ids=[_id(p) for p in SCENARIOS])
def test_scenarios_runs(script: Path):
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, f"{_id(script)} failed:\n{proc.stdout}\n{proc.stderr}"


def test_at_least_the_exemplars_exist():
    have = {_id(p) for p in DEMOS}
    for expected in (
        "code/foundations/02_names_objects_references/demo.py",
        "code/foundations/33_gil_threads_races/demo.py",
    ):
        assert expected in have

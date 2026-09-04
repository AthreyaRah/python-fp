"""Testing with pytest & hypothesis - the practice snippet.

Run it:  python code/foundations/38_testing_with_pytest/demo.py

Mental model:
- A test states an OBSERVABLE fact about your code and `assert`s it. pytest
  rewrites `assert` so a failure shows both sides.
- Discovery: files `test_*.py`, functions `test_*`. Arrange - Act - Assert.
- FIXTURES provide inputs and clean up after: a `@pytest.fixture` that `yield`s
  runs the code after the `yield` as teardown. Requesting a fixture by parameter
  name injects it.
- `@pytest.mark.parametrize` runs one test body over many inputs.
- `pytest.raises` asserts an exception; `pytest.approx` compares floats.
- HYPOTHESIS generates many inputs for a PROPERTY that should always hold, and
  shrinks any failure to a minimal example.

This script writes a small test file and runs pytest on it.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402

SAMPLE = '''
import pytest


def normalise(name: str) -> str:
    return name.strip().lower()


@pytest.fixture
def sample_names():
    data = ["  Ada ", "GRACE", "linus"]
    yield data
    data.clear()                 # teardown, runs after each test that uses it


def test_normalise_basic(sample_names):
    assert [normalise(n) for n in sample_names] == ["ada", "grace", "linus"]


@pytest.mark.parametrize("raw,expected", [
    ("  X ", "x"),
    ("Y", "y"),
    ("z z", "z z"),
])
def test_normalise_cases(raw, expected):
    assert normalise(raw) == expected


def test_raises_on_none():
    with pytest.raises(AttributeError):
        normalise(None)


def test_float_math():
    assert 0.1 + 0.2 == pytest.approx(0.3)


# --- a property-based test ---------------------------------------------------
from hypothesis import given, strategies as st


@given(st.text())
def test_normalise_is_idempotent(s):
    once = normalise(s)
    assert normalise(once) == once     # normalising twice == normalising once
'''


def main() -> None:
    d = generated_dir("pytest_demo")
    test_file = d / "test_sample.py"
    test_file.write_text(textwrap.dedent(SAMPLE).strip() + "\n", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", "--no-header"],
        capture_output=True, text=True,
    )
    print(proc.stdout.strip())
    summary = [ln for ln in proc.stdout.splitlines() if "passed" in ln or "failed" in ln]
    print("\nresult:", summary[-1] if summary else "(no summary)")


if __name__ == "__main__":
    main()

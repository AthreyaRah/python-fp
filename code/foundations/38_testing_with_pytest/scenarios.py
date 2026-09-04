"""Testing with pytest - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/38_testing_with_pytest/scenarios.py

Each scenario writes a tiny test file and runs pytest on it, reporting the
pass/fail counts.
"""

from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

ROOT = generated_dir("pytest_scenarios")


def _run_pytest(name: str, source: str) -> tuple[int, int]:
    """Write `source` to a test file, run pytest, return (passed, failed)."""
    path = ROOT / f"test_{name}.py"
    path.write_text(textwrap.dedent(source).strip() + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(path), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True,
    )
    out = proc.stdout + proc.stderr
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", out)) else 0
    return passed, failed + errors


# ======================================================================================
# Scenario 1 - Shared state between tests -> order-dependent failure.
# ======================================================================================

_ISOLATED = """
    import pytest

    @pytest.fixture
    def store():
        return {}                       # a fresh dict per test

    def test_a(store):
        store["x"] = 1
        assert store == {"x": 1}

    def test_b(store):
        assert store == {}              # starts empty, always
"""

_SHARED = """
    STORE = {}                          # module-level: shared across tests

    def test_a():
        STORE["x"] = 1
        assert STORE == {"x": 1}

    def test_b():
        assert STORE == {}              # fails - test_a left "x" behind
"""


def s1_build() -> tuple[int, int]:
    return _run_pytest("isolated", _ISOLATED)   # (2, 0)


def s1_break() -> tuple[int, int]:
    return _run_pytest("shared", _SHARED)       # (1, 1) - test_b fails because of test_a


def s1_fix() -> tuple[int, int]:
    return _run_pytest("isolated2", _ISOLATED)


S1_WHY = """
Tests must be independent - runnable in any order, in isolation. A module-level
mutable (`STORE = {}`) that one test writes and another reads couples them:
`test_b` passes alone but fails after `test_a`. Give each test its own state via a
fixture (which pytest rebuilds per test), `tmp_path`, `monkeypatch`, or explicit
setup/teardown.
"""


# ======================================================================================
# Scenario 2 - Comparing floats with ==.
# ======================================================================================

_EXACT = """
    def combine(a, b):
        return a + b

    def test_combine():
        assert combine(0.1, 0.2) == 0.3       # 0.30000000000000004 != 0.3
"""

_APPROX = """
    import pytest

    def combine(a, b):
        return a + b

    def test_combine():
        assert combine(0.1, 0.2) == pytest.approx(0.3)
"""


def s2_build() -> tuple[int, int]:
    return _run_pytest("approx", _APPROX)       # (1, 0)


def s2_break() -> tuple[int, int]:
    return _run_pytest("exact", _EXACT)         # (0, 1)


def s2_fix() -> tuple[int, int]:
    return _run_pytest("approx2", _APPROX)


S2_WHY = """
Floating-point results of arithmetic rarely equal a decimal literal exactly, so
`assert result == 0.3` is flaky. `pytest.approx(x)` compares with a relative (and
absolute) tolerance: `assert result == pytest.approx(0.3)`. Same idea as
`math.isclose`.
"""


# ======================================================================================
# Scenario 3 - Fixture teardown that never runs (no yield).
# ======================================================================================

_NO_YIELD = """
    import pytest

    LOG = []

    @pytest.fixture
    def resource():
        LOG.append("open")
        return "handle"                 # returns -> teardown code below is dead
        LOG.append("close")

    def test_uses_it(resource):
        assert resource == "handle"

    def test_teardown_ran():
        assert LOG == ["open", "close"]   # fails: 'close' never appended
"""

_YIELD = """
    import pytest

    LOG = []

    @pytest.fixture
    def resource():
        LOG.append("open")
        yield "handle"                  # test runs here...
        LOG.append("close")            # ...then this teardown runs

    def test_uses_it(resource):
        assert resource == "handle"

    def test_teardown_ran():
        assert LOG == ["open", "close"]
"""


def s3_build() -> tuple[int, int]:
    return _run_pytest("yield_fixture", _YIELD)      # (2, 0)


def s3_break() -> tuple[int, int]:
    return _run_pytest("noyield_fixture", _NO_YIELD)  # (1, 1)


def s3_fix() -> tuple[int, int]:
    return _run_pytest("yield_fixture2", _YIELD)


S3_WHY = """
A fixture that `return`s a value provides it but has no teardown - code after the
`return` is unreachable. A fixture that `yield`s hands the value to the test, then
RESUMES after the `yield` once the test finishes (pass or fail) to run teardown.
Use `yield` whenever there is cleanup.
"""


# ======================================================================================
# Scenario 4 - A test with no assertion always passes.
# ======================================================================================

_NO_ASSERT = """
    def add(a, b):
        return a - b                    # BUG: subtraction

    def test_add():
        add(2, 3)                        # calls it... but asserts nothing
"""

_WITH_ASSERT = """
    def add(a, b):
        return a - b                    # same bug

    def test_add():
        assert add(2, 3) == 5           # now the bug is caught
"""


def s4_build() -> tuple[int, int]:
    # A real test of correct code passes for the right reason.
    return _run_pytest("real_add", """
        def add(a, b):
            return a + b

        def test_add():
            assert add(2, 3) == 5
    """)  # (1, 0)


def s4_break() -> tuple[int, int]:
    return _run_pytest("no_assert", _NO_ASSERT)   # (1, 0) - GREEN despite the bug


def s4_fix() -> tuple[int, int]:
    return _run_pytest("with_assert", _WITH_ASSERT)  # (0, 1) - the bug is caught


S4_WHY = """
pytest marks a test as passed if it simply RETURNS without raising. A test that
calls the code but never `assert`s anything is always green - it proves only "no
exception", not "correct result". Every test needs at least one assertion about
an observable outcome. (A `return` of a truthy value even warns in newer pytest.)
"""


SCENARIOS = [
    Scenario("Shared state between tests", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Comparing floats with ==", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Fixture teardown without yield", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("A test with no assertion", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

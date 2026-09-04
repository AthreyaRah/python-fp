"""Numeric types — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/05_numeric_types/scenarios.py
"""

from __future__ import annotations

import math
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 — Money in float.
# ======================================================================================

def s1_build() -> int:
    # Represent money as an integer number of cents. Always exact.
    total_cents = 0
    for _ in range(1_000):
        total_cents += 10  # $0.10
    return total_cents  # 10_000 cents == $100.00 exactly


def s1_break() -> bool:
    total = 0.0
    for _ in range(1_000):
        total += 0.10
    # Expected 100.0; you get 100.00000000000007 or similar.
    return total == 100.0  # False


def s1_fix() -> bool:
    total = Decimal("0.00")
    for _ in range(1_000):
        total += Decimal("0.10")
    return total == Decimal("100.00")  # True


S1_WHY = """
0.10 has no exact representation as a binary fraction, so each `+= 0.10` stores a
value slightly off, and 1000 of those errors accumulate. Integer cents sidestep
floats entirely; `Decimal` does exact base-10 arithmetic. Never hold currency in
a binary float.
"""


# ======================================================================================
# Scenario 2 — Guarding against NaN with ==.
# ======================================================================================

def _measurements() -> list[float]:
    return [1.5, float("nan"), 2.0, float("nan"), 3.5]


def s2_build() -> list[float]:
    return [v for v in _measurements() if not math.isnan(v)]  # [1.5, 2.0, 3.5]


def s2_break() -> list[float]:
    nan = float("nan")
    # Intent: drop the NaNs. `v == nan` is ALWAYS False, so nothing is dropped.
    kept = [v for v in _measurements() if v != nan]
    assert len(kept) == 5, "the == nan guard never matched; NaNs slipped through"
    return kept


def s2_fix() -> list[float]:
    return [v for v in _measurements() if not math.isnan(v)]


S2_WHY = """
IEEE-754 defines NaN as unordered: `nan == anything` is False, including
`nan == nan`, and `nan != anything` is True. So `v == nan` never matches and
`v != nan` matches everything. Detect NaN with `math.isnan(v)` (or `v != v`,
which is True only for NaN), never with `==`.
"""


# ======================================================================================
# Scenario 3 — Floor division with negative numbers.
# ======================================================================================

def s3_build() -> int:
    # Pages needed to show `items` at `per_page` each: ceil division, done safely.
    items, per_page = 95, 10
    return -(-items // per_page)  # 10


def s3_break() -> tuple[int, int]:
    # "Truncate toward zero" is a common wrong assumption for //.
    seconds = -1
    minutes = seconds // 60          # expected 0, got -1
    remainder = seconds % 60         # expected -1, got 59
    assert (minutes, remainder) == (-1, 59)
    return minutes, remainder


def s3_fix() -> tuple[int, int]:
    seconds = -1
    minutes = int(seconds / 60)                 # truncates toward zero -> 0
    remainder = seconds - minutes * 60          # -1
    return minutes, remainder


S3_WHY = """
Python's `//` is *floor* division: it rounds toward negative infinity, not toward
zero. And `%` is defined so that `a == (a // b) * b + (a % b)` always holds, which
forces the remainder's sign to match the divisor. If you want truncation toward
zero, use `int(a / b)` or `math.trunc`, and compute the remainder from that.
"""


# ======================================================================================
# Scenario 4 — Decimal built from a float.
# ======================================================================================

def s4_build() -> "Decimal":
    return Decimal("0.1") + Decimal("0.2")  # Decimal('0.3') exactly


def s4_break() -> bool:
    d = Decimal(0.1)  # passing a float: faithfully copies the inexact value
    # d is Decimal('0.1000000000000000055511151231257827021181583404541015625')
    return d == Decimal("0.1")  # False


def s4_fix() -> bool:
    d = Decimal("0.1")            # from a string: exactly one tenth
    also = Decimal(1) / Decimal(10)
    return d == Decimal("0.1") and also == d


S4_WHY = """
`Decimal(0.1)` does not "fix" the float — it converts the exact binary value the
float already holds, which is not 1/10. To get an exact decimal, construct from a
string (`Decimal("0.1")`) or from integers (`Decimal(1) / Decimal(10)`). Same
rule for `Fraction`: `Fraction(0.1)` != `Fraction(1, 10)`.
"""


SCENARIOS = [
    Scenario("Money in float", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Guarding NaN with ==", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Floor division with negatives", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Decimal from a float", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

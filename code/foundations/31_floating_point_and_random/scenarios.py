"""Floating point & random - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/31_floating_point_and_random/scenarios.py
"""

from __future__ import annotations

import math
import random
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Accumulated floating-point error in a sum.
# ======================================================================================

# Values that span very different magnitudes: the small ones get lost.
_SPREAD = [1e16, 1.0, -1e16, 1.0, 1.0]   # true sum is 3.0


def s1_build() -> float:
    return math.fsum(_SPREAD)   # 3.0 - fsum keeps an exact running compensation


def s1_break() -> float:
    total = 0.0
    for v in _SPREAD:
        total += v              # plain += near 1e16 swallows a 1.0
    return total  # 2.0, not 3.0


def s1_fix() -> float:
    return math.fsum(_SPREAD)   # or sum(_SPREAD): compensated since Python 3.12


S1_WHY = """
`1e16 + 1.0` rounds to `1e16` because a float64 near 1e16 cannot represent a
difference of 1 - the small addend is swallowed, and a manual `+=` loop loses it.
`math.fsum` carries an exact running correction; the built-in `sum` also uses
compensated (Neumaier) summation for floats since Python 3.12. When magnitudes
vary a lot, reach for `math.fsum`, or sort ascending, or use `Decimal`/integers.
"""


# ======================================================================================
# Scenario 2 - Sharing the module-global random generator.
# ======================================================================================

def _library_call_that_uses_random() -> None:
    random.random()   # some dependency also pulls from the global generator


def s2_build() -> list[int]:
    rng = random.Random(123)                       # our own generator
    _library_call_that_uses_random()               # cannot disturb `rng`
    return [rng.randint(0, 9) for _ in range(4)]


def s2_break() -> bool:
    random.seed(123)
    _library_call_that_uses_random()               # consumes one draw from global
    with_interference = [random.randint(0, 9) for _ in range(4)]

    random.seed(123)
    clean = [random.randint(0, 9) for _ in range(4)]

    return with_interference != clean              # "reproducible" run diverged


def s2_fix() -> bool:
    rng = random.Random(123)
    _library_call_that_uses_random()
    a = [rng.randint(0, 9) for _ in range(4)]

    rng = random.Random(123)
    _library_call_that_uses_random()
    b = [rng.randint(0, 9) for _ in range(4)]

    return a == b                                  # stable regardless of other code


S2_WHY = """
`random.random()`, `random.randint()`, etc. all draw from one hidden
module-global generator. Anything else in the process that calls them - a
library, a logging filter, a test helper - advances that shared state, so your
"seeded, reproducible" sequence shifts. Create a dedicated `random.Random(seed)`
instance and use only its methods.
"""


# ======================================================================================
# Scenario 3 - random.sample without enough population.
# ======================================================================================

def s3_build() -> int:
    pool = ["a", "b", "c"]
    picks = random.Random(0).choices(pool, k=10)   # WITH replacement -> fine
    return len(picks)  # 10


def s3_break() -> str:
    pool = ["a", "b", "c"]
    try:
        random.Random(0).sample(pool, k=10)        # WITHOUT replacement
    except ValueError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> int:
    pool = ["a", "b", "c"]
    return len(random.Random(0).choices(pool, k=10))  # or sample(pool, min(k, len(pool)))


S3_WHY = """
`random.sample(population, k)` draws k DISTINCT items - without replacement - so it
raises `ValueError: Sample larger than population or is negative` when k exceeds
the population size. Use `random.choices(population, k=k)` when repeats are
acceptable (sampling with replacement), or clamp `k` to `len(population)`.
"""


# ======================================================================================
# Scenario 4 - round() uses banker's rounding.
# ======================================================================================

def s4_build() -> str:
    # "round half up" explicitly, via Decimal.
    return str(Decimal("2.5").quantize(Decimal("1"), rounding=ROUND_HALF_UP))  # "3"


def s4_break() -> tuple[int, int, int]:
    # Expecting 1, 2, 3 - "round half up". Python rounds half to EVEN.
    got = (round(0.5), round(1.5), round(2.5))
    assert got == (0, 2, 2)
    return got


def s4_fix() -> list[int]:
    def round_half_up(x: float) -> int:
        return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    return [round_half_up(v) for v in (0.5, 1.5, 2.5)]  # [1, 2, 3]


S4_WHY = """
Python 3's built-in `round()` implements "round half to even" (banker's
rounding): halves go to the nearest even integer, so `round(0.5) == 0` and
`round(2.5) == 2`. It reduces cumulative bias over many values, but surprises
anyone expecting school-style "round half up". For that, use
`decimal.Decimal(str(x)).quantize(..., rounding=ROUND_HALF_UP)`.
"""


SCENARIOS = [
    Scenario("Accumulated float error", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Shared global random generator", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("sample larger than population", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("round() is banker's rounding", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

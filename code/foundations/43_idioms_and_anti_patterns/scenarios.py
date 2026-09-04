"""Idioms & anti-patterns - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/43_idioms_and_anti_patterns/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - range(len(...)) indexing vs zip.
# ======================================================================================

def s1_build() -> list[str]:
    keys = ["a", "b", "c"]
    values = [1, 2, 3]
    return [f"{k}={v}" for k, v in zip(keys, values, strict=True)]


def s1_break() -> str:
    keys = ["a", "b", "c"]
    values = [1, 2]                       # one short - a data glitch
    try:
        return str([f"{keys[i]}={values[i]}" for i in range(len(keys))])
    except IndexError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> list[str]:
    keys = ["a", "b", "c"]
    values = [1, 2]
    # zip stops at the shortest; strict=True would flag the mismatch loudly.
    return [f"{k}={v}" for k, v in zip(keys, values)]


S1_WHY = """
`for i in range(len(a))` then indexing `a[i]`, `b[i]` re-derives what iteration
already gives you, and silently assumes the sequences are the same length -
`b[i]` throws `IndexError` when they aren't. `zip(a, b)` pairs them directly and
stops at the shorter; `zip(a, b, strict=True)` (3.10+) raises on a length
mismatch. Use `enumerate(a)` when you genuinely need the index.
"""


# ======================================================================================
# Scenario 2 - `if not value` where you mean `if value is None`.
# ======================================================================================

def apply_discount(price: float, discount: float | None) -> float:
    # BUG version uses `if not discount` - which is also true for 0.0
    return price if not discount else price * (1 - discount)


def apply_discount_fixed(price: float, discount: float | None) -> float:
    return price if discount is None else price * (1 - discount)


def s2_build() -> float:
    return apply_discount_fixed(100.0, None)      # 100.0 - no discount supplied


def s2_break() -> tuple[float, float]:
    supplied_zero = apply_discount(100.0, 0.0)    # caller explicitly said "0% off"
    not_supplied = apply_discount(100.0, None)    # caller said nothing
    # Both come out 100.0 - the function can't tell "0" from "missing".
    assert supplied_zero == not_supplied == 100.0
    # And a real 0.25 discount still works, so the bug hides:
    return apply_discount(100.0, 0.25), supplied_zero


def s2_fix() -> float:
    return apply_discount_fixed(100.0, 0.0)       # 100.0, but for the RIGHT reason


S2_WHY = """
`if not discount` is true for `None`, `0`, `0.0`, `""`, `[]`, `False` - so a
legitimate zero is indistinguishable from "not provided". When you mean "the
argument was omitted", test `is None`. Reserve `if not x:` for "x is empty /
falsy" and make sure that is really what you want.
"""


# ======================================================================================
# Scenario 3 - type(x) == list instead of isinstance.
# ======================================================================================

class Rows(list):                    # a list subclass with extra behaviour
    pass


def flatten_one_level(value) -> list:
    out: list = []
    for v in value:
        if isinstance(v, list):      # respects subclasses
            out.extend(v)
        else:
            out.append(v)
    return out


def flatten_exact(value) -> list:
    out: list = []
    for v in value:
        if type(v) == list:          # EXACT type only
            out.extend(v)
        else:
            out.append(v)
    return out


def s3_build() -> list:
    return flatten_one_level([Rows([1, 2]), 3, [4]])   # [1, 2, 3, 4]


def s3_break() -> list:
    result = flatten_exact([Rows([1, 2]), 3, [4]])
    # Rows is a list, but `type(v) == list` is False for it, so it isn't flattened.
    assert result == [Rows([1, 2]), 3, 4]
    return result


def s3_fix() -> list:
    return flatten_one_level([Rows([1, 2]), 3, [4]])


S3_WHY = """
`type(x) == list` asks "is x EXACTLY a list?" - it says no to every subclass
(`Rows`, `collections.UserList`, an ORM's list-like column). `isinstance(x,
list)` asks "is x a list or a kind of list?", which is almost always what you
mean. Use `isinstance` (with a tuple of types if needed); reserve exact `type()`
checks for the rare case where subclasses must be rejected.
"""


# ======================================================================================
# Scenario 4 - map/filter are one-pass iterators.
# ======================================================================================

def s4_build() -> tuple[int, int]:
    nums = range(10)
    squares = [x * x for x in nums if x % 2 == 0]   # a list: reusable
    return sum(squares), max(squares)


def s4_break() -> tuple[int, list]:
    nums = range(10)
    squares = map(lambda x: x * x, filter(lambda x: x % 2 == 0, nums))
    total = sum(squares)          # consumes the iterator
    leftover = list(squares)     # already exhausted -> []
    assert leftover == []
    return total, leftover


def s4_fix() -> tuple[int, int]:
    nums = range(10)
    squares = [x * x for x in nums if x % 2 == 0]
    return sum(squares), max(squares)


S4_WHY = """
`map` and `filter` return lazy, single-pass iterators (like generator
expressions), so consuming one with `sum` leaves nothing for a second pass -
`max` then sees an empty iterator. A list comprehension both reads clearer than
nested `map`/`filter`/`lambda` AND gives you a reusable list. Use `map`/`filter`
only when you already have a named function and are piping straight into one
consumer.
"""


SCENARIOS = [
    Scenario("range(len(...)) vs zip", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("`not value` vs `is None`", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("type() == vs isinstance", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("map/filter are one-pass", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

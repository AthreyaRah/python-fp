"""Comprehensions - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/09_comprehensions/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - A generator expression is single-pass.
# ======================================================================================

def s1_build() -> tuple[int, int]:
    squares = [x * x for x in range(5)]  # a list: reusable
    return sum(squares), max(squares)


def s1_break() -> tuple[list, list]:
    squares = (x * x for x in range(5))  # a generator: one pass only
    first = list(squares)
    second = list(squares)              # already exhausted
    assert first == [0, 1, 4, 9, 16] and second == []
    return first, second


def s1_fix() -> tuple[int, int]:
    squares = [x * x for x in range(5)]  # materialise if you need it twice
    return sum(squares), max(squares)


S1_WHY = """
A generator expression produces an iterator. Iterating it advances an internal
position; when it reaches the end it raises StopIteration and stays exhausted -
there is no rewind. If you consume it more than once, or with two functions
(`sum` then `max`), only the first sees data. Use a list comprehension when you
need to iterate more than once.
"""


# ======================================================================================
# Scenario 2 - Closures capturing the comprehension variable.
# ======================================================================================

def s2_build() -> list[int]:
    funcs = [lambda i=i: i for i in range(4)]  # bind the value now, via a default
    return [f() for f in funcs]  # [0, 1, 2, 3]


def s2_break() -> list[int]:
    funcs = [lambda: i for i in range(4)]  # all close over the SAME cell
    results = [f() for f in funcs]
    assert results == [3, 3, 3, 3], "every lambda sees the final i"
    return results


def s2_fix() -> list[int]:
    from functools import partial

    funcs = [partial(lambda v: v, i) for i in range(4)]  # freeze i at creation
    return [f() for f in funcs]


S2_WHY = """
The comprehension has one variable `i`, rebound each iteration. A bare
`lambda: i` closes over the variable, not its current value, so when you call the
lambdas later they all read `i`'s final value. Bind eagerly: `lambda i=i: i`
(default value captured at def time) or `functools.partial`.
"""


# ======================================================================================
# Scenario 3 - Nested comprehension clause order.
# ======================================================================================

def s3_build() -> list[int]:
    matrix = [[1, 2], [3, 4], [5, 6]]
    return [x for row in matrix for x in row]  # outer clause first: [1,2,3,4,5,6]


def s3_break() -> str:
    matrix = [[1, 2], [3, 4]]  # noqa: F841 - referenced inside the comprehension
    try:
        # Clauses in the wrong order: `row` is used before the clause defines it.
        return str([x for x in row for row in matrix])  # noqa: F821
    except NameError as exc:
        return f"{type(exc).__name__}: {exc}"


def s3_fix() -> list[int]:
    matrix = [[1, 2], [3, 4]]
    return [x for row in matrix for x in row]  # left-to-right = outer-to-inner


S3_WHY = """
Comprehension `for`/`if` clauses execute left to right, exactly like writing the
nested loops top to bottom:
`for row in matrix:` then `for x in row:`. Put the clause that defines a name
before any clause that uses it.
"""


# ======================================================================================
# Scenario 4 - Wrapping a genexp in a list defeats short-circuiting.
# ======================================================================================

_CALLS: list[int] = []


def _expensive(x: int) -> bool:
    _CALLS.append(x)
    return x > 3


def s4_build() -> tuple[bool, int]:
    _CALLS.clear()
    found = any(_expensive(x) for x in range(100))  # genexp: any() stops at first hit
    return found, len(_CALLS)  # (True, 5) - checked 0..4 then stopped


def s4_break() -> tuple[bool, int]:
    _CALLS.clear()
    found = any([_expensive(x) for x in range(100)])  # list comp: ALL 100 run first
    assert len(_CALLS) == 100
    return found, len(_CALLS)


def s4_fix() -> tuple[bool, int]:
    _CALLS.clear()
    found = any(_expensive(x) for x in range(100))  # drop the brackets
    return found, len(_CALLS)


S4_WHY = """
`any()` / `all()` / `next()` short-circuit: they stop as soon as the answer is
known. A generator expression feeds them items lazily, so evaluation stops early.
A list comprehension inside the call builds the ENTIRE list first - every
`_expensive` call runs - and only then hands the finished list to `any`. Drop the
`[]` and pass the generator.
"""


SCENARIOS = [
    Scenario("Generator expression is single-pass", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Closures over the loop variable", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Nested clause order", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("List comp defeats short-circuit", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

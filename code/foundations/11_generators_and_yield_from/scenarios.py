"""Generators - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/11_generators_and_yield_from/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Validation in a generator body doesn't run until first next().
# ======================================================================================

def s1_build() -> str:
    def parse(rows):
        if not rows:
            raise ValueError("no rows")   # checked eagerly by the wrapper below
        return _parse_inner(rows)

    def _parse_inner(rows):
        for r in rows:
            yield r.upper()

    try:
        parse([])                          # raises right now, at call time
    except ValueError as exc:
        return f"caught at call time: {exc}"
    return "no error (unexpected)"


def s1_break() -> str:
    def parse(rows):
        if not rows:
            raise ValueError("no rows")   # inside a generator body: deferred!
        for r in rows:
            yield r.upper()

    gen = parse([])            # returns a generator; the `if` has NOT run
    made_it_here = "constructed a 'parser' over empty input without error"
    try:
        next(gen)             # the ValueError finally fires here
    except ValueError as exc:
        return f"{made_it_here}; error only on first use: {exc}"
    return made_it_here


def s1_fix() -> str:
    def parse(rows):
        if not rows:
            raise ValueError("no rows")
        return _inner(rows)   # plain function does the check, delegates to a gen

    def _inner(rows):
        for r in rows:
            yield r.upper()

    try:
        parse([])
    except ValueError as exc:
        return f"caught at call time: {exc}"
    return "no error (unexpected)"


S1_WHY = """
Calling a generator function does not execute its body - it builds a paused
generator. Any argument validation written with `yield` in the same function is
deferred until the first `next()`, so errors surface far from the call. Split it:
an ordinary function validates eagerly and returns an inner generator.
"""


# ======================================================================================
# Scenario 2 - A generator object is single-pass.
# ======================================================================================

def _squares_gen():
    for x in range(5):
        yield x * x


def s2_build() -> tuple[list, list]:
    return list(_squares_gen()), list(_squares_gen())  # call again for a 2nd pass


def s2_break() -> tuple[list, list]:
    g = _squares_gen()
    first = list(g)
    second = list(g)            # g is exhausted
    assert second == []
    return first, second


def s2_fix() -> tuple[list, list]:
    squares = list(_squares_gen())   # materialise once
    return list(squares), list(squares)


S2_WHY = """
A generator IS an iterator: one forward pass, no reset. Iterate it twice and the
second pass is empty. Either call the generator function again for a fresh
generator, or convert to a list if you need to keep the data.
"""


# ======================================================================================
# Scenario 3 - finally / cleanup in a generator when the loop breaks early.
# ======================================================================================

def s3_build() -> list[str]:
    log: list[str] = []

    def managed():
        try:
            for i in range(5):
                yield i
        finally:
            log.append("cleaned up")

    for x in managed():          # consumed fully -> finally runs
        if x == 99:
            break
    return log  # ['cleaned up']


def s3_break() -> list[str]:
    log: list[str] = []

    def managed():
        try:
            for i in range(5):
                yield i
        finally:
            log.append("cleaned up")

    gen = managed()
    for x in gen:
        if x == 2:
            break                # leave early; `gen` is still suspended
    # We never told the generator we're done, so `finally` has not run yet.
    return list(log)  # []


def s3_fix() -> list[str]:
    import contextlib

    log: list[str] = []

    def managed():
        try:
            for i in range(5):
                yield i
        finally:
            log.append("cleaned up")

    with contextlib.closing(managed()) as gen:  # close() -> finally runs
        for x in gen:
            if x == 2:
                break
    return log  # ['cleaned up']


S3_WHY = """
A generator's `finally` (and any `with` inside it) runs when the generator
finishes, is `.close()`d, or is garbage-collected. Breaking out of the loop does
neither immediately - the generator sits suspended, holding whatever resource it
opened, until GC gets to it. Close it deterministically:
`contextlib.closing(gen)`, or fully consume it.
"""


# ======================================================================================
# Scenario 4 - Getting a generator's return value.
# ======================================================================================

def _load(rows):
    n = 0
    for r in rows:
        n += 1
        yield r * 10
    return n  # how many rows were processed


def s4_build() -> tuple[list, int]:
    def driver(rows):
        count = yield from _load(rows)   # yield from surfaces the return value
        results.append(count)

    results: list[int] = []
    produced = list(driver([1, 2, 3]))
    return produced, results[0]  # ([10, 20, 30], 3)


def s4_break() -> int:
    g = _load([1, 2, 3])
    last_seen = -1
    for item in g:
        last_seen = item
    # last_seen is the last YIELDED value (30), not the return value (3).
    assert last_seen == 30
    return last_seen


def s4_fix() -> int:
    g = _load([1, 2, 3])
    try:
        while True:
            next(g)
    except StopIteration as stop:
        return stop.value  # 3


S4_WHY = """
`return value` in a generator does not yield anything - it ends iteration and
sets `StopIteration.value`. A `for` loop discards that. Read it with
`yield from` (which evaluates to the delegate's return value) or by catching
`StopIteration` and reading `.value`.
"""


SCENARIOS = [
    Scenario("Deferred validation in a generator", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Generator is single-pass", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Cleanup skipped on early break", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Capturing a generator's return value", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

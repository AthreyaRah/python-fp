"""Iterators - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/10_iterators_and_the_iterator_protocol/scenarios.py
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Iterating a consumed iterator a second time.
# ======================================================================================

def _rows():
    return iter([("id", "name"), (1, "Ada"), (2, "Bo")])  # header + data


def s1_build() -> tuple:
    it = _rows()
    header = next(it)
    data = list(it)                 # consume the rest once
    return header, data


def s1_break() -> tuple[int, int]:
    it = _rows()
    n_first = sum(1 for _ in it)    # walks it to the end
    n_second = sum(1 for _ in it)   # already exhausted
    assert (n_first, n_second) == (3, 0)
    return n_first, n_second


def s1_fix() -> tuple[int, int]:
    rows = list(_rows())            # materialise: now re-iterable
    return sum(1 for _ in rows), sum(1 for _ in rows)


S1_WHY = """
An iterator has one job: hand out the next item and remember where it stopped.
`sum(1 for _ in it)` drains it; the second pass starts at the end and yields
nothing. Only an *iterable* (list, tuple, dict) can be walked repeatedly, because
each `for` asks it for a brand-new iterator.
"""


# ======================================================================================
# Scenario 2 - An "iterable" whose __iter__ returns self.
# ======================================================================================

class GoodBag:
    def __init__(self, items):
        self._items = list(items)

    def __iter__(self):
        return iter(self._items)  # a FRESH iterator every call


class BadBag:
    def __init__(self, items):
        self._items = list(items)
        self._i = 0

    def __iter__(self):
        return self  # returns itself, sharing one position

    def __next__(self):
        if self._i >= len(self._items):
            raise StopIteration
        self._i += 1
        return self._items[self._i - 1]


def s2_build() -> list[tuple[int, int]]:
    bag = GoodBag([1, 2, 3])
    return [(a, b) for a in bag for b in bag]  # 9 pairs - nested loops both work


def s2_break() -> list[tuple[int, int]]:
    bag = BadBag([1, 2, 3])
    pairs = [(a, b) for a in bag for b in bag]
    # The inner loop exhausts the shared position on the first outer step.
    assert pairs == [(1, 2), (1, 3)]
    return pairs


def s2_fix() -> list[tuple[int, int]]:
    bag = GoodBag([1, 2, 3])
    return [(a, b) for a in bag for b in bag]


S2_WHY = """
An *iterable* should return a NEW iterator from `__iter__` so independent loops
don't interfere. `BadBag.__iter__` returns `self`, so the outer and inner loops
share one `self._i`; the inner loop runs it to the end during the first outer
iteration and everything stops. Keep the two roles separate: the container's
`__iter__` builds a small iterator object (or is a generator).
"""


# ======================================================================================
# Scenario 3 - A leaked StopIteration inside a generator (PEP 479).
# ======================================================================================

def s3_build() -> list[int]:
    def take_pairs(it):
        it = iter(it)
        while True:
            try:
                a = next(it)
                b = next(it)
            except StopIteration:
                return          # clean end of generator
            yield a + b

    return list(take_pairs([1, 2, 3, 4, 5]))  # [3, 7] - the lone 5 is dropped


def s3_break() -> str:
    def take_pairs(it):
        it = iter(it)
        while True:
            a = next(it)        # when exhausted, this StopIteration escapes...
            b = next(it)
            yield a + b

    try:
        list(take_pairs([1, 2, 3]))  # ...and PEP 479 turns it into RuntimeError
    except RuntimeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> list[int]:
    def take_pairs(it):
        it = iter(it)
        while True:
            a = next(it, None)
            b = next(it, None)
            if a is None or b is None:
                return
            yield a + b

    return list(take_pairs([1, 2, 3]))  # [3]


S3_WHY = """
Since PEP 479 (Python 3.7+), a `StopIteration` that bubbles out of a generator
body is replaced with `RuntimeError` - otherwise a stray `next()` hitting the end
would silently truncate the generator and hide bugs. Handle exhaustion
explicitly: `next(it, default)` or a `try/except StopIteration: return`.
"""


# ======================================================================================
# Scenario 4 - A "peek" that consumes the item.
# ======================================================================================

def s4_build() -> list[int]:
    it = iter([10, 20, 30, 40])
    first = next(it)
    rest = itertools.chain([first], it)  # put the peeked item back
    return list(rest)  # [10, 20, 30, 40]


def s4_break() -> list[int]:
    it = iter([10, 20, 30, 40])
    _peek = next(it)                # look at the first item...
    processed = [x for x in it]     # ...but the loop starts at the SECOND
    assert processed == [20, 30, 40]
    return processed


def s4_fix() -> list[int]:
    it = iter([10, 20, 30, 40])
    peek = next(it)
    it = itertools.chain([peek], it)  # or use more_itertools.peekable
    return list(it)


S4_WHY = """
`next(it)` removes the item from the stream - there is no non-destructive peek on
a bare iterator. If you consumed one to inspect it, prepend it back with
`itertools.chain([item], it)`, or wrap the iterator in something that supports
look-ahead.
"""


SCENARIOS = [
    Scenario("Re-iterating a consumed iterator", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("__iter__ returns self", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Leaked StopIteration (PEP 479)", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Peeking consumes the item", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

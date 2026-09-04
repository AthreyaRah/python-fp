"""functools - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/14_functools/scenarios.py
"""

from __future__ import annotations

import sys
from functools import cache, cached_property, partial, reduce
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - lru_cache / cache needs hashable arguments.
# ======================================================================================

def s1_build() -> int:
    @cache
    def score(items: tuple[int, ...]) -> int:   # tuple is hashable
        return sum(x * x for x in items)

    return score((1, 2, 3)) + score((1, 2, 3))  # second call is a cache hit


def s1_break() -> str:
    @cache
    def score(items: list[int]) -> int:         # list is NOT hashable
        return sum(x * x for x in items)

    try:
        return str(score([1, 2, 3]))
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> int:
    @cache
    def score(items: tuple[int, ...]) -> int:
        return sum(x * x for x in items)

    data = [1, 2, 3]
    return score(tuple(data))                   # freeze the argument at the call


S1_WHY = """
`cache` / `lru_cache` build the cache key by hashing the arguments. A `list` (or
`dict`, or `set`) has no `__hash__`, so the very first call raises
`TypeError: unhashable type`. Pass an immutable equivalent (`tuple`,
`frozenset`), or don't cache functions that take mutable containers.
"""


# ======================================================================================
# Scenario 2 - cached_property goes stale when its inputs change.
# ======================================================================================

class ReportCached:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows

    @cached_property
    def total(self) -> int:
        return sum(self.rows)


class ReportLive:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows

    @property
    def total(self) -> int:
        return sum(self.rows)


def s2_build() -> int:
    r = ReportLive([1, 2, 3])
    r.rows.append(4)
    return r.total  # 10 - recomputed each access


def s2_break() -> int:
    r = ReportCached([1, 2, 3])
    _ = r.total          # computes and caches 6
    r.rows.append(4)     # the underlying data changed...
    return r.total       # ...still 6. Stale.


def s2_fix() -> int:
    r = ReportCached([1, 2, 3])
    _ = r.total
    r.rows.append(4)
    del r.total          # drop the cached value; next access recomputes
    return r.total       # 10


S2_WHY = """
`@cached_property` computes the value on first access and stores it in the
instance's `__dict__` under the same name, which then shadows the descriptor - so
later accesses return the stored value and never call your method again. It is
correct only when the result never changes. Use a plain `@property` for
derived-from-mutable-state values, or invalidate with `del obj.attr`.
"""


# ======================================================================================
# Scenario 3 - reduce over a possibly-empty iterable with no initializer.
# ======================================================================================

def s3_build() -> int:
    rows: list[int] = []                       # could be empty
    return reduce(lambda a, b: a + b, rows, 0)  # initializer -> safe -> 0


def s3_break() -> str:
    rows: list[int] = []
    try:
        return str(reduce(lambda a, b: a + b, rows))  # no initializer
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s3_fix() -> int:
    rows = [10, 20, 30]
    return reduce(lambda a, b: a + b, rows, 0)  # 60, and 0 for the empty case


S3_WHY = """
`reduce(f, seq)` with no initializer takes `seq[0]` as the starting accumulator.
If `seq` is empty there is nothing to start from, so it raises
`TypeError: reduce() of empty iterable with no initial value`. Always pass the
identity element as the third argument (`0` for sum, `1` for product, `""` for
concat) when the input can be empty. Better yet, use `sum` / `math.prod` /
`"".join`.
"""


# ======================================================================================
# Scenario 4 - partial prepends positional arguments.
# ======================================================================================

def s4_build():
    from_hex = partial(int, base=16)   # fix the KEYWORD arg
    return from_hex("ff")  # 255


def s4_break() -> str:
    from_hex = partial(int, 16)        # fixes the FIRST positional -> int(16, "ff")
    try:
        return str(from_hex("ff"))
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s4_fix():
    from_hex = partial(int, base=16)
    return from_hex("ff")


S4_WHY = """
`partial(func, *args, **kwargs)` remembers `args` to PREPEND and `kwargs` to
merge. `partial(int, 16)` means "call `int(16, <later args>)`", so
`from_hex("ff")` becomes `int(16, "ff")` -> TypeError. To fix a parameter that is
not the first positional, bind it by keyword: `partial(int, base=16)`.
"""


SCENARIOS = [
    Scenario("cache needs hashable arguments", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("cached_property goes stale", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("reduce on empty with no initializer", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("partial prepends positionals", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

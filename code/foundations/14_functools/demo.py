"""functools - the practice snippet.

Run it:  python code/foundations/14_functools/demo.py

`functools` is higher-order-function plumbing:
- cache / lru_cache : memoise a pure function by its (hashable) arguments
- partial           : pre-fill some arguments, get a new callable
- reduce            : fold a binary function over an iterable
- singledispatch    : pick an implementation by the type of the first argument
- cached_property   : a property computed once, then stored on the instance
- total_ordering    : fill in <, <=, >, >= from __eq__ and one of them
- wraps             : copy metadata from a wrapped function (see decorators)
"""

from __future__ import annotations

import functools
from functools import cached_property, partial, reduce, singledispatch


@functools.cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def caching() -> None:
    print("fib(30) =", fib(30))
    print("cache_info:", fib.cache_info())  # hits/misses/currsize


def partials() -> None:
    from_hex = partial(int, base=16)           # fix a keyword argument
    print("from_hex('ff') =", from_hex("ff"))
    line = partial(print, end=" | ")           # fix a keyword for print
    line("a"); line("b"); print("c")


def folding() -> None:
    nums = [3, 1, 4, 1, 5, 9]
    print("product via reduce:", reduce(lambda a, b: a * b, nums))
    print("reduce with initializer on []:", reduce(lambda a, b: a + b, [], 0))


@singledispatch
def describe(value) -> str:
    return f"something: {value!r}"


@describe.register
def _(value: int) -> str:
    return f"int {value} ({'even' if value % 2 == 0 else 'odd'})"


@describe.register
def _(value: list) -> str:
    return f"list of {len(value)}"


def dispatch() -> None:
    for v in (10, [1, 2, 3], "hi"):
        print("  describe:", describe(v))


class Dataset:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows

    @cached_property
    def total(self) -> int:
        print("    (computing total...)")
        return sum(self.rows)


def cached_props() -> None:
    d = Dataset([1, 2, 3, 4])
    print("  first access:", d.total)
    print("  second access:", d.total, "(no recompute)")


@functools.total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.t = (major, minor)

    def __eq__(self, other): return self.t == other.t
    def __lt__(self, other): return self.t < other.t
    def __repr__(self): return f"v{self.t[0]}.{self.t[1]}"


def ordering() -> None:
    v1, v2 = Version(1, 2), Version(1, 10)
    print("  v1 < v2:", v1 < v2, "| v1 >= v2:", v1 >= v2, "(>= synthesised)")


def main() -> None:
    caching()
    print()
    partials()
    print()
    folding()
    print()
    dispatch()
    print()
    cached_props()
    print()
    ordering()


if __name__ == "__main__":
    main()

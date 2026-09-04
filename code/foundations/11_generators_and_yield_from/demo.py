"""Generators & yield from - the practice snippet.

Run it:  python code/foundations/11_generators_and_yield_from/demo.py

Mental model:
- A function containing `yield` is a GENERATOR FUNCTION. Calling it runs NOTHING;
  it returns a generator object (an iterator).
- Each `next()` runs the body until the next `yield`, hands back that value, and
  FREEZES the frame - locals and the instruction pointer are kept.
- `return value` in a generator ends it and stashes `value` in
  `StopIteration.value` (which `yield from` reads).
- `yield from sub` delegates to another iterator: yields all of its items and
  evaluates to its return value.
"""

from __future__ import annotations

import sys


def runs_lazily() -> None:
    def chatty():
        print("  >> body starts")
        yield 1
        print("  >> resumed after first yield")
        yield 2
        print("  >> body ends")

    g = chatty()
    print("called chatty(); body has NOT run yet")
    print("next ->", next(g))
    print("next ->", next(g))


def memory_generator_vs_list() -> None:
    n = 5_000_000
    gen = (x for x in range(n))
    print(f"generator over {n:,} items: {sys.getsizeof(gen)} bytes")
    print("sum through it:", sum(gen))


def yield_from_delegates() -> None:
    def leaves(tree):
        for node in tree:
            if isinstance(node, list):
                yield from leaves(node)   # recurse without manual re-yield loop
            else:
                yield node

    print("flatten nested list:", list(leaves([1, [2, [3, 4], 5], [6]])))


def generator_pipeline() -> None:
    def read_lines():
        yield from ["12", "not-a-number", "7", "", "5"]

    def to_ints(lines):
        for line in lines:
            try:
                yield int(line)
            except ValueError:
                continue

    def running_total(nums):
        total = 0
        for n in nums:
            total += n
            yield total

    print("pipeline running totals:", list(running_total(to_ints(read_lines()))))


def return_value_via_stopiteration() -> None:
    def counter(items):
        n = 0
        for x in items:
            n += 1
            yield x
        return n  # the count

    g = counter("abc")
    try:
        while True:
            next(g)          # the StopIteration that ENDS it carries the value
    except StopIteration as stop:
        print("generator's return value:", stop.value)


def main() -> None:
    runs_lazily()
    print()
    memory_generator_vs_list()
    print()
    yield_from_delegates()
    print()
    generator_pipeline()
    print()
    return_value_via_stopiteration()


if __name__ == "__main__":
    main()

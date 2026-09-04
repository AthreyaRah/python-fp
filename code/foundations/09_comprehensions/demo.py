"""Comprehensions & generator expressions - the practice snippet.

Run it:  python code/foundations/09_comprehensions/demo.py

Mental model:
- A comprehension `[expr for x in it if cond]` builds a whole container NOW,
  eagerly, in one expression. `[]` -> list, `{}` -> set or dict, and it runs in
  its own scope (the loop variable does not leak).
- A generator expression `(expr for x in it if cond)` has identical syntax with
  parentheses but is LAZY: it computes each item on demand, once, and is
  exhausted after one pass.
"""

from __future__ import annotations

import sys


def the_four_forms() -> None:
    nums = range(6)
    print("list :", [n * n for n in nums])
    print("set  :", {n % 3 for n in nums})
    print("dict :", {n: n * n for n in nums})
    print("gen  :", (n * n for n in nums))  # a generator object, not the values


def eager_vs_lazy_memory() -> None:
    n = 1_000_000
    list_bytes = sys.getsizeof([x for x in range(n)])
    gen_bytes = sys.getsizeof(x for x in range(n))
    print(f"list comp of {n:,} ints: {list_bytes:>10,} bytes")
    print(f"generator expression   : {gen_bytes:>10,} bytes  (holds no items)")
    print("sum via genexp (no intermediate list):", sum(x for x in range(n)))


def nested_reads_left_to_right() -> None:
    matrix = [[1, 2, 3], [4, 5, 6]]
    flat = [x for row in matrix for x in row]  # same order as nested for-loops
    print("flatten:", flat)
    pairs = [(a, b) for a in "xy" for b in (1, 2)]
    print("cartesian:", pairs)


def condition_vs_ternary() -> None:
    nums = range(6)
    print("filter (if at end)    :", [n for n in nums if n % 2 == 0])
    print("map    (ternary front):", [n if n % 2 == 0 else -n for n in nums])


def loop_var_does_not_leak() -> None:
    data = [1, 2, 3]
    squares = [v * v for v in data]
    print("squares:", squares, "| is 'v' defined out here?", "v" in dir())


def main() -> None:
    the_four_forms()
    print()
    eager_vs_lazy_memory()
    print()
    nested_reads_left_to_right()
    print()
    condition_vs_ternary()
    print()
    loop_var_does_not_leak()


if __name__ == "__main__":
    main()

"""Idioms & anti-patterns - the practice snippet.

Run it:  python code/foundations/43_idioms_and_anti_patterns/demo.py

"Pythonic" means working with the language's grain - truthiness, the iteration
protocols, EAFP, unpacking, comprehensions, the standard library - instead of
translating idioms from another language. This is a tour of the small stuff.
Each pair below produces the same result; the second form is the idiomatic one.
"""

from __future__ import annotations

from collections import Counter


def iteration() -> None:
    names = ["ada", "grace", "linus"]
    ages = [36, 45, 54]

    # un-Pythonic: manual index bookkeeping
    out1 = []
    for i in range(len(names)):
        out1.append(f"{names[i]} is {ages[i]}")

    # Pythonic: zip / enumerate
    out2 = [f"{n} is {a}" for n, a in zip(names, ages)]
    print("zip vs range(len):", out1 == out2)


def truthiness() -> None:
    def label(items):
        return "empty" if not items else f"{len(items)} items"

    print("truthiness:", label([]), "|", label([1, 2, 3]))


def unpacking() -> None:
    first, *middle, last = [1, 2, 3, 4, 5]
    print("unpacking:", first, middle, last)
    a, b = b_swap = (1, 2)
    a, b = b, a
    print("swap without a temp:", a, b, "| tuple was", b_swap)


def dict_idioms() -> None:
    words = "the cat the dog the bird".split()
    # Pythonic tally
    counts = Counter(words)
    print("Counter:", counts.most_common(1))

    prices = {"apple": 3}
    print("get with default:", prices.get("banana", 0))
    prices.setdefault("banana", []).append(1)
    print("setdefault:", prices["banana"])


def eafp() -> None:
    config = {"retries": "3"}
    # EAFP: try it, handle the failure
    try:
        retries = int(config["retries"])
    except (KeyError, ValueError):
        retries = 1
    print("EAFP parse:", retries)


def comprehension_over_map_filter() -> None:
    nums = range(10)
    old = list(map(lambda x: x * x, filter(lambda x: x % 2 == 0, nums)))
    new = [x * x for x in nums if x % 2 == 0]
    print("comprehension vs map/filter/lambda:", old == new)


def main() -> None:
    iteration()
    truthiness()
    unpacking()
    dict_idioms()
    eafp()
    comprehension_over_map_filter()


if __name__ == "__main__":
    main()

"""itertools - the practice snippet.

Run it:  python code/foundations/15_itertools/demo.py

`itertools` is a set of lazy iterator building blocks. They compose: each returns
an iterator, so you can pipe them without building intermediate lists.
- infinite   : count, cycle, repeat        (always bound with islice / takewhile)
- slicing    : islice, takewhile, dropwhile
- combining  : chain, chain.from_iterable, zip_longest, pairwise
- grouping   : groupby (CONSECUTIVE keys - sort first), accumulate
- products   : product, permutations, combinations
"""

from __future__ import annotations

import itertools
from itertools import accumulate, chain, groupby, islice, pairwise


def bounded_infinite() -> None:
    first_5_odd = list(islice(itertools.count(1, 2), 5))
    print("islice(count(1, 2), 5):", first_5_odd)


def flattening() -> None:
    rows = [[1, 2], [3, 4], [5]]
    print("chain.from_iterable:", list(chain.from_iterable(rows)))


def running_stats() -> None:
    prices = [10, 8, 12, 7, 15, 6]
    print("running max:", list(accumulate(prices, max)))
    print("cumulative sum:", list(accumulate(prices)))


def deltas() -> None:
    readings = [3, 5, 4, 9, 9, 2]
    print("pairwise diffs:", [b - a for a, b in pairwise(readings)])


def grouping() -> None:
    people = [("eng", "Ada"), ("eng", "Cy"), ("data", "Bo"), ("data", "Di")]
    people.sort(key=lambda p: p[0])  # groupby needs the key column sorted
    for team, members in groupby(people, key=lambda p: p[0]):
        print(f"  {team}: {[name for _, name in members]}")


def combinatorics() -> None:
    print("product:", list(itertools.product([0, 1], repeat=2)))
    print("combinations:", list(itertools.combinations("abc", 2)))


def main() -> None:
    bounded_infinite()
    print()
    flattening()
    print()
    running_stats()
    print()
    deltas()
    print()
    grouping()
    print()
    combinatorics()


if __name__ == "__main__":
    main()

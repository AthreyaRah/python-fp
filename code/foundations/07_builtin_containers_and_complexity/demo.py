"""list, tuple, dict, set: internals & complexity - the practice snippet.

Run it:  python code/foundations/07_builtin_containers_and_complexity/demo.py

Mental model:
- list  : a resizable array of object pointers, laid out contiguously. Index and
          append are O(1); insert/delete/`in` near the front are O(n).
- tuple : a fixed-size array. Immutable, a bit smaller, hashable if its items are.
- dict  : a hash table. get / set / del / `in` are O(1) average. Remembers
          insertion order (since 3.7).
- set   : a hash table with keys only. `in` is O(1) average. No order.
The single most common performance bug is using `x in some_list` in a loop.
"""

from __future__ import annotations

import sys
import time


def membership_cost() -> None:
    n = 20_000
    data = list(range(n))
    as_set = set(data)
    probes = range(n - 500, n + 500)  # half hits, half misses, all near the end

    t0 = time.perf_counter()
    sum(1 for p in probes if p in data)  # O(n) scan each time
    list_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    sum(1 for p in probes if p in as_set)  # O(1) hash lookup each time
    set_ms = (time.perf_counter() - t0) * 1000

    print(f"1000 membership checks over {n} items:")
    print(f"  x in list -> {list_ms:7.2f} ms")
    print(f"  x in set  -> {set_ms:7.2f} ms   ({list_ms / max(set_ms, 1e-9):.0f}x faster)")


def list_over_allocates() -> None:
    lst: list[int] = []
    sizes = []
    last = None
    for i in range(17):
        size = sys.getsizeof(lst)
        if size != last:
            sizes.append((i, size))
            last = size
        lst.append(i)
    print("list grows in chunks (len -> bytes):", sizes)


def tuple_is_leaner_and_hashable() -> None:
    print("getsizeof([1,2,3]) =", sys.getsizeof([1, 2, 3]),
          "| getsizeof((1,2,3)) =", sys.getsizeof((1, 2, 3)))
    print("hash((1,2,3)) works:", hash((1, 2, 3)) is not None)
    try:
        hash([1, 2, 3])
    except TypeError as exc:
        print("hash([1,2,3]) ->", exc)


def dict_keeps_insertion_order() -> None:
    d = {}
    for k in ["z", "a", "m", "b"]:
        d[k] = k.upper()
    print("dict iterates in insertion order:", list(d))


def main() -> None:
    membership_cost()
    print()
    list_over_allocates()
    print()
    tuple_is_leaner_and_hashable()
    print()
    dict_keeps_insertion_order()


if __name__ == "__main__":
    main()

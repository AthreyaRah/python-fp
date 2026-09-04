"""Container internals & complexity - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/07_builtin_containers_and_complexity/scenarios.py
"""

from __future__ import annotations

import sys
import time
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - O(n^2) membership: `x in list` inside a loop.
# ======================================================================================

def _find_duplicates(seq, seen_factory):
    seen = seen_factory()
    dups = []
    for x in seq:
        if x in seen:          # cost depends on what `seen` is
            dups.append(x)
        else:
            seen.append(x) if isinstance(seen, list) else seen.add(x)
    return dups


def s1_build() -> float:
    data = list(range(4_000)) + list(range(1_000))
    t0 = time.perf_counter()
    _find_duplicates(data, set)      # `in` on a set: O(1) each
    return round((time.perf_counter() - t0) * 1000, 1)


def s1_break() -> bool:
    data = list(range(4_000)) + list(range(1_000))
    t0 = time.perf_counter()
    _find_duplicates(data, list)     # `in` on a list: O(n) each -> O(n^2) total
    list_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    _find_duplicates(data, set)
    set_ms = (time.perf_counter() - t0) * 1000
    return list_ms > set_ms * 5      # list version is dramatically slower


def s1_fix() -> list[int]:
    data = [1, 2, 2, 3, 1]
    return _find_duplicates(data, set)  # [2, 1]


S1_WHY = """
`x in a_list` walks the list element by element - O(n). Do that once per item in
an n-item loop and you have O(n^2): 5000 items -> ~12 million comparisons.
`x in a_set` hashes x and checks one bucket - O(1). Membership-heavy code wants a
set or dict, not a list.
"""


# ======================================================================================
# Scenario 2 - Removing items from a list while iterating it.
# ======================================================================================

def s2_build() -> list[int]:
    nums = [1, 2, 3, 4, 5, 6]
    return [x for x in nums if x % 2 != 0]  # build a new list -> [1, 3, 5]


def s2_break() -> list[int]:
    nums = [1, 2, 2, 3, 4]
    for x in nums:
        if x % 2 == 0:
            nums.remove(x)     # mutating the list the for-loop is walking
    # A "2" survives: removing the first 2 shifts the second 2 into an index the
    # loop has already passed.
    assert nums == [1, 2, 3], "an even 2 survived the filter"
    return nums


def s2_fix() -> list[int]:
    nums = [1, 2, 3, 4, 5, 6]
    for x in nums[:]:          # iterate a copy
        if x % 2 == 0:
            nums.remove(x)
    return nums


S2_WHY = """
A list iterator holds an integer index and increments it each step. `list.remove`
shifts every later element left by one. After removing index 1, the element that
was at index 2 is now at index 1 - but the iterator has moved on to index 2, so
that element is never examined. Build a new list (comprehension / filter) or
iterate a copy (`nums[:]`).
"""


# ======================================================================================
# Scenario 3 - Building a sequence with insert(0, ...).
# ======================================================================================

def s3_build() -> float:
    n = 30_000
    t0 = time.perf_counter()
    dq: deque[int] = deque()
    for i in range(n):
        dq.appendleft(i)      # O(1) at either end
    return round((time.perf_counter() - t0) * 1000, 1)


def s3_break() -> bool:
    n = 30_000
    t0 = time.perf_counter()
    lst: list[int] = []
    for i in range(n):
        lst.insert(0, i)      # O(n): shift everything right every time
    list_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    dq: deque[int] = deque()
    for i in range(n):
        dq.appendleft(i)
    deque_ms = (time.perf_counter() - t0) * 1000
    return list_ms > deque_ms * 10


def s3_fix() -> list[int]:
    # If you need a list and prepend order: append, then reverse once (O(n)).
    lst = []
    for i in range(5):
        lst.append(i)
    lst.reverse()
    return lst  # [4, 3, 2, 1, 0]


S3_WHY = """
A list stores elements contiguously, so `insert(0, x)` must move all n existing
elements one slot to the right - O(n), making the loop O(n^2). `collections.deque`
is a doubly linked list of blocks: `appendleft` / `popleft` are O(1). If you must
end up with a list, append and `reverse()` once.
"""


# ======================================================================================
# Scenario 4 - Deduplicating while preserving order.
# ======================================================================================

def s4_build() -> list[str]:
    seq = ["b", "a", "b", "c", "a", "d"]
    return list(dict.fromkeys(seq))  # ['b', 'a', 'c', 'd'] - order kept


def s4_break() -> bool:
    seq = list("the quick brown fox")
    via_set = list(set(seq))
    via_dict = list(dict.fromkeys(seq))
    # set() drops duplicates but also drops order; result is not the input order.
    return via_set != via_dict and sorted(via_set) == sorted(via_dict)


def s4_fix() -> list[int]:
    seq = [3, 1, 3, 2, 1, 4]
    return list(dict.fromkeys(seq))  # [3, 1, 2, 4]


S4_WHY = """
A set is a hash table with no notion of order, so `list(set(seq))` returns items
in bucket order, which depends on the hash values, not on when you inserted them.
A dict preserves insertion order, so `dict.fromkeys(seq)` dedups (keys are
unique) while keeping first-seen order. `list(dict.fromkeys(seq))` is the
idiom.
"""


SCENARIOS = [
    Scenario("O(n^2) membership", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Removing while iterating", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("insert(0, x) in a loop", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Dedup preserving order", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

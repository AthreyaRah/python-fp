"""itertools - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/15_itertools/scenarios.py
"""

from __future__ import annotations

import sys
from itertools import chain, groupby, zip_longest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

WORDS = ["ant", "bee", "arc", "cat", "auk", "bat"]


# ======================================================================================
# Scenario 1 - groupby without sorting first.
# ======================================================================================

def _by_first_letter(words):
    return {k: [w for w in g] for k, g in groupby(words, key=lambda w: w[0])}


def s1_build() -> dict:
    return _by_first_letter(sorted(WORDS))  # {'a': [...3...], 'b': [...2...], 'c': [...]}


def s1_break() -> int:
    grouped = _by_first_letter(WORDS)  # NOT sorted
    # 'a' appears as several separate runs; only the last survives in the dict,
    # and no group is complete.
    assert grouped["a"] == ["auk"], "only the final 'a' run remains"
    return len(grouped["a"])  # 1, not 3


def s1_fix() -> list[int]:
    grouped = _by_first_letter(sorted(WORDS, key=lambda w: w[0]))
    return [len(v) for v in grouped.values()]  # [3, 2, 1]


S1_WHY = """
`groupby` yields a new group every time the key CHANGES between consecutive
items - it does not gather all items with the same key globally. On unsorted
input, "ant" and "arc" and "auk" form three separate 'a' groups. Sort by the same
key first (`sorted(data, key=k)`), exactly like SQL `GROUP BY` needs an ordering
or a hash step.
"""


# ======================================================================================
# Scenario 2 - groupby's sub-iterators are only valid until you advance.
# ======================================================================================

def s2_build() -> list[tuple[str, list[str]]]:
    data = sorted(WORDS)
    return [(k, list(g)) for k, g in groupby(data, key=lambda w: w[0])]  # materialise now


def s2_break() -> list[list[str]]:
    data = sorted(WORDS)
    groups = list(groupby(data, key=lambda w: w[0]))  # keep the group objects
    # By the time we read them, the shared underlying iterator has moved on.
    result = [list(g) for _, g in groups]
    assert result == [[], [], []], "every group came out empty"
    return result


def s2_fix() -> list[list[str]]:
    data = sorted(WORDS)
    return [list(g) for _, g in groupby(data, key=lambda w: w[0])]


S2_WHY = """
`groupby` does not copy anything: each group iterator is a view over the same
source iterator, positioned at that group's start. Advancing to the next group
(which `list(groupby(...))` does immediately) drags the source past the previous
group, so reading it later yields nothing. Consume each group - `list(g)` - before
moving to the next, e.g. inside the same comprehension.
"""


# ======================================================================================
# Scenario 3 - chain(list_of_lists) instead of chain.from_iterable.
# ======================================================================================

def s3_build() -> list[int]:
    rows = [[1, 2], [3, 4], [5]]
    return list(chain.from_iterable(rows))  # [1, 2, 3, 4, 5]


def s3_break() -> list:
    rows = [[1, 2], [3, 4], [5]]
    out = list(chain(rows))  # chain sees ONE argument: the outer list
    assert out == [[1, 2], [3, 4], [5]], "yielded the sublists, not their items"
    return out


def s3_fix() -> list[int]:
    rows = [[1, 2], [3, 4], [5]]
    return list(chain(*rows))  # or chain.from_iterable(rows)


S3_WHY = """
`chain(*iterables)` treats each ARGUMENT as an iterable to concatenate.
`chain(rows)` passes a single argument - the list of rows - so it iterates that
once, yielding the rows themselves. Use `chain.from_iterable(rows)` (lazy, no
unpacking) or `chain(*rows)` (unpacks eagerly).
"""


# ======================================================================================
# Scenario 4 - zip stops at the shortest input.
# ======================================================================================

def s4_build() -> dict:
    headers = ["id", "name", "email", "city"]
    row = [1, "Ada"]  # short row - two fields missing
    return dict(zip_longest(headers, row, fillvalue=None))


def s4_break() -> dict:
    headers = ["id", "name", "email", "city"]
    row = [1, "Ada"]
    record = dict(zip(headers, row))  # silently drops 'email' and 'city'
    assert set(record) == {"id", "name"}, "two columns vanished with no warning"
    return record


def s4_fix() -> dict:
    headers = ["id", "name", "email", "city"]
    row = [1, "Ada"]
    try:
        return dict(zip(headers, row, strict=True))  # raises on length mismatch
    except ValueError:
        return dict(zip_longest(headers, row, fillvalue=None))


S4_WHY = """
`zip` stops as soon as the shortest input is exhausted and gives no indication
that the others had more (or less). For a row that is meant to match a header,
that is silent data loss. Use `strict=True` (Python 3.10+) to turn a length
mismatch into a `ValueError`, or `itertools.zip_longest(fillvalue=...)` when short
rows are expected.
"""


SCENARIOS = [
    Scenario("groupby without sorting", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("groupby sub-iterator lifetime", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("chain vs chain.from_iterable", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("zip stops at the shortest", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

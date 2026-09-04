"""Names, objects & references — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/02_names_objects_references/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 — Aliasing: two names, one list.
# ======================================================================================

def s1_build() -> list[int]:
    original = [1, 2, 3]
    snapshot = list(original)  # a real copy
    original.append(4)
    assert snapshot == [1, 2, 3]
    return snapshot


def s1_break() -> list[int]:
    original = [1, 2, 3]
    snapshot = original  # NOT a copy — a second label on the same list
    original.append(4)
    assert snapshot == [1, 2, 3, 4], "snapshot changed under us"
    return snapshot  # [1, 2, 3, 4]


def s1_fix() -> bool:
    original = [1, 2, 3]
    snapshot = original[:]  # slice builds a new list
    original.append(4)
    return snapshot == [1, 2, 3] and snapshot is not original


S1_WHY = """
`snapshot = original` copies the reference, not the object. Both names point at
one list; `original.append(4)` mutates that shared object, so `snapshot` "sees"
the change. A copy (`list(x)`, `x[:]`, `copy.copy`) makes a second object.
"""


# ======================================================================================
# Scenario 2 — Identity vs equality: `is` is not `==`.
# ======================================================================================

def s2_build() -> bool:
    def is_sentinel(x: object) -> bool:
        return x is None  # correct: None is a singleton

    return is_sentinel(None) and not is_sentinel(0) and not is_sentinel("")


def s2_break() -> list[bool]:
    def config_equals(x: int) -> bool:
        threshold = int("1000")  # a distinct int object, not the cached range
        return x is threshold  # bug: identity check instead of equality

    # 1000 is outside CPython's small-int cache (-5..256), so the caller's 1000
    # and the function's `threshold` are different objects: `is` is False.
    results = [config_equals(1000), config_equals(500 + 500)]
    assert results == [False, False], "identity check on 1000 should fail"
    return results


def s2_fix() -> bool:
    def config_equals(x: int) -> bool:
        return x == 1000  # value equality

    return config_equals(int("1000")) and config_equals(999 + 1)


S2_WHY = """
`is` compares object identity (id()); `==` compares value. Small integers
(-5..256) and some short strings are cached and reused by CPython, so `is` can
appear to work — then breaks for 257, or 1000, or a string built at runtime.
Rule: `is` only for `None`/`True`/`False`; `==` for everything else.
"""


# ======================================================================================
# Scenario 3 — Passing to a function: rebinding vs mutating.
# ======================================================================================

def s3_build() -> list[int]:
    def with_extra(seq: list[int], value: int) -> list[int]:
        return seq + [value]  # new list; caller's list untouched

    base = [1, 2]
    extended = with_extra(base, 3)
    assert base == [1, 2] and extended == [1, 2, 3]
    return extended


def s3_break() -> list[int]:
    def normalise_in_place(seq: list[int]) -> list[int]:
        seq = [x / max(seq) for x in seq]  # rebinds the LOCAL name only
        return seq

    caller = [2, 4, 8]
    result = normalise_in_place(caller)
    # The caller expected `caller` to be normalised too (a common wrong mental
    # model). It was not — only the returned value is.
    assert caller == [2, 4, 8], "caller list unchanged despite the name"
    return result


def s3_fix() -> list[int]:
    def normalise_in_place(seq: list[int]) -> None:
        top = max(seq)
        seq[:] = [x / top for x in seq]  # slice-assign mutates the object

    caller = [2, 4, 8]
    normalise_in_place(caller)
    return caller  # [0.25, 0.5, 1.0]


S3_WHY = """
Arguments are passed by assignment: the parameter name is bound to the same
object the caller passed. `seq = [...]` inside the function rebinds that local
name to a new object — the caller's binding is untouched. `seq[:] = [...]` and
`seq.append(...)` mutate the shared object, which the caller sees.
"""


# ======================================================================================
# Scenario 4 — The mutable default argument.
# ======================================================================================

def s4_build() -> list[list[int]]:
    def push(value: int, into: list[int] | None = None) -> list[int]:
        into = [] if into is None else into
        into.append(value)
        return into

    return [push(1), push(2), push(3)]  # [[1], [2], [3]]


def s4_break() -> list[list[int]]:
    def push(value: int, into: list[int] = []) -> list[int]:  # the bug
        into.append(value)
        return into

    calls = [push(1), push(2), push(3)]
    assert calls == [[1, 2, 3], [1, 2, 3], [1, 2, 3]], "one shared list"
    assert calls[0] is calls[1] is calls[2]
    return calls


def s4_fix() -> bool:
    def push(value: int, into: list[int] | None = None) -> list[int]:
        into = [] if into is None else into
        into.append(value)
        return into

    a, b = push(1), push(2)
    return a == [1] and b == [2] and a is not b


S4_WHY = """
The default value `[]` is evaluated once, when `def` runs, and stored on the
function object (`push.__defaults__`). Every call that omits `into` binds the
parameter to that one list, so appends accumulate across calls. The sentinel
pattern (`None`, then build `[]` inside the body) creates a fresh list per call.
"""


SCENARIOS = [
    Scenario("Aliasing: two names, one list", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Identity vs equality", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Rebinding vs mutating an argument", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("The mutable default argument", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""Mutability — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/03_mutability_and_the_default_arg_trap/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 — `+=` on a list stored inside a tuple.
# ======================================================================================

def s1_build() -> tuple:
    row = (["a", "b"], "meta")
    row[0].append("c")  # mutate the list; do not touch the tuple slot
    return row  # (['a', 'b', 'c'], 'meta')


def s1_break() -> tuple:
    row = (["a", "b"], "meta")
    try:
        row[0] += ["c"]  # <- both mutates the list AND tries to rebind row[0]
    except TypeError:
        pass
    # The TypeError fires, yet the list was already extended.
    assert row[0] == ["a", "b", "c"], "the mutation happened before the error"
    return row


def s1_fix() -> tuple:
    row = (["a", "b"], "meta")
    row[0].append("c")           # explicit in-place, no rebinding attempt
    return row


S1_WHY = """
`row[0] += ["c"]` compiles to: load `row[0]`, call `list.__iadd__` on it (which
extends the list in place and returns it), then STORE_SUBSCR back into `row[0]`.
The store into a tuple raises TypeError — but the in-place extend already ran.
Use `row[0].append(...)` / `.extend(...)` when the container is immutable, or
make the outer container a list.
"""


# ======================================================================================
# Scenario 2 — Mutable default argument (a dict this time).
# ======================================================================================

def s2_build() -> list[dict]:
    def record(key: str, value: int, store: dict | None = None) -> dict:
        store = {} if store is None else store
        store[key] = value
        return store

    return [record("a", 1), record("b", 2)]  # [{'a': 1}, {'b': 2}]


def s2_break() -> list[dict]:
    def record(key: str, value: int, store: dict = {}) -> dict:  # the bug
        store[key] = value
        return store

    calls = [record("a", 1), record("b", 2), record("c", 3)]
    assert calls[0] == {"a": 1, "b": 2, "c": 3}, "one shared dict"
    assert calls[0] is calls[1] is calls[2]
    return calls


def s2_fix() -> bool:
    def record(key: str, value: int, store: dict | None = None) -> dict:
        store = {} if store is None else store
        store[key] = value
        return store

    a, b = record("a", 1), record("b", 2)
    return a == {"a": 1} and b == {"b": 2} and a is not b


S2_WHY = """
`store={}` builds one dict when `def` executes and stashes it in
`record.__defaults__`. Every call that omits `store` mutates that same dict, so
entries pile up across calls. `None` + build-inside-the-body gives each call its
own dict.
"""


# ======================================================================================
# Scenario 3 — A mutable object used as a dict key / set member.
# ======================================================================================

def s3_build() -> dict:
    seen: dict[tuple, int] = {}
    for coord in [(0, 0), (1, 2), (0, 0)]:
        seen[coord] = seen.get(coord, 0) + 1
    return seen  # {(0, 0): 2, (1, 2): 1}


def s3_break() -> str:
    seen: dict = {}
    key = [0, 0]  # a list
    try:
        seen[key] = 1
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> dict:
    seen: dict = {}
    key = [0, 0]
    seen[tuple(key)] = 1  # freeze it first
    seen[frozenset({"a", "b"})] = 2
    return seen


S3_WHY = """
A dict/set stores items in buckets chosen by `hash(key)`. If a key could mutate,
its hash could change and the item would become unfindable — so Python forbids it
up front: mutable built-ins do not implement `__hash__`, and using one as a key
raises `TypeError: unhashable type`. Convert to an immutable equivalent
(`tuple`, `frozenset`) or a hashable value object.
"""


# ======================================================================================
# Scenario 4 — A mutable class attribute shared by all instances.
# ======================================================================================

def s4_build() -> tuple[list, list]:
    class Cart:
        def __init__(self) -> None:
            self.items: list[str] = []  # per-instance

    a, b = Cart(), Cart()
    a.items.append("apple")
    return a.items, b.items  # (['apple'], [])


def s4_break() -> tuple[list, list, bool]:
    class Cart:
        items: list[str] = []  # class attribute: ONE list for the whole class

        def add(self, x: str) -> None:
            self.items.append(x)  # mutates the shared class list

    a, b = Cart(), Cart()
    a.add("apple")
    assert b.items == ["apple"], "b sees a's item"
    return a.items, b.items, a.items is b.items


def s4_fix() -> tuple[list, list]:
    class Cart:
        def __init__(self) -> None:
            self.items: list[str] = []

        def add(self, x: str) -> None:
            self.items.append(x)

    a, b = Cart(), Cart()
    a.add("apple")
    return a.items, b.items  # (['apple'], [])


S4_WHY = """
`items = []` in the class body creates one list bound to the class object.
`self.items.append(x)` reads `items` (found on the class, since the instance has
none) and mutates it — no assignment happens, so no instance attribute is ever
created, and every instance keeps sharing the class list. Assigning
`self.items = []` in `__init__` gives each instance its own.
"""


SCENARIOS = [
    Scenario("+= on a list inside a tuple", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Mutable default argument", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Mutable object as a dict key", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Mutable class attribute", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

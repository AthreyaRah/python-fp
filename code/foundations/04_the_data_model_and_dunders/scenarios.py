"""The data model — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/04_the_data_model_and_dunders/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 — Defining __eq__ silently makes the object unhashable.
# ======================================================================================

def s1_build() -> int:
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __eq__(self, other):
            return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

        def __hash__(self):
            return hash((self.x, self.y))  # restore hashing, consistent with __eq__

    return len({Point(0, 0), Point(0, 0), Point(1, 1)})  # 2


def s1_break() -> str:
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __eq__(self, other):  # define __eq__ only
            return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    try:
        {Point(0, 0)}
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s1_fix() -> int:
    from dataclasses import dataclass

    @dataclass(frozen=True)  # generates __eq__ AND a matching __hash__
    class Point:
        x: int
        y: int

    return len({Point(0, 0), Point(0, 0), Point(1, 1)})  # 2


S1_WHY = """
Python keeps the invariant `a == b  =>  hash(a) == hash(b)`. If you override
`__eq__` but inherit `object.__hash__` (based on id), two "equal" objects could
hash differently. To stop that silently breaking sets/dicts, Python sets
`__hash__ = None` on any class that defines `__eq__` without `__hash__`, which
makes instances unhashable. Supply `__hash__` yourself, or use
`@dataclass(frozen=True)` / `NamedTuple`.
"""


# ======================================================================================
# Scenario 2 — __str__ without __repr__.
# ======================================================================================

def s2_build() -> str:
    class Money:
        def __init__(self, cents):
            self.cents = cents

        def __repr__(self):
            return f"Money(cents={self.cents})"

    return repr([Money(150), Money(99)])


def s2_break() -> bool:
    class Money:
        def __init__(self, cents):
            self.cents = cents

        def __str__(self):  # only __str__
            return f"${self.cents / 100:.2f}"

    shown = repr([Money(150)])  # containers use repr() of their items
    # You get the useless default: "[<...Money object at 0x...>]"
    return "Money object at 0x" in shown


def s2_fix() -> str:
    class Money:
        def __init__(self, cents):
            self.cents = cents

        def __repr__(self):
            return f"Money(cents={self.cents})"

        # __str__ falls back to __repr__ automatically; add one only if you want
        # a different human-facing form.
        def __str__(self):
            return f"${self.cents / 100:.2f}"

    return f"{[Money(150)]!r} and str is {Money(150)}"


S2_WHY = """
`repr()` is meant to be unambiguous and is the fallback everywhere: the REPL,
`print` of a list/dict, debuggers, logging `%r`. `str()` is the human form and
*defaults to* `__repr__` when absent. Defining only `__str__` leaves `repr()` as
`object.__repr__` (`<Money object at 0x...>`), which is what containers show.
Always define `__repr__`; add `__str__` only when you need a distinct display.
"""


# ======================================================================================
# Scenario 3 — Raising in __add__ instead of returning NotImplemented.
# ======================================================================================

def s3_build() -> object:
    class Weight:
        def __init__(self, g):
            self.g = g

        def __repr__(self):
            return f"Weight({self.g})"

        def __add__(self, other):
            if isinstance(other, Weight):
                return Weight(self.g + other.g)
            return NotImplemented  # decline politely; let Python try the reflected op

        def __radd__(self, other):
            if other == 0:          # sum() seeds the accumulator with int 0
                return self
            return self.__add__(other)

    return sum([Weight(10), Weight(5), Weight(2)])  # -> Weight(17)


def s3_break() -> str:
    class Weight:
        def __init__(self, g):
            self.g = g

        def __add__(self, other):
            if not isinstance(other, Weight):
                raise TypeError("can only add Weight to Weight")  # too aggressive
            return Weight(self.g + other.g)

    try:
        sum([Weight(10), Weight(5)])  # 0 + Weight(10) -> int.__add__ fails,
    except TypeError as exc:          # then Weight.__radd__ missing -> __add__(0) raises
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> object:
    class Weight:
        def __init__(self, g):
            self.g = g

        def __repr__(self):
            return f"Weight({self.g})"

        def __add__(self, other):
            if isinstance(other, Weight):
                return Weight(self.g + other.g)
            if other == 0:            # tolerate sum()'s starting 0
                return self
            return NotImplemented

        __radd__ = __add__

    return sum([Weight(10), Weight(5)])


S3_WHY = """
Binary operators use a negotiation: `a + b` tries `a.__add__(b)`; if that returns
the singleton `NotImplemented`, Python tries `b.__radd__(a)`; if that also
declines, it raises `TypeError`. Returning `NotImplemented` is how you say "not
my job, let someone else try". Raising instead short-circuits the negotiation, so
`sum()` (which does `0 + first`) and mixed-type expressions blow up.
"""


# ======================================================================================
# Scenario 4 — Hashing on a field you then mutate.
# ======================================================================================

def s4_build() -> bool:
    class Tag:
        def __init__(self, name):
            self._name = name  # treated as immutable identity

        def __hash__(self):
            return hash(self._name)

        def __eq__(self, other):
            return isinstance(other, Tag) and self._name == other._name

    t = Tag("urgent")
    bag = {t}
    return t in bag  # True, and stays True — we never mutate _name


def s4_break() -> bool:
    class Tag:
        def __init__(self, name):
            self.name = name  # public, mutable

        def __hash__(self):
            return hash(self.name)  # hash depends on mutable state

        def __eq__(self, other):
            return isinstance(other, Tag) and self.name == other.name

    t = Tag("urgent")
    bag = {t}
    t.name = "later"          # hash(t) changes; the set still has it in the OLD bucket
    return t in bag           # False! the object is in the set but unfindable


def s4_fix() -> bool:
    from dataclasses import dataclass

    @dataclass(frozen=True)  # fields can't be reassigned -> hash stays stable
    class Tag:
        name: str

    t = Tag("urgent")
    bag = {t}
    try:
        t.name = "later"  # FrozenInstanceError
    except Exception:
        pass
    return t in bag  # True


S4_WHY = """
A set places an item in a bucket chosen by `hash(item)` at insert time. If the
item's hash later changes (because it depends on a field you mutated), lookups
compute the *new* hash, land in a different bucket, and miss — the object is
still in the set but effectively lost. Hash only over fields that never change;
`frozen=True` enforces that.
"""


SCENARIOS = [
    Scenario("__eq__ without __hash__", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("__str__ without __repr__", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("raise vs NotImplemented in __add__", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("hashing a mutable field", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

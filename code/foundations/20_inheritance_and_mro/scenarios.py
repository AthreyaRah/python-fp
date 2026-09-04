"""Inheritance & MRO - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/20_inheritance_and_mro/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Overriding __init__ without calling super().
# ======================================================================================

def s1_build() -> str:
    class Animal:
        def __init__(self, name):
            self.name = name

    class Dog(Animal):
        def __init__(self, name, tricks):
            super().__init__(name)     # extend, don't replace
            self.tricks = tricks

    d = Dog("Rex", ["sit"])
    return f"{d.name} knows {d.tricks}"


def s1_break() -> str:
    class Animal:
        def __init__(self, name):
            self.name = name

    class Dog(Animal):
        def __init__(self, name, tricks):
            self.tricks = tricks       # forgot super().__init__(name)

    d = Dog("Rex", ["sit"])
    try:
        return d.name                  # AttributeError - never set
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> str:
    class Animal:
        def __init__(self, name):
            self.name = name

    class Dog(Animal):
        def __init__(self, name, tricks):
            super().__init__(name)
            self.tricks = tricks

    d = Dog("Rex", ["sit"])
    return f"{d.name} knows {d.tricks}"


S1_WHY = """
Defining `__init__` in a subclass REPLACES the parent's - it does not
automatically run first. If you don't call `super().__init__(...)`, the parent's
setup (here, `self.name = name`) simply never happens, and the missing attribute
surfaces later as an AttributeError far from the cause.
"""


# ======================================================================================
# Scenario 2 - Hardcoding a base call instead of super() in a diamond.
# ======================================================================================

def _diamond(use_super: bool):
    calls: list[str] = []

    class Base:
        def __init__(self):
            calls.append("Base")

    class Left(Base):
        def __init__(self):
            calls.append("Left")
            if use_super:
                super().__init__()
            else:
                Base.__init__(self)   # hardcoded

    class Right(Base):
        def __init__(self):
            calls.append("Right")
            if use_super:
                super().__init__()
            else:
                Base.__init__(self)   # hardcoded

    class Child(Left, Right):
        def __init__(self):
            calls.append("Child")
            if use_super:
                super().__init__()
            else:
                Left.__init__(self)
                Right.__init__(self)

    Child()
    return calls


def s2_build() -> list[str]:
    return _diamond(use_super=True)   # ['Child', 'Left', 'Right', 'Base'] - each once


def s2_break() -> list[str]:
    calls = _diamond(use_super=False)
    # Base runs TWICE (once from Left, once from Right) and Right is reached
    # only via the manual call - the MRO is not respected.
    assert calls.count("Base") == 2
    return calls


def s2_fix() -> list[str]:
    return _diamond(use_super=True)


S2_WHY = """
In the diamond Child(Left, Right), the MRO is Child -> Left -> Right -> Base.
`super().__init__()` in Left routes to Right (the next in the MRO of the actual
class), so Base runs exactly once at the end. Hardcoding `Base.__init__(self)` in
both Left and Right calls Base twice and skips the cooperative chain. Use
`super()` consistently in every class in the hierarchy.
"""


# ======================================================================================
# Scenario 3 - An inconsistent MRO.
# ======================================================================================

def s3_build() -> list[str]:
    class X: pass
    class Y: pass

    class P(X, Y): pass
    class Q(X, Y): pass          # same base order as P
    class R(P, Q): pass          # consistent -> fine

    return [c.__name__ for c in R.__mro__]


def s3_break() -> str:
    class X: pass
    class Y: pass

    class P(X, Y): pass
    class Q(Y, X): pass          # OPPOSITE base order

    try:
        class R(P, Q): pass      # X-before-Y and Y-before-X cannot both hold
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> list[str]:
    class X: pass
    class Y: pass

    class P(X, Y): pass
    class Q(X, Y): pass          # align the orders
    class R(P, Q): pass

    return [c.__name__ for c in R.__mro__]


S3_WHY = """
C3 linearization must produce ONE ordering consistent with every base's order.
`P(X, Y)` says X comes before Y; `Q(Y, X)` says Y before X. A class combining both
(`R(P, Q)`) demands both at once, which is impossible, so Python refuses at class
creation: `TypeError: Cannot create a consistent method resolution order`. Keep
base classes in a consistent order everywhere.
"""


# ======================================================================================
# Scenario 4 - Calling an overridable method from __init__.
# ======================================================================================

def s4_build() -> int:
    class Report:
        def __init__(self, rows):
            self.rows = rows          # set state BEFORE using it

        def summary(self):            # call this after construction, not during
            return sum(self.rows)

    r = Report([1, 2, 3])
    return r.summary()  # 6


def s4_break() -> str:
    class Report:
        def __init__(self, rows):
            self.rows = rows
            self.cached = self._compute()   # calls the (overridden) method now

        def _compute(self):
            return sum(self.rows)

    class WeightedReport(Report):
        def __init__(self, rows, weights):
            super().__init__(rows)           # _compute() runs in here...
            self.weights = weights           # ...but weights isn't set until now

        def _compute(self):
            return sum(r * w for r, w in zip(self.rows, self.weights))

    try:
        WeightedReport([1, 2, 3], [1, 1, 1])
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> int:
    class Report:
        def __init__(self, rows):
            self.rows = rows

        def compute(self):
            return sum(self.rows)

    class WeightedReport(Report):
        def __init__(self, rows, weights):
            super().__init__(rows)
            self.weights = weights

        def compute(self):
            return sum(r * w for r, w in zip(self.rows, self.weights))

    return WeightedReport([1, 2, 3], [2, 2, 2]).compute()  # compute lazily -> 12


S4_WHY = """
`self._compute()` dispatches dynamically to the MOST-DERIVED override
immediately - even though the subclass's `__init__` has not finished and
`self.weights` is not set yet - so `WeightedReport._compute` hits
`AttributeError`. Don't call overridable methods from `__init__`. Compute derived
values lazily (a method or `@property` called after construction), or make the
subclass set its state before `super().__init__()`.
"""


SCENARIOS = [
    Scenario("Overriding __init__ without super()", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Hardcoded base call in a diamond", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Inconsistent MRO", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Overridable method called from __init__", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

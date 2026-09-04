"""Classes & OOP - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/19_classes_and_oop/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - `self.x += 1` where x is a class attribute.
# ======================================================================================

def s1_build() -> tuple[int, int]:
    class Widget:
        _created = 0

        def __init__(self):
            Widget._created += 1       # rebind on the class explicitly

    a = Widget(); Widget(); Widget()
    return Widget._created, a._created  # (3, 3) - `a` has no instance attr, reads class


def s1_break() -> tuple[int, int]:
    class Widget:
        _created = 0

        def __init__(self):
            self._created += 1         # read class attr (0), write INSTANCE attr (1)

    a, b, c = Widget(), Widget(), Widget()
    # Every instance thinks _created == 1; the class counter never moved.
    assert (a._created, Widget._created) == (1, 0)
    return a._created, Widget._created


def s1_fix() -> tuple[int, int]:
    class Widget:
        _created = 0

        def __init__(self):
            type(self)._created += 1   # or Widget._created += 1

    a, b, c = Widget(), Widget(), Widget()
    return a._created, Widget._created  # (3, 3)


S1_WHY = """
`self._created += 1` expands to `self._created = self._created + 1`. The read
finds `_created` on the class (0). The write always targets the INSTANCE
`__dict__`, creating a per-instance `_created` that shadows the class one. So each
instance ends at 1 and the shared counter never changes. Rebind on the class:
`type(self)._created += 1`.
"""


# ======================================================================================
# Scenario 2 - Forgetting `self` in a method signature.
# ======================================================================================

def s2_build() -> int:
    class Box:
        def __init__(self, n):
            self.n = n

        def doubled(self):
            return self.n * 2

    return Box(21).doubled()  # 42


def s2_break() -> str:
    class Box:
        def __init__(self, n):
            self.n = n

        def doubled():             # no self
            return 0

    try:
        return str(Box(21).doubled())   # passes the instance as the 1st arg
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> int:
    class Box:
        def __init__(self, n):
            self.n = n

        def doubled(self):
            return self.n * 2

    return Box(21).doubled()


S2_WHY = """
`obj.doubled()` is sugar for `Box.doubled(obj)` - the instance is always passed as
the first positional argument. A method defined as `def doubled():` accepts zero
arguments, so the call raises
`TypeError: doubled() takes 0 positional arguments but 1 was given`. Every
instance method needs an explicit first parameter (conventionally `self`).
"""


# ======================================================================================
# Scenario 3 - Assigning to a read-only property.
# ======================================================================================

def s3_build() -> str:
    class Person:
        def __init__(self, first, last):
            self.first, self.last = first, last

        @property
        def full_name(self):
            return f"{self.first} {self.last}"

        @full_name.setter
        def full_name(self, value):
            self.first, self.last = value.split(" ", 1)

    p = Person("Ada", "L")
    p.full_name = "Grace Hopper"   # setter exists
    return p.first + "/" + p.last  # 'Grace/Hopper'


def s3_break() -> str:
    class Person:
        def __init__(self, first, last):
            self.first, self.last = first, last

        @property
        def full_name(self):
            return f"{self.first} {self.last}"

    p = Person("Ada", "L")
    try:
        p.full_name = "Grace Hopper"   # no setter -> AttributeError
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> str:
    class Person:
        def __init__(self, first, last):
            self.first, self.last = first, last

        @property
        def full_name(self):
            return f"{self.first} {self.last}"

        @full_name.setter
        def full_name(self, value):
            self.first, self.last = value.split(" ", 1)

    p = Person("Ada", "L")
    p.full_name = "Grace Hopper"
    return p.full_name


S3_WHY = """
`property` is a data descriptor: it defines `__get__` AND `__set__` on the class.
Because a data descriptor takes priority over the instance `__dict__`, assigning
`p.full_name = ...` calls the property's `__set__`, which - with no `@x.setter` -
raises `AttributeError: property 'full_name' has no setter`. Add a setter, or
make it genuinely read-only on purpose.
"""


# ======================================================================================
# Scenario 4 - Returning a value from __init__.
# ======================================================================================

def s4_build() -> int:
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y      # initialise; return nothing

    return Point(3, 4).x  # 3


def s4_break() -> str:
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y
            return (x, y)               # __init__ must return None

    try:
        Point(3, 4)
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> tuple[int, int]:
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        @classmethod
        def origin(cls) -> "Point":     # want a factory? use a classmethod
            return cls(0, 0)

    p = Point.origin()
    return p.x, p.y


S4_WHY = """
`Point(3, 4)` calls `Point.__new__` (which builds the instance) then
`Point.__init__(instance, 3, 4)` (which sets it up). `__init__`'s job is to
mutate `self`, not to produce a value - returning anything other than `None`
raises `TypeError: __init__() should return None`. If you want a construction
that returns something computed, use a `@classmethod` factory or override
`__new__`.
"""


SCENARIOS = [
    Scenario("self.x += 1 on a class attribute", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Forgetting self in a method", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Assigning to a read-only property", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Returning from __init__", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

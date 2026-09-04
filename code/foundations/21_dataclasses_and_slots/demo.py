"""dataclasses & __slots__ - the practice snippet.

Run it:  python code/foundations/21_dataclasses_and_slots/demo.py

Mental model:
- `@dataclass` reads the class-level annotated fields and GENERATES `__init__`,
  `__repr__`, and `__eq__` (and, opt-in, ordering and `__hash__`).
- Mutable defaults must use `field(default_factory=...)` - a bare `[]` is
  rejected, because one list would be shared by all instances.
- `frozen=True` -> instances are immutable and hashable.
- `__slots__` (or `slots=True`) fixes the allowed attribute names, removes the
  per-instance `__dict__` (less memory), and turns attribute typos into errors.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, replace


@dataclass
class Point:
    x: int
    y: int
    label: str = "origin"


@dataclass
class Bag:
    items: list[str] = field(default_factory=list)  # fresh list per instance


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float


@dataclass
class Temperature:
    celsius: float

    def __post_init__(self) -> None:
        if self.celsius < -273.15:
            raise ValueError("below absolute zero")
        self.fahrenheit = self.celsius * 9 / 5 + 32


@dataclass(slots=True)
class Vec3:
    x: float
    y: float
    z: float


def generated_methods() -> None:
    p = Point(1, 2)
    print("repr :", p)
    print("eq   :", Point(1, 2) == Point(1, 2), "| !=", Point(1, 2) == Point(9, 9))


def default_factory() -> None:
    a, b = Bag(), Bag()
    a.items.append("x")
    print("independent lists:", a.items, b.items)


def frozen_and_replace() -> None:
    c = Coordinate(51.5, -0.1)
    print("hashable frozen dataclass in a set:", {c, Coordinate(51.5, -0.1)})
    moved = replace(c, lon=0.0)         # produce a modified copy
    print("replace ->", moved)
    try:
        c.lat = 0.0
    except Exception as exc:
        print("mutating frozen ->", type(exc).__name__)


def post_init() -> None:
    t = Temperature(25)
    print("__post_init__ derived fahrenheit:", t.fahrenheit)


def slots_save_memory() -> None:
    v = Vec3(1.0, 2.0, 3.0)
    print("Vec3 has __dict__?", hasattr(v, "__dict__"))
    print("size Vec3 vs Point:", sys.getsizeof(v), "vs", sys.getsizeof(Point(1, 2)))
    try:
        v.w = 4.0
    except AttributeError as exc:
        print("typo caught by slots:", exc)


def main() -> None:
    generated_methods()
    print()
    default_factory()
    print()
    frozen_and_replace()
    print()
    post_init()
    print()
    slots_save_memory()


if __name__ == "__main__":
    main()

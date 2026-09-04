"""The data model & dunder methods — the practice snippet.

Run it:  python code/foundations/04_the_data_model_and_dunders/demo.py

Mental model: Python's operators and built-in functions are syntax over
"dunder" (double-underscore) methods. `len(x)` calls `x.__len__()`; `a + b`
calls `a.__add__(b)`; `x[k]` calls `x.__getitem__(k)`; `for` calls
`x.__iter__()`; `with` calls `__enter__` / `__exit__`. Implement the right
dunders and your object behaves like a built-in.
"""

from __future__ import annotations

from collections.abc import Iterator


class Vector:
    """A tiny 2D vector that plugs into Python's operator and builtin protocols."""

    def __init__(self, x: float, y: float) -> None:
        self._x = float(x)
        self._y = float(y)

    # --- how it prints -------------------------------------------------------
    def __repr__(self) -> str:                       # repr(), REPL, in containers
        return f"Vector({self._x!r}, {self._y!r})"

    # --- equality & hashing -----------------------------------------------
    def __eq__(self, other: object) -> bool:             # ==
        if not isinstance(other, Vector):
            return NotImplemented
        return (self._x, self._y) == (other._x, other._y)

    def __hash__(self) -> int:                           # hash(), set/dict keys
        return hash((self._x, self._y))

    # --- arithmetic ------------------------------------------------------
    def __add__(self, other: object) -> Vector:        # self + other
        if not isinstance(other, Vector):
            return NotImplemented                        # let Python try other.__radd__
        return Vector(self._x + other._x, self._y + other._y)

    def __radd__(self, other: object) -> Vector:       # other + self
        if other == 0:                                   # sum() starts from int 0
            return self
        return self.__add__(other)

    def __mul__(self, k: float) -> Vector:             # self * k
        return Vector(self._x * k, self._y * k)

    # --- container-ish behaviour ---------------------------------------
    def __len__(self) -> int:                            # len()
        return 2

    def __getitem__(self, i: int) -> float:              # v[0], v[1], unpacking
        return (self._x, self._y)[i]

    def __iter__(self) -> Iterator[float]:               # for c in v, tuple(v)
        yield self._x
        yield self._y

    # --- truthiness ----------------------------------------------------
    def __bool__(self) -> bool:                          # bool(v), if v:
        return (self._x, self._y) != (0.0, 0.0)


def main() -> None:
    a = Vector(1, 2)
    b = Vector(3, 4)

    print("repr(a)      ->", repr(a))
    print("a == Vector(1,2) ->", a == Vector(1, 2), "(via __eq__)")
    print("a + b        ->", a + b, "(via __add__)")
    print("sum([a, b])  ->", sum([a, b]), "(via __radd__, starts from 0)")
    print("a * 3        ->", a * 3, "(via __mul__)")
    print("len(a)       ->", len(a), "(via __len__)")
    print("a[1]         ->", a[1], "(via __getitem__)")
    print("list(a)      ->", list(a), "(via __iter__)")
    print("x, y = a     ->", (lambda x, y: (x, y))(*a), "(unpacking uses __iter__)")
    print("bool(Vector(0,0)) ->", bool(Vector(0, 0)), "(via __bool__)")
    print("{a, b, Vector(1,2)} ->", {a, b, Vector(1, 2)}, "(hashable -> set works)")


if __name__ == "__main__":
    main()

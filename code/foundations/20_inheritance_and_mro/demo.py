"""Inheritance, MRO & super() - the practice snippet.

Run it:  python code/foundations/20_inheritance_and_mro/demo.py

Mental model:
- A subclass inherits attributes it doesn't define, found by walking the METHOD
  RESOLUTION ORDER (`Cls.__mro__`) - a single linear list computed by the C3
  algorithm from all the bases.
- `super()` does NOT mean "my parent class". It means "the next class in the MRO
  of `type(self)`, after the current class" - so in multiple inheritance it can
  route to a sibling. This is what makes cooperative `__init__` work.
"""

from __future__ import annotations


class A:
    def __init__(self, **kw):
        self.trace = kw.get("trace", []) + ["A"]
        super().__init__()

    def who(self) -> str:
        return "A"


class B(A):
    def __init__(self, **kw):
        super().__init__(trace=kw.get("trace", []) + ["B"])

    def who(self) -> str:
        return "B -> " + super().who()


class C(A):
    def __init__(self, **kw):
        super().__init__(trace=kw.get("trace", []) + ["C"])

    def who(self) -> str:
        return "C -> " + super().who()


class D(B, C):
    def who(self) -> str:
        return "D -> " + super().who()


def show_mro() -> None:
    print("D.__mro__:", [cls.__name__ for cls in D.__mro__])


def super_follows_the_mro() -> None:
    d = D()
    # super() in B routes to C (the next class in D's MRO), not straight to A.
    print("D().who():", d.who())
    print("init trace:", d.trace)  # order the cooperative __init__ chain ran


def isinstance_and_issubclass() -> None:
    d = D()
    print("isinstance(d, (B, C)):", isinstance(d, (B, C)))
    print("issubclass(D, A):", issubclass(D, A))
    print("issubclass(B, C):", issubclass(B, C))


def main() -> None:
    show_mro()
    print()
    super_follows_the_mro()
    print()
    isinstance_and_issubclass()


if __name__ == "__main__":
    main()

"""Descriptors - the practice snippet.

Run it:  python code/foundations/24_descriptors/demo.py

Mental model: a descriptor is an object that defines `__get__` (and optionally
`__set__` / `__delete__`) and lives as a CLASS attribute. When you touch
`instance.attr` and `attr` is a descriptor on the class, Python calls the
descriptor's method instead of just reading the dict.

- DATA descriptor (`__set__` or `__delete__` present): wins over the instance
  `__dict__` on both read and write. `property` is one.
- NON-DATA descriptor (`__get__` only): the instance `__dict__` shadows it.
  Plain functions are non-data descriptors - that is how `obj.method` becomes a
  bound method.
`__set_name__(owner, name)` tells the descriptor which attribute name it is.
"""

from __future__ import annotations


class Positive:
    """A data descriptor: validates on set, stores in the instance dict."""

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__[self._name]

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self._name} must be positive, got {value}")
        instance.__dict__[self._name] = value


class Order:
    quantity = Positive()
    price = Positive()

    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price


def descriptor_in_action() -> None:
    o = Order(3, 10)
    print("o.quantity =", o.quantity, "| o.price =", o.price)
    try:
        o.quantity = -1
    except ValueError as exc:
        print("o.quantity = -1 ->", exc)


def functions_are_descriptors() -> None:
    class C:
        def greet(self):
            return "hi"

    c = C()
    # `c.greet` is C.greet.__get__(c, C) -> a bound method
    print("C.greet is a function:", type(C.__dict__["greet"]).__name__)
    print("c.greet is bound:", c.greet.__self__ is c)
    bound = C.greet.__get__(c, C)
    print("manual __get__ bind:", bound())


def data_vs_non_data() -> None:
    class NonData:                       # only __get__
        def __get__(self, inst, owner=None):
            return "from descriptor"

    class Holder:
        x = NonData()

    h = Holder()
    print("before instance set: h.x =", h.x)
    h.__dict__["x"] = "from instance dict"
    print("after instance set:  h.x =", h.x, "(instance dict shadows non-data)")


def main() -> None:
    descriptor_in_action()
    print()
    functions_are_descriptors()
    print()
    data_vs_non_data()


if __name__ == "__main__":
    main()

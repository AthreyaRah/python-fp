"""Metaclasses - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/25_metaclasses/scenarios.py
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Metaclass conflict when combining with ABC.
# ======================================================================================

def s1_build() -> list[str]:
    registry: list[str] = []

    class Base(ABC):
        def __init_subclass__(cls, **kw):        # lightweight hook, no metaclass
            super().__init_subclass__(**kw)
            registry.append(cls.__name__)

        @abstractmethod
        def run(self): ...

    class Job(Base):
        def run(self):
            return "done"

    return registry  # ['Job']


def s1_break() -> str:
    class Registry(type):
        def __new__(mcs, name, bases, ns):
            return super().__new__(mcs, name, bases, ns)

    try:
        # ABC already uses ABCMeta; a second, unrelated metaclass conflicts.
        class Base(ABC, metaclass=Registry):
            pass
        return "no error (unexpected)"
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> list[str]:
    registry: list[str] = []

    class Base(ABC):
        def __init_subclass__(cls, **kw):
            super().__init_subclass__(**kw)
            registry.append(cls.__name__)

        @abstractmethod
        def run(self): ...

    class Job(Base):
        def run(self):
            return "done"

    return registry


S1_WHY = """
A class has exactly ONE metaclass, and Python derives it from the bases: every
base's metaclass must be the same as, or a subclass of, the chosen one. `ABC`'s
metaclass is `ABCMeta`; adding an unrelated `metaclass=Registry` gives
`TypeError: metaclass conflict`. `__init_subclass__` needs no metaclass at all,
so it composes cleanly with ABCs, enums, and anything else.
"""


# ======================================================================================
# Scenario 2 - __init_subclass__ not forwarding keyword arguments.
# ======================================================================================

def s2_build() -> dict:
    table: dict[str, type] = {}

    class Handler:
        def __init_subclass__(cls, /, *, route: str, **kwargs):
            super().__init_subclass__(**kwargs)     # forward the rest
            table[route] = cls

    class Home(Handler, route="/"):
        pass

    class About(Handler, route="/about"):
        pass

    return {k: v.__name__ for k, v in table.items()}


def s2_break() -> str:
    class Handler:
        def __init_subclass__(cls):                 # accepts NO keyword args
            super().__init_subclass__()

    try:
        class Home(Handler, route="/"):            # passes an unexpected kwarg
            pass
        return "no error (unexpected)"
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> dict:
    table: dict[str, type] = {}

    class Handler:
        def __init_subclass__(cls, /, *, route: str = "", **kwargs):
            super().__init_subclass__(**kwargs)
            if route:
                table[route] = cls

    class Home(Handler, route="/"):
        pass

    return {k: v.__name__ for k, v in table.items()}


S2_WHY = """
Keyword arguments in a class header (`class Home(Handler, route="/")`) are passed
straight to `__init_subclass__` and to `type.__new__`. If your
`__init_subclass__` doesn't declare `route` (or `**kwargs`), you get
`TypeError: __init_subclass__() got an unexpected keyword argument 'route'`.
Accept the ones you use and forward the rest with
`super().__init_subclass__(**kwargs)`.
"""


# ======================================================================================
# Scenario 3 - __init_subclass__ registers abstract intermediate classes.
# ======================================================================================

def s3_build() -> list[str]:
    registry: list[str] = []

    class Shape(ABC):
        def __init_subclass__(cls, /, *, register: bool = False, **kw):
            super().__init_subclass__(**kw)
            if register:                        # opt in explicitly
                registry.append(cls.__name__)

        @abstractmethod
        def area(self): ...

    class Polygon(Shape, ABC):                   # intermediate - does NOT opt in
        pass

    class Square(Polygon, register=True):
        def area(self):
            return 1

    return registry  # ['Square'] only


def s3_break() -> list[str]:
    registry: list[str] = []

    class Shape(ABC):
        def __init_subclass__(cls, **kw):
            super().__init_subclass__(**kw)
            registry.append(cls.__name__)       # no guard - every subclass

        @abstractmethod
        def area(self): ...

    class Polygon(Shape, ABC):                   # abstract layer...
        pass

    class Square(Polygon):
        def area(self):
            return 1

    # 'Polygon' - which cannot be instantiated - is now in the registry too.
    assert registry == ["Polygon", "Square"]
    return registry


def s3_fix() -> list[str]:
    registry: list[str] = []

    class Shape(ABC):
        def __init_subclass__(cls, /, *, register: bool = False, **kw):
            super().__init_subclass__(**kw)
            if register:
                registry.append(cls.__name__)

        @abstractmethod
        def area(self): ...

    class Polygon(Shape, ABC):
        pass

    class Square(Polygon, register=True):
        def area(self):
            return 1

    return registry


S3_WHY = """
`__init_subclass__` fires for EVERY subclass at every level - including abstract
intermediate classes you never intend to instantiate. Checking
`cls.__abstractmethods__` is unreliable here because `ABCMeta` fills it in AFTER
`__init_subclass__` has run. Use an explicit opt-in: a `register=True` class
keyword argument (or a decorator) so only the classes you mean get added.
"""


# ======================================================================================
# Scenario 4 - Metaclass passed as a base instead of `metaclass=`.
# ======================================================================================

class Meta(type):
    def __new__(mcs, name, bases, ns):
        ns.setdefault("tag", "made-by-Meta")
        return super().__new__(mcs, name, bases, ns)


def s4_build() -> str:
    class Service(metaclass=Meta):
        pass

    return Service().tag  # "made-by-Meta"


def s4_break() -> str:
    class Service(Meta):        # Meta as a BASE -> Service is a subclass of `type`
        pass

    try:
        Service()              # calling it needs type()'s args: (name, bases, ns)
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> str:
    class Service(metaclass=Meta):
        pass

    return Service().tag


S4_WHY = """
`class C(Meta)` makes `Meta` a BASE class of `C`. Since `Meta` subclasses `type`,
`C` is now itself a kind of class-factory, and `C()` expects the arguments `type`
takes - `C() -> TypeError: type.__new__() takes exactly 3 arguments`. To apply a
metaclass you pass it as the `metaclass=` keyword: `class C(metaclass=Meta)`.
"""


SCENARIOS = [
    Scenario("Metaclass conflict with ABC", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("__init_subclass__ kwargs not forwarded", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Registering abstract intermediates", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Metaclass as a base class", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

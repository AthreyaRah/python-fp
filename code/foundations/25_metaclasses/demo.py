"""Metaclasses & __init_subclass__ - the practice snippet.

Run it:  python code/foundations/25_metaclasses/demo.py

Mental model:
- A class is an object, and its type is its METACLASS (default: `type`).
  `type(name, bases, namespace)` builds a class the same way `type` does when it
  runs a `class` statement.
- A metaclass customises class CREATION (its `__new__`/`__init__` run once, when
  the class is defined).
- `__init_subclass__` is the lightweight hook: a classmethod on a base class,
  called automatically whenever a subclass is created. It covers most real needs
  (registering plugins, validating subclasses) without a metaclass.
- Prefer, in order: a class decorator, then `__init_subclass__`, then a metaclass.
"""

from __future__ import annotations


def classes_are_made_by_type() -> None:
    # These two are equivalent:
    class A:
        greeting = "hi"

        def hello(self):
            return self.greeting

    B = type("B", (), {"greeting": "hi", "hello": lambda self: self.greeting})

    print("type(A) is type:", type(A) is type)
    print("A().hello() =", A().hello(), "| B().hello() =", B().hello())


class Plugin:
    registry: dict[str, type] = {}

    def __init_subclass__(cls, /, *, key: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = key or cls.__name__.lower()
        Plugin.registry[name] = cls


class JsonPlugin(Plugin, key="json"):
    pass


class CsvPlugin(Plugin):  # no key -> uses "csvplugin"
    pass


def init_subclass_registry() -> None:
    print("Plugin.registry:", {k: v.__name__ for k, v in Plugin.registry.items()})


class Sealed(type):
    """A metaclass that forbids subclassing classes it made."""

    def __new__(mcs, name, bases, ns):
        for base in bases:
            if isinstance(base, Sealed):
                raise TypeError(f"{base.__name__} is sealed; cannot subclass it")
        return super().__new__(mcs, name, bases, ns)


class Config(metaclass=Sealed):
    pass


def metaclass_enforcement() -> None:
    print("Config created via metaclass Sealed:", type(Config).__name__)
    try:
        class SubConfig(Config):
            pass
    except TypeError as exc:
        print("subclassing Config ->", exc)


def main() -> None:
    classes_are_made_by_type()
    print()
    init_subclass_registry()
    print()
    metaclass_enforcement()


if __name__ == "__main__":
    main()

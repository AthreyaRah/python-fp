"""Descriptors - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/24_descriptors/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Descriptor stores state on itself -> shared by all instances.
# ======================================================================================

def s1_build() -> tuple[int, int]:
    class Field:
        def __set_name__(self, owner, name):
            self.name = name

        def __get__(self, inst, owner=None):
            return inst.__dict__.get(self.name) if inst else self

        def __set__(self, inst, value):
            inst.__dict__[self.name] = value      # per-instance storage

    class Box:
        v = Field()

        def __init__(self, v):
            self.v = v

    a, b = Box(1), Box(2)
    return a.v, b.v  # (1, 2)


def s1_break() -> tuple[int, int]:
    class Field:
        def __get__(self, inst, owner=None):
            return getattr(self, "_value", None) if inst else self

        def __set__(self, inst, value):
            self._value = value                   # stored on the DESCRIPTOR object

    class Box:
        v = Field()

        def __init__(self, v):
            self.v = v

    a, b = Box(1), Box(2)
    # There is one Field() shared by the class, so setting b.v overwrote a.v.
    assert (a.v, b.v) == (2, 2)
    return a.v, b.v


def s1_fix() -> tuple[int, int]:
    class Field:
        def __set_name__(self, owner, name):
            self.name = name

        def __get__(self, inst, owner=None):
            return inst.__dict__.get(self.name) if inst else self

        def __set__(self, inst, value):
            inst.__dict__[self.name] = value

    class Box:
        v = Field()

        def __init__(self, v):
            self.v = v

    a, b = Box(1), Box(2)
    return a.v, b.v


S1_WHY = """
`v = Field()` creates ONE descriptor object, held by the class and shared by every
instance. Storing `self._value` in `__set__` writes to that single object, so the
last instance to set the attribute wins for all of them. Store per-instance state
in `instance.__dict__` (keyed by the name from `__set_name__`) or a
`weakref.WeakKeyDictionary` keyed by the instance.
"""


# ======================================================================================
# Scenario 2 - A non-data descriptor gets shadowed by an instance attribute.
# ======================================================================================

def s2_build() -> str:
    class Computed:                     # data descriptor: has __set__
        def __get__(self, inst, owner=None):
            return "computed" if inst else self

        def __set__(self, inst, value):
            raise AttributeError("read-only")

    class Model:
        kind = Computed()

    m = Model()
    try:
        m.kind = "manual"               # blocked - data descriptor wins
    except AttributeError:
        pass
    return m.kind  # "computed"


def s2_break() -> str:
    class Computed:                     # NON-data descriptor: only __get__
        def __get__(self, inst, owner=None):
            return "computed" if inst else self

    class Model:
        kind = Computed()

    m = Model()
    m.kind = "manual"                   # allowed - lands in m.__dict__
    return m.kind  # "manual" - the descriptor is now shadowed


def s2_fix() -> str:
    class Computed:
        def __get__(self, inst, owner=None):
            return "computed" if inst else self

        def __set__(self, inst, value):
            raise AttributeError("read-only")

    class Model:
        kind = Computed()

    m = Model()
    try:
        m.kind = "manual"
    except AttributeError:
        pass
    return m.kind


S2_WHY = """
Attribute lookup priority: data descriptor (defines `__set__`/`__delete__`) >
instance `__dict__` > non-data descriptor (`__get__` only) > class attributes.
A `__get__`-only descriptor is therefore overridden the moment an instance
attribute of the same name exists. Add `__set__` (even one that raises) to make it
a data descriptor that always takes precedence.
"""


# ======================================================================================
# Scenario 3 - Two descriptors sharing a hardcoded storage key.
# ======================================================================================

def s3_build() -> tuple[int, int]:
    class Attr:
        def __set_name__(self, owner, name):
            self.key = "_" + name          # unique per attribute

        def __get__(self, inst, owner=None):
            return getattr(inst, self.key) if inst else self

        def __set__(self, inst, value):
            setattr(inst, self.key, value)

    class Rect:
        width = Attr()
        height = Attr()

        def __init__(self, w, h):
            self.width, self.height = w, h

    r = Rect(4, 9)
    return r.width, r.height  # (4, 9)


def s3_break() -> tuple[int, int]:
    class Attr:
        def __get__(self, inst, owner=None):
            return getattr(inst, "_value", None) if inst else self

        def __set__(self, inst, value):
            inst._value = value               # both descriptors use "_value"

    class Rect:
        width = Attr()
        height = Attr()

        def __init__(self, w, h):
            self.width, self.height = w, h     # height overwrites width's storage

    r = Rect(4, 9)
    assert (r.width, r.height) == (9, 9)
    return r.width, r.height


def s3_fix() -> tuple[int, int]:
    class Attr:
        def __set_name__(self, owner, name):
            self.key = "_" + name

        def __get__(self, inst, owner=None):
            return getattr(inst, self.key) if inst else self

        def __set__(self, inst, value):
            setattr(inst, self.key, value)

    class Rect:
        width = Attr()
        height = Attr()

        def __init__(self, w, h):
            self.width, self.height = w, h

    r = Rect(4, 9)
    return r.width, r.height


S3_WHY = """
A descriptor instance does not inherently know which attribute name it was
assigned to. Hardcoding a storage key means every descriptor of that class on the
same object writes to the same slot and clobbers the others. `__set_name__(self,
owner, name)` is called once at class creation with the attribute name - use it to
derive a unique per-attribute storage key.
"""


# ======================================================================================
# Scenario 4 - Putting a descriptor on an instance instead of the class.
# ======================================================================================

class Loud:
    def __get__(self, inst, owner=None):
        return "GET via descriptor"

    def __set__(self, inst, value):
        inst.__dict__["_x"] = value


def s4_build() -> str:
    class Thing:
        x = Loud()          # descriptor lives on the CLASS

    return Thing().x  # "GET via descriptor"


def s4_break() -> str:
    class Thing:
        pass

    t = Thing()
    t.x = Loud()            # assigned to the INSTANCE - just a normal attribute
    result = t.x            # returns the Loud object itself; __get__ never fires
    return type(result).__name__  # "Loud", not the string


def s4_fix() -> str:
    class Thing:
        x = Loud()

    return Thing().x


S4_WHY = """
The descriptor protocol is only triggered for attributes found on the TYPE during
`instance.attr` lookup. An object stored in `instance.__dict__` is returned
as-is - `__get__`/`__set__` are never consulted. Descriptors must be class
attributes.
"""


SCENARIOS = [
    Scenario("Descriptor stores state on itself", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Non-data descriptor shadowed", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Shared hardcoded storage key", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Descriptor on the instance", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

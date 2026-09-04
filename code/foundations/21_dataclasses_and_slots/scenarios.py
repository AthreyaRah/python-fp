"""dataclasses & __slots__ - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/21_dataclasses_and_slots/scenarios.py
"""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError, dataclass, field, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Mutable default without default_factory.
# ======================================================================================

def s1_build() -> tuple[list, list]:
    @dataclass
    class Cart:
        items: list[str] = field(default_factory=list)

    a, b = Cart(), Cart()
    a.items.append("apple")
    return a.items, b.items  # (['apple'], [])


def s1_break() -> str:
    try:
        @dataclass
        class Cart:
            items: list = []           # rejected at class-definition time
        return "no error (unexpected)"
    except ValueError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> tuple[list, list]:
    @dataclass
    class Cart:
        items: list[str] = field(default_factory=list)

    a, b = Cart(), Cart()
    a.items.append("apple")
    return a.items, b.items


S1_WHY = """
`@dataclass` builds one `__init__` shared by all instances. A bare `items: list =
[]` would put that single list into every instance's `items` - the class-attribute
trap. Rather than let that happen silently, dataclass raises `ValueError: mutable
default ... is not allowed`. Use `field(default_factory=list)` to build a new
container per instance.
"""


# ======================================================================================
# Scenario 2 - Mutating a frozen dataclass.
# ======================================================================================

@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "USD"


def s2_build() -> "Money":
    m = Money(500)
    return replace(m, cents=750)   # a new Money; the original is untouched


def s2_break() -> str:
    m = Money(500)
    try:
        m.cents = 750
    except FrozenInstanceError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s2_fix() -> "Money":
    m = Money(500)
    return replace(m, cents=750)


S2_WHY = """
`frozen=True` generates a `__setattr__` (and `__delattr__`) that always raises
`FrozenInstanceError`. That is the point - frozen instances are safe to share, use
as dict keys, and cache. To "change" one, build a new instance:
`dataclasses.replace(obj, field=new_value)`.
"""


# ======================================================================================
# Scenario 3 - A non-frozen dataclass is unhashable.
# ======================================================================================

def s3_build() -> int:
    @dataclass(frozen=True)
    class Tag:
        name: str

    return len({Tag("a"), Tag("a"), Tag("b")})  # 2


def s3_break() -> str:
    @dataclass
    class Tag:               # default: eq=True, frozen=False -> __hash__ = None
        name: str

    try:
        {Tag("a")}
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> int:
    @dataclass(frozen=True)
    class Tag:
        name: str

    return len({Tag("a"), Tag("a"), Tag("b")})


S3_WHY = """
A dataclass with `eq=True` (the default) but not `frozen` gets `__hash__` set to
`None` - the same rule as any class that defines `__eq__` without `__hash__`
(topic 04): equal-but-mutable objects must not be dict keys. `frozen=True` makes
it immutable and restores a consistent `__hash__`. (Or `@dataclass(eq=False)` to
keep identity hashing, or `unsafe_hash=True` if you know what you're doing.)
"""


# ======================================================================================
# Scenario 4 - __slots__ catches attribute typos; no slots hides them.
# ======================================================================================

def s4_build() -> str:
    @dataclass(slots=True)
    class Config:
        retries: int
        timeout: float

    c = Config(3, 1.5)
    try:
        c.retires = 5            # typo: 'retires' not 'retries'
    except AttributeError as exc:
        return f"caught: {type(exc).__name__}"
    return "typo slipped through (unexpected)"


def s4_break() -> tuple[int, bool]:
    @dataclass
    class Config:                # no slots -> instances have __dict__
        retries: int
        timeout: float

    c = Config(3, 1.5)
    c.retires = 5                 # typo silently creates a dead attribute
    # `retries` is still 3; a `retires` attribute now exists and does nothing.
    return c.retries, hasattr(c, "retires")  # (3, True)


def s4_fix() -> str:
    @dataclass(slots=True)
    class Config:
        retries: int
        timeout: float

    c = Config(3, 1.5)
    try:
        c.retires = 5
    except AttributeError:
        c.retries = 5            # fixed after the error pointed at the typo
    return f"retries={c.retries}"


S4_WHY = """
Without `__slots__`, every instance has a `__dict__` and any `obj.anything = ...`
just adds a key - so a misspelled attribute name is silently a new, useless
attribute while the real one keeps its old value. `slots=True` declares the exact
allowed names; assigning anything else raises `AttributeError`, turning the typo
into an immediate, located error (and saving the per-instance dict's memory).
"""


SCENARIOS = [
    Scenario("Mutable default without default_factory", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Mutating a frozen dataclass", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Non-frozen dataclass is unhashable", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("__slots__ catches attribute typos", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

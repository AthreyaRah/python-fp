"""Type hints & typing - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/23_type_hints_and_typing/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, get_type_hints

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Trusting an annotation to validate at runtime.
# ======================================================================================

def s1_build() -> list[int]:
    def take(n: int) -> list[int]:
        n = int(n)                 # validate/coerce at the boundary - annotations don't
        return list(range(n))

    return take("3")  # [0, 1, 2]


def s1_break() -> str:
    def take(n: int) -> list[int]:
        return list(range(n))      # trusts the annotation; gets a str

    try:
        return str(take("3"))
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> list[int]:
    def take(n: int) -> list[int]:
        n = int(n)                 # coerce at the boundary
        return list(range(n))

    return take("3")  # [0, 1, 2]


S1_WHY = """
`def take(n: int)` records `{"n": int}` in `__annotations__` and that is all -
the interpreter never compares the argument to it. Passing `"3"` sails past the
signature and fails deep inside at `range("3")`. If a value crosses a trust
boundary (user input, a file, an API), validate/coerce it explicitly (or use a
library like pydantic that reads the annotations and enforces them).
"""


# ======================================================================================
# Scenario 2 - Annotation says list, default says None.
# ======================================================================================

def s2_build() -> list[int]:
    def add_id(new_id: int, into: list[int] | None = None) -> list[int]:
        into = [] if into is None else into
        into.append(new_id)
        return into

    return add_id(1)  # [1]  (fresh list, correct type)


def s2_break() -> str:
    def add_id(new_id: int, into: list[int] = None) -> list[int]:  # type: ignore[assignment]
        into.append(new_id)      # `into` is None at runtime
        return into

    try:
        return str(add_id(1))
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> list[int]:
    def add_id(new_id: int, into: Optional[list[int]] = None) -> list[int]:
        into = [] if into is None else into
        into.append(new_id)
        return into

    return add_id(1)


S2_WHY = """
`into: list[int] = None` is a contradiction: the annotation promises a list, the
default is `None`. A type checker flags it; at runtime the default really is
`None`, so `into.append(...)` raises `AttributeError`. When a parameter can be
absent, its type is `X | None` (a.k.a. `Optional[X]`) and its default is `None`,
with the real value built inside the body.
"""


# ======================================================================================
# Scenario 3 - Reading raw __annotations__ under `from __future__ import annotations`.
# ======================================================================================

def _annotated(a: int, b: str) -> bool:  # noqa: ARG001
    return True


def s3_build() -> dict:
    hints = get_type_hints(_annotated)   # resolves the string annotations
    return {k: v.__name__ for k, v in hints.items()}  # {'a': 'int', 'b': 'str', 'return': 'bool'}


def s3_break() -> dict:
    raw = _annotated.__annotations__     # PEP 563: these are STRINGS, not types
    # e.g. {'a': 'int', 'b': 'str', 'return': 'bool'} - looks similar but they are str
    return {k: type(v).__name__ for k, v in raw.items()}  # every value is 'str'


def s3_fix() -> dict:
    hints = get_type_hints(_annotated)
    return {k: type(v).__name__ for k, v in hints.items()}  # 'type' for each real class


S3_WHY = """
With `from __future__ import annotations` (PEP 563), every annotation is stored as
a string and never evaluated - great for forward references and import cost, but
`func.__annotations__["a"]` is the string `"int"`, not the class `int`.
`typing.get_type_hints(obj)` evaluates them in the right namespace and returns the
actual objects. Libraries that introspect annotations (dataclasses, pydantic)
call it for you.
"""


# ======================================================================================
# Scenario 4 - "Optional" does not mean "has a default".
# ======================================================================================

def s4_build() -> str:
    def greet(name: str | None = None) -> str:   # optional TYPE *and* a default
        return f"hello {name or 'stranger'}"

    return greet()  # "hello stranger"


def s4_break() -> str:
    def greet(name: Optional[str]) -> str:       # Optional type, but NO default
        return f"hello {name or 'stranger'}"

    try:
        return greet()                           # TypeError: missing argument
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s4_fix() -> str:
    def greet(name: Optional[str] = None) -> str:
        return f"hello {name or 'stranger'}"

    return greet()


S4_WHY = """
`Optional[str]` / `str | None` describes the VALUE's type ("a str or None"). It
says nothing about whether the caller may omit the argument - that is decided
solely by whether the parameter has a default. `def greet(name: Optional[str])`
still requires an argument; add `= None` to make it truly optional.
"""


SCENARIOS = [
    Scenario("Trusting an annotation at runtime", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Annotation vs None default", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Raw __annotations__ are strings", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Optional != optional parameter", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""ABCs, Protocols & duck typing - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/22_abcs_protocols_duck_typing/scenarios.py
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections import UserDict
from pathlib import Path
from typing import Protocol, runtime_checkable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Instantiating an incomplete ABC subclass.
# ======================================================================================

class Repository(ABC):
    @abstractmethod
    def get(self, key: str): ...

    @abstractmethod
    def put(self, key: str, value): ...


def s1_build() -> str:
    class MemRepo(Repository):
        def __init__(self):
            self._d = {}

        def get(self, key):
            return self._d.get(key)

        def put(self, key, value):
            self._d[key] = value

    r = MemRepo()
    r.put("a", 1)
    return f"get('a') -> {r.get('a')}"


def s1_break() -> str:
    class HalfRepo(Repository):
        def get(self, key):        # implements get, forgets put
            return None

    try:
        HalfRepo()
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s1_fix() -> str:
    class MemRepo(Repository):
        def __init__(self):
            self._d = {}

        def get(self, key):
            return self._d.get(key)

        def put(self, key, value):
            self._d[key] = value

    return f"instantiated: {type(MemRepo()).__name__}"


S1_WHY = """
`abc.ABCMeta` collects every name still marked `@abstractmethod` into
`__abstractmethods__`. If that set is non-empty when you call the class,
construction raises `TypeError: Can't instantiate abstract class HalfRepo with
abstract method put`. The check happens at instantiation, so an incomplete
implementation fails fast rather than at first use of the missing method.
"""


# ======================================================================================
# Scenario 2 - isinstance against a Protocol that isn't runtime_checkable.
# ======================================================================================

class Closable(Protocol):
    def close(self) -> None: ...


@runtime_checkable
class ClosableRT(Protocol):
    def close(self) -> None: ...


class Handle:
    def close(self) -> None:
        pass


def s2_build() -> bool:
    return isinstance(Handle(), ClosableRT)  # True


def s2_break() -> str:
    try:
        return str(isinstance(Handle(), Closable))
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> bool:
    return isinstance(Handle(), ClosableRT)


S2_WHY = """
A `Protocol` is primarily for STATIC type checkers - `isinstance` against one is
disabled by default and raises `TypeError: Instance and class checks can only be
used with @runtime_checkable protocols`. Add `@runtime_checkable` to opt in; note
it only checks that the named attributes EXIST, not their signatures or types.
"""


# ======================================================================================
# Scenario 3 - runtime_checkable is a shallow (name-only) check.
# ======================================================================================

@runtime_checkable
class Sender(Protocol):
    def send(self, message: str) -> bool: ...


class RealSender:
    def send(self, message: str) -> bool:
        return True


class WrongSender:
    def send(self):          # no `message` parameter - different contract
        return "sent!"


def s3_build() -> bool:
    s = RealSender()
    return isinstance(s, Sender) and s.send("hello") is True


def s3_break() -> str:
    s = WrongSender()
    passes_isinstance = isinstance(s, Sender)   # True! only checks name 'send'
    try:
        s.send("hello")                          # ...but the call is wrong
    except TypeError as exc:
        return f"isinstance says {passes_isinstance}, call fails: {type(exc).__name__}"
    return "call unexpectedly worked"


def s3_fix() -> bool:
    # Don't lean on runtime_checkable for correctness. Let the static checker
    # verify signatures, or duck-test the actual behaviour you need.
    s = RealSender()
    try:
        ok = s.send("probe")
        return ok is True
    except TypeError:
        return False


S3_WHY = """
`@runtime_checkable` makes `isinstance(x, P)` check only that each protocol member
NAME is present on `x`. It does not verify parameter names, counts, or types. So
an object with a `send` method of the wrong shape passes the check and then blows
up when called. Use protocols for static checking (mypy/pyright); at runtime,
test the behaviour you actually rely on.
"""


# ======================================================================================
# Scenario 4 - Subclassing dict vs subclassing UserDict / MutableMapping.
# ======================================================================================

def s4_build() -> dict:
    class LowerDict(UserDict):
        def __setitem__(self, key, value):
            super().__setitem__(key.lower(), value)

    d = LowerDict()
    d["Name"] = "Ada"
    d.update({"CITY": "London"})           # goes through __setitem__
    return dict(d)  # {'name': 'Ada', 'city': 'London'}


def s4_break() -> dict:
    class LowerDict(dict):
        def __setitem__(self, key, value):
            super().__setitem__(key.lower(), value)

    d = LowerDict()
    d["Name"] = "Ada"                       # via __setitem__ -> 'name'
    d.update({"CITY": "London"})            # dict.update bypasses your __setitem__
    d2 = LowerDict(TITLE="Dr")              # so does __init__
    return {**d, **d2}  # {'name': 'Ada', 'CITY': 'London', 'TITLE': 'Dr'}


def s4_fix() -> dict:
    from collections.abc import MutableMapping

    class LowerDict(MutableMapping):
        def __init__(self, **kw):
            self._d = {}
            self.update(kw)

        def __setitem__(self, key, value):
            self._d[key.lower()] = value

        def __getitem__(self, key):
            return self._d[key.lower()]

        def __delitem__(self, key):
            del self._d[key.lower()]

        def __iter__(self):
            return iter(self._d)

        def __len__(self):
            return len(self._d)

    d = LowerDict(TITLE="Dr")
    d.update({"CITY": "London"})
    return dict(d)  # {'title': 'Dr', 'city': 'London'}


S4_WHY = """
`dict`, `list`, `str` are implemented in C. Their methods (`update`, `__init__`,
`setdefault`, ...) call the C-level storage directly, NOT your Python
`__setitem__` override - so only literal `d[k] = v` goes through your code and the
class becomes inconsistent. Subclass `collections.abc.MutableMapping` (or
`collections.UserDict`), which routes every mutating operation through the handful
of methods you implement.
"""


SCENARIOS = [
    Scenario("Incomplete ABC subclass", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("isinstance vs non-runtime Protocol", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("runtime_checkable is name-only", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Subclassing dict vs UserDict", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""Scope & namespaces - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/16_scope_legb/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Shadowing a built-in.
# ======================================================================================

def s1_build() -> int:
    totals = [10, 20, 30]        # not named `sum`
    return sum(totals)  # 60


def s1_break() -> str:
    sum = 0                       # local name `sum` shadows the builtin
    for v in [10, 20, 30]:
        sum += v
    try:
        return str(sum([1, 2]))   # `sum` is now the int 60
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> int:
    total = 0                     # pick a name that isn't a builtin
    for v in [10, 20, 30]:
        total += v
    return total + sum([1, 2])    # builtin `sum` still works


S1_WHY = """
Assigning `sum = 0` creates a LOCAL name `sum` for the whole function. Every later
`sum(...)` in that scope resolves to the local (the int) before ever reaching the
built-in, so calling it raises `TypeError: 'int' object is not callable`. Don't
name variables after built-ins: `list`, `dict`, `id`, `type`, `sum`, `min`,
`max`, `input`, `str`, `bytes`, ...
"""


# ======================================================================================
# Scenario 2 - Referencing a class-body name from a method.
# ======================================================================================

def s2_build() -> int:
    class Settings:
        RETRIES = 3

        def budget(self) -> int:
            return self.RETRIES * 10   # reach it through the instance

    return Settings().budget()  # 30


def s2_break() -> str:
    class Settings:
        RETRIES = 3

        def budget(self) -> int:
            return RETRIES * 10        # bare name -> NameError

    try:
        return str(Settings().budget())
    except NameError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> int:
    class Settings:
        RETRIES = 3

        def budget(self) -> int:
            return self.RETRIES * 10

    return Settings().budget()


S2_WHY = """
A class body runs in its own temporary namespace to build the class object. That
namespace is NOT an enclosing scope for the methods defined in it - method code
follows L-E-G-B and never sees `RETRIES` directly. Access class-level names via
`self.RETRIES` or `Settings.RETRIES`.
"""


# ======================================================================================
# Scenario 3 - Reassigning a global inside a function.
# ======================================================================================

_STATE = {"loaded": False}
_COUNT = 0


def s3_build() -> bool:
    def load():
        _STATE["loaded"] = True   # MUTATES the global object - no `global` needed

    load()
    return _STATE["loaded"]  # True


def s3_break() -> int:
    def bump():
        _COUNT = _COUNT + 1       # assignment -> local `_COUNT`; also reads it -> error
        return _COUNT

    try:
        bump()
    except UnboundLocalError:
        pass
    return _COUNT  # reads the module global - still 0, the bump never took effect


def s3_fix() -> int:
    global _COUNT
    _COUNT = 0            # rebinding a global also needs the declaration

    def bump():
        global _COUNT
        _COUNT += 1
        return _COUNT

    bump()
    bump()
    return _COUNT  # 2


S3_WHY = """
Mutating a global object (`_STATE["loaded"] = True`, `_LIST.append(...)`) just
looks the name up and calls a method - fine without `global`. REBINDING the name
(`_COUNT = ...`) is an assignment, which makes `_COUNT` local for the whole
function; the `+ 1` then reads that unassigned local -> `UnboundLocalError`, and
even if it didn't, the module global would be unchanged. Declare `global _COUNT`
to rebind it.
"""


# ======================================================================================
# Scenario 4 - Expecting a comprehension variable to leak.
# ======================================================================================

def s4_build() -> int:
    items = [5, 8, 2]
    _ = [x * x for x in items]
    last = items[-1]              # get the last item explicitly
    return last  # 2


def s4_break() -> str:
    items = [5, 8, 2]
    _ = [x * x for x in items]
    try:
        return str(x)             # NameError - `x` never existed out here (Py3)
    except NameError as exc:
        return f"{type(exc).__name__}: {exc}"


def s4_fix() -> int:
    items = [5, 8, 2]
    _ = [x * x for x in items]
    return items[-1]


S4_WHY = """
In Python 3 a list/set/dict comprehension (and a generator expression) runs in its
OWN scope, so its loop variable does not exist afterwards - unlike a plain `for`
loop, which does not create a scope and leaves its variable bound to the last
value. Coming from Python 2 (where comprehensions leaked) this surprises people.
Capture what you need explicitly.
"""


SCENARIOS = [
    Scenario("Shadowing a built-in", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Class-body name in a method", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Reassigning a global", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Comprehension variable doesn't leak", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

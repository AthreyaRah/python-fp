"""The match statement - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/42_match_statement/scenarios.py
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - A bare name is a capture pattern, not a comparison.
# ======================================================================================

class Status(Enum):
    OK = 200
    NOT_FOUND = 404


OK = 200  # a module constant


def s1_build() -> list[str]:
    def classify(code):
        match code:
            case Status.OK.value:          # dotted -> value pattern (compares)
                return "ok"
            case 404:                      # literal
                return "missing"
            case _:
                return "other"
    return [classify(c) for c in (200, 404, 500)]  # ['ok', 'missing', 'other']


def s1_break() -> list[str]:
    def classify(code):
        match code:
            case OK:                       # BARE NAME -> capture: matches ANYTHING,
                return f"captured OK={OK}"  # and rebinds a local `OK` to the subject
    # Intent was "match code == OK (200)". Instead every code matches and `OK`
    # is bound to it. (A `case 404:` after this would be a SyntaxError - see s2.)
    return [classify(c) for c in (200, 404, 500)]


def s1_fix() -> list[str]:
    def classify(code):
        match code:
            case 200:                      # a literal
                return "ok"
            case 404:
                return "missing"
            case _:
                return "other"
    return [classify(c) for c in (200, 404, 500)]


S1_WHY = """
In a `case`, a bare identifier is a CAPTURE pattern: it always matches and binds
the name to the subject. `case OK:` does NOT mean "if code == OK" - it means
"match anything, call it OK". To compare against a value you need a literal
(`case 200:`), a dotted name (`case Status.OK.value:` / `case Color.RED:`), or a
guard (`case c if c == OK:`).
"""


# ======================================================================================
# Scenario 2 - An irrefutable pattern before the last case.
# ======================================================================================

_BAD = """
match value:
    case other:        # irrefutable - always matches
        handle(other)
    case 0:            # can never be reached
        handle_zero()
"""

_GOOD = """
match value:
    case 0:
        handle_zero()
    case other:        # irrefutable, and it IS last - fine
        handle(other)
"""


def s2_build() -> str:
    compile(_GOOD, "<good>", "exec")   # compiles cleanly
    return "compiles"


def s2_break() -> str:
    try:
        compile(_BAD, "<bad>", "exec")
    except SyntaxError as exc:
        return f"{type(exc).__name__}: {exc.msg}"
    return "no error (unexpected)"


def s2_fix() -> str:
    compile(_GOOD, "<fixed>", "exec")
    return "compiles"


S2_WHY = """
A capture pattern (`case other:`) or wildcard (`case _:`) is "irrefutable" - it
always matches - so any `case` after it is dead code. Python rejects this at
compile time: `SyntaxError: name capture 'other' makes remaining patterns
unreachable` (only the LAST case may be irrefutable). Put your specific cases
first and the catch-all last.
"""


# ======================================================================================
# Scenario 3 - Sequence patterns do not match str / bytes.
# ======================================================================================

def s3_build() -> str:
    line = "move north"
    match line.split():                    # match a LIST of tokens
        case [action, target]:
            return f"{action} -> {target}"
        case _:
            return "unrecognised"


def s3_break() -> str:
    line = "move north"                    # a str, not a list
    match line:
        case [action, target]:            # sequence pattern: str is excluded
            return f"{action} -> {target}"
        case _:
            return "fell through to _"     # this is what happens


def s3_fix() -> str:
    line = "move north"
    match line.split():
        case [action, target]:
            return f"{action} -> {target}"
        case _:
            return "unrecognised"


S3_WHY = """
`str`, `bytes`, and `bytearray` are sequences, but the `match` sequence pattern
deliberately EXCLUDES them - otherwise `case [a, b]:` would match the 2-character
string "hi" and bind its characters, which is almost never intended. Split /
parse the string into a real list (or tuple) first, then match that.
"""


# ======================================================================================
# Scenario 4 - Positional class patterns need __match_args__.
# ======================================================================================

class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y


def s4_build() -> str:
    from dataclasses import dataclass

    @dataclass
    class Pt:                              # dataclass sets __match_args__ = ('x', 'y')
        x: int
        y: int

    match Pt(0, 5):
        case Pt(0, y):
            return f"y-axis at {y}"
        case Pt(x, y):
            return f"({x}, {y})"


def s4_break() -> str:
    try:
        match PlainPoint(0, 0):
            case PlainPoint(0, 0):        # positional, but no __match_args__
                return "origin"
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> str:
    match PlainPoint(0, 0):
        case PlainPoint(x=0, y=0):        # keyword patterns always work
            return "origin"
        case PlainPoint():
            return "some point"


S4_WHY = """
`case Point(0, 0)` is POSITIONAL - it needs the class to declare which attributes
those positions map to, via `__match_args__`. Plain classes don't have it, so a
positional class pattern raises `TypeError: PlainPoint() accepts 0 positional
sub-patterns`. `@dataclass` (and `NamedTuple`) set `__match_args__` for you;
otherwise use keyword sub-patterns (`case Point(x=0, y=0)`), which always work.
"""


SCENARIOS = [
    Scenario("Bare name is a capture", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Irrefutable pattern not last", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Sequence pattern vs a string", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Positional class pattern needs __match_args__", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

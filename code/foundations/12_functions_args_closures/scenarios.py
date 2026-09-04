"""Functions & closures - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/12_functions_args_closures/scenarios.py
"""

from __future__ import annotations

import sys
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Late binding: closures over a loop variable.
# ======================================================================================

def s1_build() -> list[int]:
    handlers = [lambda n=n: n * 10 for n in range(4)]  # bind n now, as a default
    return [h() for h in handlers]  # [0, 10, 20, 30]


def s1_break() -> list[int]:
    handlers = [lambda: n * 10 for n in range(4)]  # all close over the same `n`
    results = [h() for h in handlers]
    assert results == [30, 30, 30, 30], "every handler sees n's final value"
    return results


def s1_fix() -> list[int]:
    handlers = [partial(lambda n: n * 10, n) for n in range(4)]  # freeze at creation
    return [h() for h in handlers]


S1_WHY = """
A closure captures the variable `n`, not its value at the moment the lambda is
created. All four lambdas share one `n`; by the time you call them the loop has
finished and `n` is 3. Bind eagerly: a default argument (`lambda n=n:`) is
evaluated at def time, and `functools.partial` fixes the argument immediately.
"""


# ======================================================================================
# Scenario 2 - Assigning to a captured name without `nonlocal`.
# ======================================================================================

def s2_build() -> int:
    def make_accumulator():
        total = 0

        def add(x):
            nonlocal total
            total += x
            return total

        return add

    acc = make_accumulator()
    acc(10)
    return acc(5)  # 15


def s2_break() -> str:
    def make_accumulator():
        total = 0

        def add(x):
            total += x          # `total` is now LOCAL (it's assigned) -> read fails
            return total

        return add

    acc = make_accumulator()
    try:
        acc(10)
    except UnboundLocalError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s2_fix() -> int:
    def make_accumulator():
        total = 0

        def add(x):
            nonlocal total
            total += x
            return total

        return add

    acc = make_accumulator()
    acc(10)
    return acc(5)


S2_WHY = """
Python decides a name's scope at compile time by scanning the whole function
body: if it is assigned anywhere, it is local for the entire function - so
`total += x` reads a local `total` that has not been assigned yet, hence
`UnboundLocalError`. `nonlocal total` tells the compiler to use (and rebind) the
enclosing one instead.
"""


# ======================================================================================
# Scenario 3 - **kwargs silently swallows a misspelled keyword.
# ======================================================================================

def s3_build() -> float:
    def connect(*, timeout: float = 1.0, retries: int = 3) -> float:
        return timeout * retries  # explicit params -> a typo is a TypeError

    return connect(timeout=5.0)  # 15.0


def s3_break() -> float:
    def connect(**opts) -> float:
        timeout = opts.get("timeout", 1.0)
        retries = opts.get("retries", 3)
        return timeout * retries

    # Caller typo: "timout" instead of "timeout". No error - it's just ignored.
    result = connect(timout=5.0)
    assert result == 3.0, "the default timeout was used; the typo vanished into **opts"
    return result


def s3_fix() -> float:
    def connect(*, timeout: float = 1.0, retries: int = 3) -> float:
        return timeout * retries

    try:
        connect(timout=5.0)          # TypeError: unexpected keyword argument
    except TypeError:
        return connect(timeout=5.0)  # fixed call
    return -1.0


S3_WHY = """
`**kwargs` accepts every keyword argument by name and performs no validation, so
`connect(timout=5.0)` puts `{"timout": 5.0}` in `opts`, `opts.get("timeout")`
misses, and the default is used silently. Declaring the parameters explicitly
(ideally keyword-only) makes an unknown keyword a `TypeError` at the call.
"""


# ======================================================================================
# Scenario 4 - Positional args with an ambiguous order.
# ======================================================================================

def s4_build() -> tuple[int, int]:
    def canvas(*, width: int, height: int) -> tuple[int, int]:
        return width, height  # callers MUST name them

    return canvas(width=1920, height=1080)


def s4_break() -> tuple[int, int]:
    def canvas(width: int, height: int) -> tuple[int, int]:
        return width, height

    # The caller thinks the signature is (height, width). No error - silently wrong.
    intended_height, intended_width = 1080, 1920
    got = canvas(intended_height, intended_width)
    assert got == (1080, 1920) != (intended_width, intended_height)
    return got


def s4_fix() -> tuple[int, int]:
    def canvas(*, width: int, height: int) -> tuple[int, int]:
        return width, height

    return canvas(height=1080, width=1920)  # order no longer matters


S4_WHY = """
Positional arguments bind by position with no name check, so swapping two same-typed
arguments is invisible until something downstream looks wrong. Putting `*` before
the parameters makes them keyword-only: callers must write `width=...,
height=...`, and the order in the call is irrelevant.
"""


SCENARIOS = [
    Scenario("Late binding over a loop variable", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Assigning a captured name without nonlocal", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("**kwargs swallows a typo", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Ambiguous positional arguments", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""Decorators - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/13_decorators/scenarios.py
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Forgetting functools.wraps.
# ======================================================================================

def s1_build() -> tuple[str, str]:
    def announce(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw)
        return wrapper

    @announce
    def greet():
        """Say hi."""
        return "hi"

    return greet.__name__, greet.__doc__  # ('greet', 'Say hi.')


def s1_break() -> tuple[str, str | None]:
    def announce(func):
        def wrapper(*a, **kw):          # no @wraps
            return func(*a, **kw)
        return wrapper

    @announce
    def greet():
        """Say hi."""
        return "hi"

    # Introspection now sees the wrapper, not greet.
    assert greet.__name__ == "wrapper" and greet.__doc__ is None
    return greet.__name__, greet.__doc__


def s1_fix() -> tuple[str, str]:
    def announce(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw)
        return wrapper

    @announce
    def greet():
        """Say hi."""
        return "hi"

    return greet.__name__, greet.__doc__


S1_WHY = """
`@announce` replaces `greet` with the `wrapper` function object, which has its own
`__name__` ("wrapper"), no docstring, and the wrong signature. Tooling
(tracebacks, docs generators, other decorators, `inspect.signature`) then
misreports the function. `functools.wraps(func)` copies `__name__`, `__doc__`,
`__wrapped__`, `__dict__`, etc. from the original onto the wrapper.
"""


# ======================================================================================
# Scenario 2 - Using a decorator factory without calling it.
# ======================================================================================

def _limit(max_len: int):
    if not isinstance(max_len, int):
        raise TypeError(
            f"@_limit expects a length; got {type(max_len).__name__}. "
            f"Did you write @_limit instead of @_limit(n)?"
        )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(s):
            return func(s)[:max_len]
        return wrapper
    return decorator


def s2_build() -> str:
    @_limit(3)                    # call the factory -> get a decorator
    def echo(s):
        return s

    return echo("abcdefg")  # 'abc'


def s2_break() -> str:
    try:
        @_limit                  # forgot the (): _limit gets `echo` as `max_len`
        def echo(s):             # noqa: F841
            return s
        return "no error (unexpected)"
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> str:
    @_limit(3)
    def echo(s):
        return s

    return echo("abcdefg")


S2_WHY = """
`@_limit` means `echo = _limit(echo)`. `_limit` is a *factory*: it expects config
(`max_len`) and returns the real decorator. Passing the function where the length
should go means `echo` silently becomes the inner `decorator` function - unless
the factory validates its argument, as here, and raises. Either way the fix is to
call it: `@_limit(3)`.
"""


# ======================================================================================
# Scenario 3 - A decorator that forgets to return the wrapper.
# ======================================================================================

def s3_build() -> int:
    def double(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw) * 2
        return wrapper           # <- returned

    @double
    def n():
        return 21

    return n()  # 42


def s3_break() -> str:
    def double(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw) * 2
        # oops: no return -> double() returns None

    @double
    def n():
        return 21

    try:
        return n()               # n is None -> TypeError
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s3_fix() -> int:
    def double(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            return func(*a, **kw) * 2
        return wrapper

    @double
    def n():
        return 21

    return n()


S3_WHY = """
`@double` runs `n = double(n)`. If `double` falls off the end without returning,
it returns `None`, so `n` becomes `None` and `n()` raises
`TypeError: 'NoneType' object is not callable`. A decorator must return a callable
- normally the wrapper, sometimes the original function unchanged.
"""


# ======================================================================================
# Scenario 4 - Decorator stacking order.
# ======================================================================================

def _cache(func):
    store = {}

    @functools.wraps(func)
    def wrapper(x):
        if x not in store:
            store[x] = func(x)
        return store[x]

    wrapper.store = store
    return wrapper


def _add_tax(func):
    @functools.wraps(func)
    def wrapper(x):
        return round(func(x) * 1.2, 2)

    return wrapper


def s4_build() -> tuple[float, dict]:
    # @_cache outermost: the FINAL (taxed) value is cached.
    @_cache
    @_add_tax
    def price(item):
        return {"book": 10.0, "pen": 2.0}[item]

    result = price("book")
    return result, dict(price.store)  # (12.0, {'book': 12.0})


def s4_break() -> tuple[float, dict]:
    # Swapped: @_add_tax outermost, @_cache inner -> cache stores the PRE-tax
    # value, and tax is re-applied every call. Still 12.0 here, but the cache
    # now holds 10.0, and if tax were stochastic/rounded oddly you'd see drift.
    @_add_tax
    @_cache
    def price(item):
        return {"book": 10.0, "pen": 2.0}[item]

    result = price("book")
    return result, dict(price.__wrapped__.store)  # (12.0, {'book': 10.0})


def s4_fix() -> tuple[float, dict]:
    @_cache
    @_add_tax
    def price(item):
        return {"book": 10.0, "pen": 2.0}[item]

    return price("book"), dict(price.store)


S4_WHY = """
`@a` above `@b` above `def f` means `f = a(b(f))`. The decorator nearest the
`def` wraps first (innermost); the top one wraps last (outermost) and runs first
on each call. So `@_cache` on top caches the fully post-processed result;
`@_cache` underneath caches the raw result and every later stage re-runs. Order
your decorators by what layer you want memoised / authed / logged.
"""


SCENARIOS = [
    Scenario("Forgetting functools.wraps", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Factory used without calling it", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Decorator returns nothing", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Stacking order", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

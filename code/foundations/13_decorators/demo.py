"""Decorators - the practice snippet.

Run it:  python code/foundations/13_decorators/demo.py

Mental model:
    @deco
    def f(...): ...

is exactly  `f = deco(f)`  - run right after the `def`. A decorator is a callable
that takes a function and returns a replacement (usually a wrapper that calls the
original). A decorator WITH ARGUMENTS is a function that returns a decorator, so
there are three layers: factory(args) -> decorator(func) -> wrapper(*a, **kw).
"""

from __future__ import annotations

import functools
import time


def timed(func):
    """A plain decorator: wrap `func`, timing each call."""

    @functools.wraps(func)                 # copy __name__, __doc__, etc. onto wrapper
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        wrapper.last_ms = (time.perf_counter() - start) * 1000
        return result

    wrapper.last_ms = 0.0
    return wrapper


def retry(times: int):
    """A decorator factory: retry(times) returns the actual decorator."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ValueError as exc:
                    last = exc
            raise RuntimeError(f"failed after {times} attempts") from last

        return wrapper

    return decorator


@timed
def slow_square(n: int) -> int:
    """Square n, slowly."""
    time.sleep(0.01)
    return n * n


_flaky_calls = {"n": 0}


@retry(times=3)
def flaky() -> str:
    _flaky_calls["n"] += 1
    if _flaky_calls["n"] < 3:
        raise ValueError("not yet")
    return f"ok on attempt {_flaky_calls['n']}"


def decoration_happens_at_def_time() -> None:
    print("  defining announced()...")

    def announce(func):
        print(f"  >> decorator ran for {func.__name__} (at def time, before any call)")
        return func

    @announce
    def announced():
        return 1

    print("  ...done defining")


def main() -> None:
    print("slow_square(9) =", slow_square(9), f"(took ~{slow_square.last_ms:.1f} ms)")
    print("wraps kept metadata: name =", slow_square.__name__,
          "| doc =", slow_square.__doc__)
    print("flaky() ->", flaky())
    print()
    decoration_happens_at_def_time()


if __name__ == "__main__":
    main()

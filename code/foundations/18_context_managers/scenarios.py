"""Context managers - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/18_context_managers/scenarios.py
"""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

OUT = generated_dir("ctx_scenarios")


# ======================================================================================
# Scenario 1 - Manual open/close leaks the file when the body raises.
# ======================================================================================

def _tracked_open(path: Path, registry: list[str]):
    fh = path.open("w", encoding="utf-8")
    original_close = fh.close

    def close():
        registry.append("closed")
        original_close()

    fh.close = close  # type: ignore[method-assign]
    return fh


def s1_build() -> list[str]:
    path = OUT / "a.txt"
    events: list[str] = []
    with contextlib.suppress(RuntimeError):
        with _tracked_open(path, events):
            raise RuntimeError("boom in the body")
    return events  # ['closed'] - `with` closed it despite the exception


def s1_break() -> list[str]:
    path = OUT / "b.txt"
    events: list[str] = []
    fh = _tracked_open(path, events)
    try:
        raise RuntimeError("boom in the body")
        fh.close()  # never reached
    except RuntimeError:
        pass
    return events  # [] - the file was never closed


def s1_fix() -> list[str]:
    path = OUT / "c.txt"
    events: list[str] = []
    with contextlib.suppress(RuntimeError):
        with _tracked_open(path, events):
            raise RuntimeError("boom in the body")
    return events


S1_WHY = """
`with` compiles the close into a `finally`-like guarantee: `__exit__` runs on
normal exit, on `return`, and on exception. Hand-rolled `open(...); ...;
.close()` only closes if control reaches the `.close()` line - an exception (or an
early `return`) skips it and the file descriptor leaks until garbage collection.
"""


# ======================================================================================
# Scenario 2 - @contextmanager without try/finally.
# ======================================================================================

def s2_build() -> list[str]:
    log: list[str] = []

    @contextlib.contextmanager
    def session():
        log.append("open")
        try:
            yield
        finally:
            log.append("close")   # runs even if the body raises

    with contextlib.suppress(ValueError):
        with session():
            raise ValueError("body failed")
    return log  # ['open', 'close']


def s2_break() -> list[str]:
    log: list[str] = []

    @contextlib.contextmanager
    def session():
        log.append("open")
        yield
        log.append("close")       # NOT in a finally -> skipped on exception

    with contextlib.suppress(ValueError):
        with session():
            raise ValueError("body failed")
    return log  # ['open'] - 'close' never ran


def s2_fix() -> list[str]:
    log: list[str] = []

    @contextlib.contextmanager
    def session():
        log.append("open")
        try:
            yield
        finally:
            log.append("close")

    with contextlib.suppress(ValueError):
        with session():
            raise ValueError("body failed")
    return log


S2_WHY = """
When the `with` body raises, `@contextmanager` throws that exception INTO the
generator at the `yield`. If the code after `yield` is not protected by
`try/finally`, the exception propagates straight out of the generator and your
cleanup line is never reached. Always wrap the `yield` in `try/finally` (or
`try/except` if you mean to handle it).
"""


# ======================================================================================
# Scenario 3 - __exit__ accidentally suppresses exceptions.
# ======================================================================================

class QuietCtx:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False   # cleanup would go here; False = do not suppress


class BuggyCtx:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return True   # <- suppresses EVERY exception in the body


def s3_build() -> str:
    try:
        with QuietCtx():
            raise ValueError("real error")
    except ValueError as exc:
        return f"propagated: {exc}"
    return "swallowed (unexpected)"


def s3_break() -> str:
    try:
        with BuggyCtx():
            raise ValueError("real error")
    except ValueError as exc:
        return f"propagated: {exc}"
    return "swallowed: the exception vanished"


def s3_fix() -> str:
    class FixedCtx:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False  # or None - do not suppress

    try:
        with FixedCtx():
            raise ValueError("real error")
    except ValueError as exc:
        return f"propagated: {exc}"
    return "swallowed (unexpected)"


S3_WHY = """
`__exit__` is asked "did you handle the exception?" A truthy return means "yes,
suppress it"; falsy (`False`/`None`) means "no, let it propagate". Returning
`True` unconditionally - or accidentally returning a truthy value - silently eats
every error raised in the `with` body. Return `False` or `None` unless you
genuinely handled a specific exception.
"""


# ======================================================================================
# Scenario 4 - Reusing a one-shot @contextmanager object.
# ======================================================================================

@contextlib.contextmanager
def _phase(name: str):
    yield name


def s4_build() -> list[str]:
    seen = []
    for name in ("a", "b"):
        with _phase(name) as n:   # a FRESH context manager each iteration
            seen.append(n)
    return seen  # ['a', 'b']


def s4_break() -> str:
    cm = _phase("x")              # one context-manager object...
    with cm:
        pass
    try:
        with cm:                  # ...reused: its generator is already exhausted
            pass
    except Exception as exc:      # RuntimeError / AttributeError depending on version
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> list[str]:
    seen = []
    for name in ("x", "y"):
        with _phase(name) as n:   # call the factory again -> new generator
            seen.append(n)
    return seen


S4_WHY = """
A `@contextmanager` function returns a context manager wrapping a generator, and a
generator runs once. Entering it a second time raises
`RuntimeError: generator didn't yield` (it already returned). Create a new
context manager per `with` by calling the factory each time. (`threading.Lock` is
reusable but NOT reentrant - nesting `with lock` deadlocks; use `RLock`.)
"""


SCENARIOS = [
    Scenario("Manual close leaks on exception", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("@contextmanager without try/finally", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("__exit__ suppresses exceptions", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Reusing a one-shot context manager", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

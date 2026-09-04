"""Exceptions - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/17_exceptions/scenarios.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - A too-broad except swallows a real bug.
# ======================================================================================

def _parse_amount(raw: str) -> float:
    return float(raw.strip())


def s1_build() -> float:
    try:
        return _parse_amount("  12.50 ")
    except ValueError:
        return 0.0  # catch only what we expect


def s1_break() -> float:
    try:
        # Typo: `.strp()` instead of `.strip()` -> AttributeError, a real bug.
        return float(" 12.50 ".strp())  # type: ignore[attr-defined]
    except Exception:
        return 0.0   # swallows the AttributeError; caller sees a plausible 0.0


def s1_fix() -> str:
    try:
        return str(float(" 12.50 ".strp()))  # type: ignore[attr-defined]
    except ValueError:
        return "0.0"                          # only ValueError is caught...
    except AttributeError as exc:             # ...the bug now surfaces
        return f"{type(exc).__name__}: {exc}"


S1_WHY = """
`except Exception` (or a bare `except:`) catches everything derived from
Exception - including `AttributeError`, `NameError`, `TypeError` from your own
mistakes. The program keeps running with a wrong-but-plausible value and the bug
hides for weeks. Catch the narrowest exception that represents an expected,
recoverable condition.
"""


# ======================================================================================
# Scenario 2 - `return` inside `finally`.
# ======================================================================================

def s2_build() -> str:
    def read() -> str:
        try:
            raise IOError("disk gone")
        finally:
            pass  # cleanup only; no control flow
    try:
        read()
    except IOError as exc:
        return f"propagated: {exc}"


def s2_break() -> str:
    # `return` inside `finally` is a SyntaxWarning in modern Python (the language
    # itself flags it), so it is built here with exec to keep that warning local.
    import warnings

    ns: dict = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        exec(
            "def read():\n"
            "    try:\n"
            "        raise IOError('disk gone')\n"
            "    finally:\n"
            "        return 'ok'   # swallows the exception entirely\n",
            ns,
        )
    return ns["read"]()   # "ok" - the IOError vanished


def s2_fix() -> str:
    def read() -> str:
        try:
            raise IOError("disk gone")
        finally:
            pass
    try:
        read()
    except IOError as exc:
        return f"propagated: {exc}"


S2_WHY = """
`finally` runs on the way out no matter what, and if it executes `return` (or
`break`/`continue`), that control-flow action REPLACES whatever the `try` block
was doing - including an in-flight exception, which is silently discarded. Keep
`finally` to cleanup; never `return` from it.
"""


# ======================================================================================
# Scenario 3 - Re-raising without chaining loses the root cause.
# ======================================================================================

class LoadError(Exception):
    pass


def s3_build() -> tuple[str, str]:
    def load(cfg: dict):
        try:
            return int(cfg["retries"])
        except KeyError as exc:
            raise LoadError("bad config") from exc  # keep the cause

    try:
        load({})
    except LoadError as exc:
        return type(exc.__cause__).__name__, str(exc.__cause__)  # ('KeyError', "'retries'")


def s3_break() -> str | None:
    def load(cfg: dict):
        try:
            return int(cfg["retries"])
        except KeyError:
            raise LoadError("bad config")  # no `from` -> __cause__ is None

    try:
        load({})
    except LoadError as exc:
        return exc.__cause__  # None - the KeyError detail is not the explicit cause


def s3_fix() -> tuple[str, str]:
    def load(cfg: dict):
        try:
            return int(cfg["retries"])
        except KeyError as exc:
            raise LoadError(f"bad config: missing {exc}") from exc

    try:
        load({})
    except LoadError as exc:
        return type(exc.__cause__).__name__, str(exc)


S3_WHY = """
`raise New() from original` sets `New.__cause__ = original` and the traceback
shows "The above exception was the direct cause...". Without `from`, `__cause__`
is None (Python still keeps `__context__` implicitly, but tools and `raise ...
from None` can hide it). Always chain when translating one exception into another
so the root cause survives.
"""


# ======================================================================================
# Scenario 4 - A half-applied side effect when an exception interrupts.
# ======================================================================================

def s4_build() -> dict:
    account = {"balance": 100, "log": []}

    def withdraw(amount: int) -> None:
        if amount > account["balance"]:
            raise ValueError("insufficient funds")   # check BEFORE mutating
        account["balance"] -= amount
        account["log"].append(f"-{amount}")

    try:
        withdraw(150)
    except ValueError:
        pass
    return account  # untouched: {'balance': 100, 'log': []}


def s4_break() -> dict:
    account = {"balance": 100, "log": []}

    def withdraw(amount: int) -> None:
        account["balance"] -= amount                 # mutate first...
        if account["balance"] < 0:
            raise ValueError("insufficient funds")   # ...then fail
        account["log"].append(f"-{amount}")

    try:
        withdraw(150)
    except ValueError:
        pass
    # balance is now -50 and there is no log entry: inconsistent state.
    assert account == {"balance": -50, "log": []}
    return account


def s4_fix() -> dict:
    account = {"balance": 100, "log": []}

    def withdraw(amount: int) -> None:
        new_balance = account["balance"] - amount    # compute, don't commit
        if new_balance < 0:
            raise ValueError("insufficient funds")
        account["balance"] = new_balance             # commit only once it's valid
        account["log"].append(f"-{amount}")

    try:
        withdraw(150)
    except ValueError:
        pass
    return account


S4_WHY = """
An exception interrupts a function partway through; any state you already changed
stays changed. If you decrement the balance and then validate, a failed
withdrawal leaves a negative balance and no matching log entry. Validate first,
compute new values without committing, then apply them last - or wrap the whole
operation so a failure rolls back (a context manager, a DB transaction).
"""


SCENARIOS = [
    Scenario("Too-broad except hides a bug", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("return inside finally", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Re-raising without chaining", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Half-applied side effect", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

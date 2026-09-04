"""Exceptions: EAFP, chaining, groups - the practice snippet.

Run it:  python code/foundations/17_exceptions/demo.py

Mental model:
- An exception is an object. `raise` starts it travelling up the call stack; each
  frame either catches it (a matching `except`) or lets it keep going. Uncaught,
  it reaches the top and prints a traceback.
- `try / except / else / finally`: `else` runs only if no exception; `finally`
  runs no matter what (exception, return, or normal fall-through).
- EAFP ("easier to ask forgiveness than permission"): just do the thing and catch
  the failure, rather than pre-checking every condition (LBYL).
- `raise New() from original` records `original` as the cause, keeping the full
  story for debugging.
"""

from __future__ import annotations

import sys


class ConfigError(Exception):
    """Raised when configuration is invalid."""


def eafp_vs_lbyl(data: dict, key: str) -> str:
    # EAFP
    try:
        return f"eafp -> {data[key]}"
    except KeyError:
        return "eafp -> missing"


def clause_order() -> None:
    for value in (10, 0):
        try:
            result = 100 // value
        except ZeroDivisionError:
            print(f"  {value}: except (division failed)")
        else:
            print(f"  {value}: else (ok, result={result})")
        finally:
            print(f"  {value}: finally (always)")


def chaining() -> None:
    def load(raw: dict) -> int:
        try:
            return int(raw["port"])
        except (KeyError, ValueError) as exc:
            raise ConfigError("could not read 'port'") from exc

    try:
        load({"prt": "8080"})
    except ConfigError as exc:
        print("  caught:", exc)
        print("  __cause__ is the original:", repr(exc.__cause__))


def exception_groups() -> None:
    if sys.version_info < (3, 11):
        print("  (exception groups need Python 3.11+)")
        return
    try:
        raise ExceptionGroup(
            "validation failed",
            [ValueError("bad email"), KeyError("name"), ValueError("bad age")],
        )
    except* ValueError as eg:
        print("  handled ValueErrors:", [str(e) for e in eg.exceptions])
    except* KeyError as eg:
        print("  handled KeyErrors:", [str(e) for e in eg.exceptions])


def main() -> None:
    print(eafp_vs_lbyl({"a": 1}, "a"))
    print(eafp_vs_lbyl({"a": 1}, "z"))
    print()
    clause_order()
    print()
    chaining()
    print()
    exception_groups()


if __name__ == "__main__":
    main()

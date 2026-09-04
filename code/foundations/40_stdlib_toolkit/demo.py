"""stdlib toolkit: argparse, enum, subprocess - the practice snippet.

Run it:  python code/foundations/40_stdlib_toolkit/demo.py

Three everyday tools:
- argparse   : declare a command-line interface; `parse_args` turns argv into an
               object. Values are strings unless you pass `type=`.
- enum       : a fixed set of named constants. Members are SINGLETONS - compare
               with `is`. `Flag` for combinable bit options.
- subprocess : run external programs. Pass a LIST of args (never a shell string
               with interpolated input). `check=True` to raise on failure.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from enum import Enum, Flag, auto


def argparse_demo() -> None:
    parser = argparse.ArgumentParser(prog="report")
    parser.add_argument("path")                                  # positional
    parser.add_argument("--limit", type=int, default=10)         # typed option
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args(["data.csv", "--limit", "3", "--verbose"])
    print("parsed:", vars(args))
    print("limit is an int:", isinstance(args.limit, int))


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


def enum_demo() -> None:
    print("members:", [c.name for c in Color])
    print("Color.RED is Color.RED:", Color.RED is Color.RED)      # singleton
    print("Color('green'):", Color("green"))                       # lookup by value
    combined = Perm.READ | Perm.WRITE
    print("combined flag:", combined, "| WRITE in it:", Perm.WRITE in combined)


def subprocess_demo() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "print('hello from a child')"],
        capture_output=True, text=True, check=True,
    )
    print("child stdout:", result.stdout.strip(), "| returncode:", result.returncode)

    failed = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"])
    print("without check=True, a failure is just a returncode:", failed.returncode)


def main() -> None:
    argparse_demo()
    print()
    enum_demo()
    print()
    subprocess_demo()


if __name__ == "__main__":
    main()

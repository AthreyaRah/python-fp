"""Tiny shared structure for a topic's four scenarios.

Each scenario is one story: build something small, break it with a single precise
change, fix it, and explain why the broken version behaved the way it did.

`break_fn` should EITHER return a value that is observably wrong OR raise. The
`test_topic.py` for each topic asserts the specifics; `run()` here just narrates.
"""

from __future__ import annotations

import traceback
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    title: str
    build_fn: Callable[[], object]
    break_fn: Callable[[], object]
    fix_fn: Callable[[], object]
    why: str

    def run(self) -> None:
        print(f"\n=== {self.title} ===")
        print("  🔨 build :", _call(self.build_fn))
        print("  💥 break :", _call(self.break_fn))
        print("  🔧 fix   :", _call(self.fix_fn))
        print("  🧠 why   :", " ".join(self.why.split()))


def _call(fn: Callable[[], object]) -> str:
    try:
        return f"returned {fn()!r}"
    except Exception as exc:  # noqa: BLE001 - we are deliberately showing failures
        return f"raised {type(exc).__name__}: {exc}\n" + _indent(traceback.format_exc())


def _indent(text: str, prefix: str = "      ") -> str:
    return "".join(prefix + line for line in text.splitlines(keepends=True))


def run_all(scenarios: list[Scenario]) -> None:
    for scenario in scenarios:
        scenario.run()

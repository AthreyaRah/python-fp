"""Run every topic's demo.py as a subprocess and report a pass/fail table.

    python code/_harness/run_all.py            # all tracks
    python code/_harness/run_all.py foundations data-engineering

This is the "does anything rot?" check that does not need pytest. CI runs it too.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent.parent


def find_demos(tracks: list[str]) -> list[Path]:
    roots = (
        [CODE_ROOT / t for t in tracks]
        if tracks
        else [p for p in CODE_ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")]
    )
    demos: list[Path] = []
    for root in roots:
        if root.exists():
            demos.extend(sorted(root.glob("*/demo.py")))
    return demos


def main(argv: list[str]) -> int:
    demos = find_demos(argv)
    if not demos:
        print("no demo.py files found yet")
        return 0

    width = max(len(str(d.relative_to(CODE_ROOT))) for d in demos)
    failures = 0
    for demo in demos:
        rel = str(demo.relative_to(CODE_ROOT))
        started = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(demo)],
            capture_output=True,
            text=True,
            cwd=CODE_ROOT.parent,
        )
        elapsed = time.perf_counter() - started
        ok = proc.returncode == 0
        failures += not ok
        print(f"{rel:<{width}}  {'ok  ' if ok else 'FAIL'}  {elapsed:6.2f}s")
        if not ok:
            print("--- stdout ---\n" + proc.stdout)
            print("--- stderr ---\n" + proc.stderr)

    print(f"\n{len(demos) - failures}/{len(demos)} demos ran clean")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

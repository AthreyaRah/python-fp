"""Context managers & with - the practice snippet.

Run it:  python code/foundations/18_context_managers/demo.py

Mental model:
    with cm as x:
        body

is:  x = cm.__enter__()
     try: body
     finally-ish: cm.__exit__(exc_type, exc_value, traceback)

`__exit__` is GUARANTEED to run - on normal exit, on `return`, and on exception.
If it returns a truthy value, the exception is suppressed. `@contextmanager`
turns a one-`yield` generator into a context manager: everything before `yield`
is `__enter__`, everything after (put it in `finally`!) is `__exit__`.
"""

from __future__ import annotations

import contextlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402


class Timer:
    """A context manager as a class."""

    def __enter__(self) -> Timer:
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, tb) -> bool:
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000
        return False  # don't suppress exceptions


@contextlib.contextmanager
def tag(name: str):
    """The same idea as a generator."""
    print(f"  <{name}>")
    try:
        yield name
    finally:
        print(f"  </{name}>")


def class_based() -> None:
    with Timer() as t:
        sum(range(200_000))
    print(f"  Timer measured ~{t.elapsed_ms:.1f} ms")


def generator_based() -> None:
    with tag("outer"), tag("inner"):
        print("    body")


def exit_runs_even_on_exception() -> None:
    try:
        with tag("guarded"):
            raise ValueError("boom")
    except ValueError:
        print("  exception propagated, but </guarded> still printed")


def exitstack_for_many() -> None:
    d = generated_dir("ctx_demo")
    paths = [d / f"part{i}.txt" for i in range(3)]
    for i, p in enumerate(paths):
        p.write_text(f"file {i}\n", encoding="utf-8")

    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(p.open(encoding="utf-8")) for p in paths]
        print("  opened", len(files), "files; first lines:",
              [f.readline().strip() for f in files])
    # all three closed here, in reverse order


def suppressing() -> None:
    with contextlib.suppress(FileNotFoundError):
        Path("/no/such/file").read_text()
    print("  suppress(FileNotFoundError): carried on")


def main() -> None:
    class_based()
    print()
    generator_based()
    print()
    exit_runs_even_on_exception()
    print()
    exitstack_for_many()
    print()
    suppressing()


if __name__ == "__main__":
    main()

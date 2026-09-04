"""The GIL, threads & race conditions — the practice snippet.

Run it:  python code/foundations/33_gil_threads_races/demo.py

Mental model: in CPython the Global Interpreter Lock lets exactly one thread
execute bytecode at a time. That does NOT make your code thread-safe. The
interpreter can (and does) switch threads *between* bytecode instructions, and a
single line like `counter += 1` is several instructions. If a switch lands in the
middle, two threads read the same value and one update is lost.
"""

from __future__ import annotations

import dis
import sys
import threading


def show_that_plus_equals_is_not_atomic() -> None:
    print("Bytecode for `counter += 1`:")
    dis.dis("counter += 1")
    # LOAD_NAME counter / LOAD_CONST 1 / BINARY_OP += / STORE_NAME counter
    # Four steps. A thread switch between LOAD and STORE is where updates vanish.


def race_the_counter(threads: int = 8, per_thread: int = 100_000) -> int:
    counter = 0

    def worker() -> None:
        nonlocal counter
        for _ in range(per_thread):
            counter += 1  # read, add, write — interruptible in the gap

    workers = [threading.Thread(target=worker) for _ in range(threads)]
    for t in workers:
        t.start()
    for t in workers:
        t.join()

    expected = threads * per_thread
    print(f"race_the_counter: got {counter:,} / expected {expected:,} "
          f"(lost {expected - counter:,})")
    return counter


def safe_counter(threads: int = 8, per_thread: int = 100_000) -> int:
    counter = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal counter
        for _ in range(per_thread):
            with lock:  # the read-modify-write is now indivisible
                counter += 1

    workers = [threading.Thread(target=worker) for _ in range(threads)]
    for t in workers:
        t.start()
    for t in workers:
        t.join()

    expected = threads * per_thread
    print(f"safe_counter:     got {counter:,} / expected {expected:,}")
    return counter


def main() -> None:
    print(f"Python {sys.version.split()[0]}  |  GIL enabled: "
          f"{getattr(sys, '_is_gil_enabled', lambda: True)()}\n")
    show_that_plus_equals_is_not_atomic()
    print()
    # Run the race a few times: the loss is nondeterministic, sometimes 0.
    for _ in range(3):
        race_the_counter()
    safe_counter()


if __name__ == "__main__":
    main()

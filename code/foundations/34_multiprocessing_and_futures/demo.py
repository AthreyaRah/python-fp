"""multiprocessing & concurrent.futures - the practice snippet.

Run it:  python code/foundations/34_multiprocessing_and_futures/demo.py

Mental model:
- Threads share memory but are serialised by the GIL for CPU-bound Python work.
  PROCESSES have separate memory, so they run Python bytecode truly in parallel.
- The cost: arguments and return values cross the process boundary by PICKLING,
  process startup is not free, and there is no shared state (use Queue, Pipe,
  Value, Array, or Manager, or just return results).
- With the 'spawn' start method (default on macOS/Windows) each worker RE-IMPORTS
  your module, so multiprocessing code needs an `if __name__ == "__main__":`
  guard.
- `concurrent.futures`: ThreadPoolExecutor for I/O-bound, ProcessPoolExecutor for
  CPU-bound. `.submit()` returns a Future; `.result()` returns the value or
  re-raises the worker's exception.
"""

from __future__ import annotations

import multiprocessing as mp
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

# This teaching file uses 'fork' so it runs both as a script and when imported by
# the test suite. In production, 'spawn' is the safe default (see Pitfalls) and
# needs the `if __name__ == "__main__":` guard, which this file also has.
_CTX = mp.get_context("fork") if sys.platform != "win32" else None


def slow_square(n: int) -> int:
    total = 0
    for i in range(2_000_000):        # CPU-bound busy work
        total += (i * n) % 7
    return n * n


def io_task(label: str) -> str:
    time.sleep(0.05)                  # stand-in for a network/disk wait
    return f"{label}-done"


def cpu_parallelism() -> None:
    nums = [1, 2, 3, 4]

    t0 = time.perf_counter()
    serial = [slow_square(n) for n in nums]
    serial_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4, mp_context=_CTX) as ex:
        parallel = list(ex.map(slow_square, nums))
    parallel_s = time.perf_counter() - t0

    print(f"serial   : {serial}  in {serial_s:.2f}s")
    print(f"processes: {parallel}  in {parallel_s:.2f}s")


def threads_for_io() -> None:
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(io_task, [f"req{i}" for i in range(8)]))
    print("8 io tasks via threads:", results[:2], "...")


def exception_propagation() -> None:
    def will_fail(x):
        return 10 // x

    with ThreadPoolExecutor() as ex:
        fut = ex.submit(will_fail, 0)
        try:
            fut.result()
        except ZeroDivisionError as exc:
            print("worker exception re-raised on .result():", exc)


def as_completed_demo() -> None:
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(io_task, f"t{i}"): i for i in range(4)}
        order = [futures[f] for f in as_completed(futures)]
    print("as_completed yields in finish order, e.g.:", order)


def main() -> None:
    cpu_parallelism()
    print()
    threads_for_io()
    print()
    exception_propagation()
    print()
    as_completed_demo()


if __name__ == "__main__":     # REQUIRED for multiprocessing under 'spawn'
    main()

"""multiprocessing & futures - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/34_multiprocessing_and_futures/scenarios.py
"""

from __future__ import annotations

import multiprocessing as mp
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# 'fork' avoids re-importing this module in each worker, so the scenarios run
# inside pytest. In real code, 'spawn' is the safe default and needs an
# `if __name__ == "__main__":` guard (see the page's Pitfalls).
_CTX = mp.get_context("fork") if sys.platform != "win32" else None

_COUNTER = 0


def _square(n: int) -> int:
    return n * n


def _cpu_heavy(n: int) -> int:
    total = 0
    for i in range(1_500_000):
        total += (i ^ n) % 5
    return total


def _increment_global(_n: int) -> int:
    global _COUNTER
    _COUNTER += 1                 # mutates THIS process's copy only
    return _COUNTER


def _boom(_n: int) -> int:
    raise ValueError("worker failed")


# ======================================================================================
# Scenario 1 - Threads vs processes for CPU-bound work.
# ======================================================================================

def _elapsed(executor_factory) -> float:
    work = [1, 2, 3, 4]
    t0 = time.perf_counter()
    with executor_factory() as ex:
        list(ex.map(_cpu_heavy, work))
    return time.perf_counter() - t0


def s1_build() -> float:
    return _elapsed(lambda: ProcessPoolExecutor(max_workers=4, mp_context=_CTX))


def s1_break() -> bool:
    threads = _elapsed(lambda: ThreadPoolExecutor(max_workers=4))
    procs = _elapsed(lambda: ProcessPoolExecutor(max_workers=4, mp_context=_CTX))
    # 4 CPU-bound tasks: threads take turns under the GIL (~serial); processes
    # run in parallel. On a multi-core box the process version is clearly faster.
    return threads > procs * 1.5


def s1_fix() -> float:
    return _elapsed(lambda: ProcessPoolExecutor(max_workers=4, mp_context=_CTX))


S1_WHY = """
CPU-bound Python threads are serialised by the GIL - four of them finish in about
the same wall time as running the work one after another. Separate PROCESSES each
have their own interpreter and GIL, so they run in true parallel on multiple
cores. Use `ThreadPoolExecutor` for I/O-bound work (the waiting thread releases
the GIL) and `ProcessPoolExecutor` for CPU-bound work.
"""


# ======================================================================================
# Scenario 2 - Passing an unpicklable argument to a process pool.
# ======================================================================================

def s2_build() -> list[int]:
    with ProcessPoolExecutor(max_workers=2, mp_context=_CTX) as ex:
        return list(ex.map(_square, [1, 2, 3, 4]))   # module-level fn, plain ints


def s2_break() -> str:
    a_lambda = lambda n: n * n            # noqa: E731 - lambdas can't be pickled
    try:
        with ProcessPoolExecutor(max_workers=2, mp_context=_CTX) as ex:
            list(ex.map(a_lambda, [1, 2, 3]))
    except Exception as exc:              # PicklingError / AttributeError
        return type(exc).__name__
    return "no error (unexpected)"


def s2_fix() -> list[int]:
    with ProcessPoolExecutor(max_workers=2, mp_context=_CTX) as ex:
        return list(ex.map(_square, [1, 2, 3]))


S2_WHY = """
A ProcessPoolExecutor sends the callable and its arguments to the worker by
PICKLING them. Lambdas, local (nested) functions, open file handles, DB
connections, and objects with unpicklable attributes cannot cross that boundary,
so `map`/`submit` raise a pickling error. Use module-level functions and plain
data; `functools.partial` of a module-level function is picklable.
"""


# ======================================================================================
# Scenario 3 - Expecting a global to be shared across processes.
# ======================================================================================

def s3_build() -> int:
    with ProcessPoolExecutor(max_workers=3, mp_context=_CTX) as ex:
        results = list(ex.map(_square, [1, 2, 3, 4, 5]))
    return sum(results)  # combine RESULTS in the parent -> 55


def s3_break() -> int:
    global _COUNTER
    _COUNTER = 0
    with ProcessPoolExecutor(max_workers=3, mp_context=_CTX) as ex:
        list(ex.map(_increment_global, range(10)))
    # Each worker incremented its OWN copy; the parent's is untouched.
    return _COUNTER  # 0


def s3_fix() -> int:
    with ThreadPoolExecutor(max_workers=3) as ex:   # threads DO share memory...
        counts = list(ex.map(_square, range(10)))    # ...but returning values is cleaner
    return len(counts)  # 10


S3_WHY = """
Processes do not share memory. `_increment_global` runs in a child that has its
own copy of every module global, so the parent's `_COUNTER` never changes.
Coordinate through return values (map/submit, then combine in the parent), or
explicit shared objects: `multiprocessing.Value`/`Array` (with a lock),
`Manager().dict()`, or a `Queue`.
"""


# ======================================================================================
# Scenario 4 - A worker exception you never retrieve.
# ======================================================================================

def s4_build() -> str:
    with ThreadPoolExecutor() as ex:
        fut = ex.submit(_boom, 1)
        try:
            fut.result()                 # retrieving the result re-raises
        except ValueError as exc:
            return f"caught: {exc}"
    return "no exception seen (unexpected)"


def s4_break() -> str:
    with ThreadPoolExecutor() as ex:
        ex.submit(_boom, 1)              # fire and forget - never call .result()
    # The exception happened but is trapped inside the (now discarded) Future.
    return "nothing"


def s4_fix() -> str:
    errors = []
    with ThreadPoolExecutor() as ex:
        futures = [ex.submit(_boom, i) for i in range(3)]
        for fut in as_completed(futures):
            try:
                fut.result()
            except ValueError as exc:
                errors.append(str(exc))
    return f"{len(errors)} errors surfaced"


S4_WHY = """
`submit` returns a `Future` that stores either the result or the exception. If
you never call `.result()` (or `.exception()`, or iterate `as_completed`), a
worker failure is silently swallowed when the Future is garbage-collected. Always
retrieve every result - loop over `as_completed`, or use `executor.map`, which
re-raises on iteration.
"""


SCENARIOS = [
    Scenario("Threads vs processes for CPU work", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Unpicklable argument", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Global not shared across processes", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Unretrieved worker exception", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

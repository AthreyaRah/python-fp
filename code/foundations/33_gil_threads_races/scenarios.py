"""The GIL, threads & races — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/33_gil_threads_races/scenarios.py

Every "break" here is made reliable for CI by widening the race window with an
explicit read/write split and a `time.sleep(0)` yield. The bugs are real at full
speed too — just rarer.
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

THREADS = 8
N = 2_000


def _spawn(target) -> None:
    workers = [threading.Thread(target=target) for _ in range(THREADS)]
    for t in workers:
        t.start()
    for t in workers:
        t.join()


# ======================================================================================
# Scenario 1 — Lost updates on a shared counter.
# ======================================================================================

def s1_build() -> int:
    hits = 0
    for _ in range(THREADS * N):
        hits += 1
    return hits


def s1_break(attempts: int = 5) -> tuple[int, int]:
    def run() -> int:
        hits = 0

        def worker() -> None:
            nonlocal hits
            for _ in range(N):
                current = hits
                time.sleep(0)
                hits = current + 1

        _spawn(worker)
        return hits

    expected = THREADS * N
    for _ in range(attempts):
        got = run()
        if got < expected:
            return got, expected
    return got, expected


def s1_fix() -> tuple[int, int]:
    hits = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal hits
        for _ in range(N):
            with lock:
                current = hits
                time.sleep(0)
                hits = current + 1

    _spawn(worker)
    return hits, THREADS * N


S1_WHY = """
`hits = current + 1` compiles to load / add / store. The GIL lets only one thread
run bytecode at once but releases it periodically, so two threads can both load
41, both store 42: one increment is lost. The lock makes the load-add-store
indivisible with respect to other threads.
"""


# ======================================================================================
# Scenario 2 — Check-then-act: a cache initialised more than once.
# ======================================================================================

def s2_build() -> int:
    cache: dict[str, int] = {}
    init_calls = 0

    def expensive() -> int:
        nonlocal init_calls
        init_calls += 1
        return 42

    if "key" not in cache:
        cache["key"] = expensive()
    return init_calls  # 1


def s2_break(attempts: int = 5) -> int:
    def run() -> int:
        cache: dict[str, int] = {}
        init_calls = 0
        count_lock = threading.Lock()
        gate = threading.Barrier(THREADS)  # release all threads at the check together

        def get() -> None:
            nonlocal init_calls
            gate.wait()
            if "key" not in cache:              # CHECK
                time.sleep(0.005)               # ... window for other threads
                with count_lock:
                    init_calls += 1             # count the "expensive" init
                cache["key"] = 42               # ACT

        _spawn(get)
        return init_calls

    for _ in range(attempts):
        calls = run()
        if calls > 1:
            return calls
    return calls


def s2_fix() -> int:
    cache: dict[str, int] = {}
    init_calls = 0
    lock = threading.Lock()

    def get() -> None:
        nonlocal init_calls
        for _ in range(50):
            with lock:                          # check AND act under one lock
                if "key" not in cache:
                    time.sleep(0)
                    init_calls += 1
                    cache["key"] = 42

    _spawn(get)
    return init_calls  # 1


S2_WHY = """
`if "key" not in cache` and `cache["key"] = ...` are two separate operations.
Between them the GIL can move to another thread that also sees the key missing.
Both threads run the "expensive" init. The fix holds one lock across the check
and the act so only one thread can be in that section.
"""


# ======================================================================================
# Scenario 3 — Deadlock from inconsistent lock ordering.
# ======================================================================================

def _transfer(first: threading.Lock, second: threading.Lock, hold: float) -> bool:
    """Acquire `first`, wait, then try `second` with a timeout. True if both held."""
    first.acquire()
    try:
        time.sleep(hold)
        got = second.acquire(timeout=0.5)
        if got:
            second.release()
        return got
    finally:
        first.release()


def s3_build() -> bool:
    a, b = threading.Lock(), threading.Lock()
    results: list[bool] = []
    # Both threads take the locks in the SAME order: a then b.
    t1 = threading.Thread(target=lambda: results.append(_transfer(a, b, 0.1)))
    t2 = threading.Thread(target=lambda: results.append(_transfer(a, b, 0.1)))
    t1.start(); t2.start(); t1.join(); t2.join()
    return all(results)  # True: no deadlock


def s3_break() -> bool:
    a, b = threading.Lock(), threading.Lock()
    results: list[bool] = []
    # Opposite order: t1 wants a->b, t2 wants b->a. Each grabs one and waits.
    t1 = threading.Thread(target=lambda: results.append(_transfer(a, b, 0.2)))
    t2 = threading.Thread(target=lambda: results.append(_transfer(b, a, 0.2)))
    t1.start(); t2.start(); t1.join(); t2.join()
    deadlocked = not all(results)  # at least one timed out waiting
    assert deadlocked, "expected a deadlock (one side times out)"
    return deadlocked


def s3_fix() -> bool:
    a, b = threading.Lock(), threading.Lock()
    results: list[bool] = []
    ordered = sorted((a, b), key=id)  # canonical order for everyone
    lo, hi = ordered[0], ordered[1]
    t1 = threading.Thread(target=lambda: results.append(_transfer(lo, hi, 0.2)))
    t2 = threading.Thread(target=lambda: results.append(_transfer(lo, hi, 0.2)))
    t1.start(); t2.start(); t1.join(); t2.join()
    return all(results)


S3_WHY = """
Thread 1 holds `a` and waits for `b`; thread 2 holds `b` and waits for `a`.
Neither can proceed — a cycle in the wait-for graph. The GIL is irrelevant: these
threads are blocked in lock acquisition, not running bytecode. Impose a global
order (always acquire the lower id() first) and no cycle can form.
"""


# ======================================================================================
# Scenario 4 — "It's one line, so it's atomic": append vs +=.
# ======================================================================================

def s4_build() -> tuple[int, int]:
    # list.append IS atomic in CPython: the whole call is one bytecode that does
    # not release the GIL mid-way. Total count is exact.
    sink: list[int] = []

    def worker() -> None:
        for _ in range(N):
            sink.append(1)

    _spawn(worker)
    return len(sink), THREADS * N  # equal


def s4_break(attempts: int = 5) -> tuple[int, int]:
    # `total += len(chunk)` is load-add-store: NOT atomic. Same line count, very
    # different safety.
    def run() -> int:
        total = 0

        def worker() -> None:
            nonlocal total
            for _ in range(N):
                current = total
                time.sleep(0)
                total = current + 1

        _spawn(worker)
        return total

    expected = THREADS * N
    for _ in range(attempts):
        got = run()
        if got < expected:
            return got, expected
    return got, expected


def s4_fix() -> tuple[int, int]:
    total = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal total
        for _ in range(N):
            with lock:
                current = total
                time.sleep(0)
                total = current + 1

    _spawn(worker)
    return total, THREADS * N


S4_WHY = """
"One source line" says nothing about atomicity. `sink.append(1)` is a single
bytecode whose C implementation does not yield the GIL, so it is safe.
`total = total + 1` is several bytecodes with switch points between them, so it
races. Do not reason from line count; reason from whether a value is read and
written back across instructions.
"""


SCENARIOS = [
    Scenario("Lost updates on a shared counter", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Check-then-act: cache initialised twice", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Deadlock from lock ordering", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("append is atomic, += is not", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

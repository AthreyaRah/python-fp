"""Profiling - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/37_profiling_and_dis/scenarios.py

These use operation COUNTS rather than wall-clock ratios, so the point is exact
and the scenarios are not flaky - but the lessons are about timing tools.
"""

from __future__ import annotations

import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

_BUILD_CALLS = 0


def _build_data() -> list[int]:
    global _BUILD_CALLS
    _BUILD_CALLS += 1
    return list(range(500))


# ======================================================================================
# Scenario 1 - timeit runs the STATEMENT number times, setup once.
# ======================================================================================

def s1_build() -> int:
    global _BUILD_CALLS
    _BUILD_CALLS = 0
    timeit.timeit(
        "sorted(data)",
        setup="data = _build_data()",     # runs ONCE
        number=50,
        globals=globals(),
    )
    return _BUILD_CALLS  # 1 - setup ran once


def s1_break() -> int:
    global _BUILD_CALLS
    _BUILD_CALLS = 0
    timeit.timeit("sorted(_build_data())", number=50, globals=globals())
    return _BUILD_CALLS  # 50 - the builder ran every iteration; you timed IT


def s1_fix() -> int:
    global _BUILD_CALLS
    _BUILD_CALLS = 0
    t = timeit.Timer("sorted(data)", setup="data = _build_data()", globals=globals())
    t.timeit(number=50)
    return _BUILD_CALLS  # 1


S1_WHY = """
`timeit` executes the `setup` string ONCE and the main statement `number` times.
Anything expensive in the statement - building the input, importing, opening a
file - is measured on every one of those iterations. Put fixtures in `setup=`
(string or callable) so you time only the code under test.
"""


# ======================================================================================
# Scenario 2 - timeit string can't see your local names.
# ======================================================================================

def s2_build() -> float:
    def my_func(n):
        return n * n

    return timeit.timeit("my_func(10)", number=100, globals=locals())  # pass the namespace


def s2_break() -> str:
    def my_func(n):
        return n * n

    try:
        timeit.timeit("my_func(10)", number=100)   # default globals: my_func unknown
    except NameError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s2_fix() -> float:
    def my_func(n):
        return n * n

    return timeit.timeit("my_func(10)", number=100, globals={"my_func": my_func})


S2_WHY = """
The statement and setup strings run in a namespace `timeit` controls, not your
function's locals - so `timeit("my_func()")` raises `NameError` unless `my_func`
is importable at module level. Pass `globals=locals()` (or `globals=globals()`),
or `setup="from mymodule import my_func"`.
"""


# ======================================================================================
# Scenario 3 - timeit disables the garbage collector by default.
# ======================================================================================

_GC_STATE: list[bool] = []


def s3_build() -> list[bool]:
    # If GC pressure is part of what you're measuring, turn it back on in setup.
    _GC_STATE.clear()
    timeit.timeit(
        "_GC_STATE.append(gc.isenabled())",
        setup="import gc; gc.enable()",
        number=3,
        globals=globals(),
    )
    return _GC_STATE  # [True, True, True] - matches production


def s3_break() -> list[bool]:
    _GC_STATE.clear()
    timeit.timeit(
        "_GC_STATE.append(gc.isenabled())",
        setup="import gc",
        number=3,
        globals=globals(),
    )
    return _GC_STATE  # [False, False, False] - GC is off during the measurement


def s3_fix() -> list[bool]:
    _GC_STATE.clear()
    timeit.timeit(
        "_GC_STATE.append(gc.isenabled())",
        setup="import gc; gc.enable()",
        number=3,
        globals=globals(),
    )
    return _GC_STATE


S3_WHY = """
`timeit` disables the cyclic garbage collector for the duration of the
measurement, so timings are more repeatable - but code that allocates a lot of
cyclic garbage will look faster than it does in production, where GC pauses
happen. If GC cost is part of what you care about, re-enable it in `setup`
(`"import gc; gc.enable()"`) or use `time.perf_counter` around the real workload.
"""


# ======================================================================================
# Scenario 4 - Micro-tweaks vs fixing the complexity (operation counts).
# ======================================================================================

class Counter:
    def __init__(self):
        self.ops = 0

    def tick(self, n=1):
        self.ops += n


def _pairs_slow(nums, target, c: Counter) -> bool:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            c.tick()                          # one comparison
            if nums[i] + nums[j] == target:
                return True
    return False


def _pairs_micro(nums, target, c: Counter) -> bool:
    for i, a in enumerate(nums):
        rest = nums[i + 1:]
        c.tick(len(rest))                     # `need in rest` still scans them all
        if (target - a) in rest:
            return True
    return False


def _pairs_fast(nums, target, c: Counter) -> bool:
    seen: set[int] = set()
    for a in nums:
        c.tick()                              # one hash lookup
        if target - a in seen:
            return True
        seen.add(a)
    return False


def _count(fn) -> int:
    nums = list(range(400))
    c = Counter()
    fn(nums, 999_999, c)                       # no pair sums to this -> full scan
    return c.ops


def s4_build() -> tuple[int, int]:
    return _count(_pairs_slow), _count(_pairs_fast)   # ~80k vs 400


def s4_break() -> bool:
    slow = _count(_pairs_slow)
    micro = _count(_pairs_micro)
    return micro > slow / 2          # micro-tweaks: same order of magnitude (O(n^2))


def s4_fix() -> bool:
    return _count(_pairs_fast) * 50 < _count(_pairs_slow)   # O(n) vs O(n^2)


S4_WHY = """
`_pairs_slow` and `_pairs_micro` both examine ~n^2/2 candidate pairs - slicing and
local-variable caching change the constant, not the growth. Replacing the nested
scan with one pass and a hash `set` is O(n): a few hundred operations instead of
tens of thousands. Profile to find the hot loop, fix its complexity first, and
only then micro-optimise what the profiler still flags.
"""


SCENARIOS = [
    Scenario("timeit runs the statement N times", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("timeit string can't see locals", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("timeit disables the GC", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Micro-tweaks vs the algorithm", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

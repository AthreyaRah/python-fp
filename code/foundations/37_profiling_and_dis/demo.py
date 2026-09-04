"""Profiling: timeit, cProfile, dis - the practice snippet.

Run it:  python code/foundations/37_profiling_and_dis/demo.py

Mental model:
- Don't guess about performance - MEASURE, then change the biggest thing.
- `timeit` : micro-benchmarks. Runs the statement many times, takes the best of
  several repeats, and disables the GC. Put setup in `setup=`, not the statement.
- `cProfile` : whole-program profiling. Function-level call counts and time.
  `tottime` = time spent IN the function itself; `cumtime` = including callees.
- `dis` : the bytecode a function compiles to - useful for understanding costs.
- The big wins are almost always ALGORITHMIC (O(n^2) -> O(n)), not micro-tweaks.
"""

from __future__ import annotations

import cProfile
import dis
import io
import pstats
import time
import timeit


def timeit_compare() -> None:
    setup = "data = list(range(10_000)); target = 9_999"
    list_t = min(timeit.repeat("target in data", setup=setup, number=1000, repeat=5))
    set_t = min(timeit.repeat("target in s", setup=setup + "; s = set(data)",
                              number=1000, repeat=5))
    print(f"'x in list' : {list_t * 1e6:8.1f} us / 1000 checks")
    print(f"'x in set'  : {set_t * 1e6:8.1f} us / 1000 checks  "
          f"({list_t / set_t:.0f}x faster)")


def time_a_block() -> None:
    t0 = time.perf_counter()
    _ = sum(i * i for i in range(200_000))
    print(f"block took {(time.perf_counter() - t0) * 1000:.1f} ms")


def profile_a_function() -> None:
    def has_dupes(seq):
        seen = []
        for x in seq:
            if x in seen:          # O(n) each -> O(n^2) loop: the hotspot
                return True
            seen.append(x)
        return False

    data = list(range(3000)) + [1]
    prof = cProfile.Profile()
    prof.enable()
    has_dupes(data)
    prof.disable()

    buf = io.StringIO()
    pstats.Stats(prof, stream=buf).sort_stats("tottime").print_stats(3)
    top = [ln for ln in buf.getvalue().splitlines() if "has_dupes" in ln]
    print("cProfile top (by tottime):", top[0].strip() if top else "(n/a)")


def disassemble() -> None:
    def add_one(x):
        return x + 1

    print("bytecode for `return x + 1`:")
    dis.dis(add_one)


def main() -> None:
    timeit_compare()
    print()
    time_a_block()
    print()
    profile_a_function()
    print()
    disassemble()


if __name__ == "__main__":
    main()

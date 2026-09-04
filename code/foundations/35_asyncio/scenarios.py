"""asyncio - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/35_asyncio/scenarios.py
"""

from __future__ import annotations

import asyncio
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402


async def _work(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return name


# ======================================================================================
# Scenario 1 - Calling a coroutine function without awaiting it.
# ======================================================================================

def s1_build() -> str:
    async def main():
        return await _work("done", 0.01)

    return asyncio.run(main())  # "done"


def s1_break() -> str:
    ran = []

    async def record():
        ran.append("ran")
        return "x"

    async def main():
        record()               # <- creates a coroutine, never awaited: does nothing
        await asyncio.sleep(0)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # "coroutine was never awaited"
        asyncio.run(main())
    return "never ran" if not ran else "ran"


def s1_fix() -> str:
    ran = []

    async def record():
        ran.append("ran")
        return "x"

    async def main():
        await record()         # awaited -> the body executes
        await asyncio.sleep(0)

    asyncio.run(main())
    return "ran" if ran else "never ran"


S1_WHY = """
`record()` on an `async def` returns a coroutine OBJECT - the body has not
executed. Without `await` (or scheduling it as a task) it is never driven by the
loop, so nothing happens and Python emits `RuntimeWarning: coroutine 'record' was
never awaited`. Always `await` a coroutine, or wrap it in `asyncio.create_task` /
pass it to `gather`.
"""


# ======================================================================================
# Scenario 2 - A blocking call inside a coroutine freezes the loop.
# ======================================================================================

def s2_build() -> float:
    async def task():
        await asyncio.sleep(0.1)         # async wait: yields to the loop
        return 1

    async def main():
        t0 = time.perf_counter()
        await asyncio.gather(*(task() for _ in range(5)))
        return time.perf_counter() - t0

    return asyncio.run(main())  # ~0.1s - all five overlap


def s2_break() -> bool:
    async def task():
        time.sleep(0.05)                 # SYNC sleep: blocks the whole event loop
        return 1

    async def main():
        t0 = time.perf_counter()
        await asyncio.gather(*(task() for _ in range(5)))
        return time.perf_counter() - t0

    total = asyncio.run(main())
    return total >= 0.20                 # 5 x 0.05s ran back to back, not concurrently


def s2_fix() -> bool:
    async def task():
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, time.sleep, 0.05)  # offload the blocking bit
        return 1

    async def main():
        t0 = time.perf_counter()
        await asyncio.gather(*(task() for _ in range(5)))
        return time.perf_counter() - t0

    return asyncio.run(main()) < 0.15


S2_WHY = """
The event loop is single-threaded. While a coroutine runs synchronous code it
never yields, so every other task is stuck. `time.sleep`, `requests.get`, a big
loop - all freeze the loop. Use the async equivalent (`asyncio.sleep`, an async
HTTP client), or push the blocking call to a thread/process pool with
`loop.run_in_executor`.
"""


# ======================================================================================
# Scenario 3 - Awaiting coroutines one at a time instead of concurrently.
# ======================================================================================

def s3_build() -> float:
    async def main():
        t0 = time.perf_counter()
        await asyncio.gather(_work("a", 0.1), _work("b", 0.1), _work("c", 0.1))
        return time.perf_counter() - t0

    return asyncio.run(main())  # ~0.1s


def s3_break() -> bool:
    async def main():
        t0 = time.perf_counter()
        for coro in (_work("a", 0.1), _work("b", 0.1), _work("c", 0.1)):
            await coro                  # each runs to completion before the next
        return time.perf_counter() - t0

    return asyncio.run(main()) >= 0.28


def s3_fix() -> bool:
    async def main():
        t0 = time.perf_counter()
        async with asyncio.TaskGroup() as tg:
            for name in ("a", "b", "c"):
                tg.create_task(_work(name, 0.1))
        return time.perf_counter() - t0

    return asyncio.run(main()) < 0.15


S3_WHY = """
`await coro` drives that coroutine to completion before the next statement -
sequential by definition. Concurrency needs the coroutines running as scheduled
TASKS at the same time: `asyncio.gather(*coros)` or an `asyncio.TaskGroup` with
`tg.create_task(...)`. Then the loop interleaves them at their `await` points.
"""


# ======================================================================================
# Scenario 4 - Fire-and-forget create_task loses results and errors.
# ======================================================================================

def s4_build() -> list[str]:
    async def main():
        async with asyncio.TaskGroup() as tg:      # awaits all, propagates errors
            tasks = [tg.create_task(_work(f"t{i}", 0.01)) for i in range(3)]
        return [t.result() for t in tasks]

    return asyncio.run(main())  # ['t0', 't1', 't2']


def s4_break() -> str:
    done = []

    async def slow():
        await asyncio.sleep(0.05)
        done.append("finished")

    async def main():
        asyncio.create_task(slow())    # scheduled, but main returns before it runs
        return "main returned"

    result = asyncio.run(main())
    # asyncio.run() stopped the loop; `slow` never got to finish.
    return f"{result}, slow done: {bool(done)}"


def s4_fix() -> str:
    done = []

    async def slow():
        await asyncio.sleep(0.05)
        done.append("finished")

    async def main():
        task = asyncio.create_task(slow())
        await task                     # keep a reference AND await it
        return "main returned"

    result = asyncio.run(main())
    return f"{result}, slow done: {bool(done)}"


S4_WHY = """
`asyncio.run()` runs the loop only until the coroutine you gave it returns, then
cancels whatever is left. A bare `create_task(...)` that you neither await nor
track is cancelled at shutdown - its result and any exception vanish (the loop
keeps only a weak reference, so it can even be GC'd early). Await your tasks, keep
them in a list, or - best - use `asyncio.TaskGroup`, which awaits every child and
re-raises failures.
"""


SCENARIOS = [
    Scenario("Coroutine never awaited", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Blocking call freezes the loop", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Awaiting one at a time", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Fire-and-forget task", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

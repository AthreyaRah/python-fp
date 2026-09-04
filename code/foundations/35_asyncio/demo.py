"""asyncio: the event loop & coroutines - the practice snippet.

Run it:  python code/foundations/35_asyncio/demo.py

Mental model:
- `async def` makes a COROUTINE FUNCTION. Calling it returns a coroutine object
  and runs NOTHING yet.
- `await x` suspends the current coroutine and hands control back to the EVENT
  LOOP until `x` is ready. The loop runs ONE coroutine at a time, switching only
  at `await` points - it is single-threaded concurrency.
- `asyncio.run(main())` starts the loop, runs `main` to completion, stops it.
- Concurrency comes from scheduling multiple coroutines as TASKS
  (`asyncio.gather`, `asyncio.TaskGroup`, `create_task`) - awaiting them one by
  one is just sequential code.
- A BLOCKING call (`time.sleep`, `requests.get`, heavy CPU) freezes the whole
  loop. Use async equivalents or `loop.run_in_executor`.
"""

from __future__ import annotations

import asyncio
import time


async def fetch(name: str, seconds: float) -> str:
    await asyncio.sleep(seconds)          # yields to the loop; other tasks run
    return f"{name} ({seconds}s)"


async def sequential() -> float:
    t0 = time.perf_counter()
    await fetch("a", 0.1)
    await fetch("b", 0.1)
    await fetch("c", 0.1)
    return time.perf_counter() - t0       # ~0.3s


async def concurrent_gather() -> float:
    t0 = time.perf_counter()
    await asyncio.gather(fetch("a", 0.1), fetch("b", 0.1), fetch("c", 0.1))
    return time.perf_counter() - t0       # ~0.1s


async def task_group() -> list[str]:
    results: list[str] = []
    async with asyncio.TaskGroup() as tg:     # 3.11+; cancels siblings on error
        tasks = [tg.create_task(fetch(f"t{i}", 0.05)) for i in range(4)]
    return [t.result() for t in tasks]


def blocking_work(n: int) -> int:
    total = 0
    for i in range(1_000_000):
        total += i % n
    return total


async def offload_blocking() -> int:
    loop = asyncio.get_running_loop()
    # Run the CPU/blocking function in a thread so the loop stays responsive.
    return await loop.run_in_executor(None, blocking_work, 7)


async def main() -> None:
    print(f"sequential awaits : {await sequential():.2f}s")
    print(f"asyncio.gather    : {await concurrent_gather():.2f}s")
    print("TaskGroup results :", await task_group())
    print("run_in_executor   :", await offload_blocking())


if __name__ == "__main__":
    asyncio.run(main())

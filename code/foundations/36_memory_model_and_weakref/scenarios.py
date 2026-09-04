"""The memory model & weakref - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/36_memory_model_and_weakref/scenarios.py
"""

from __future__ import annotations

import gc
import sys
import weakref
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402


class Parent:
    def __init__(self):
        self.children: list = []


class StrongChild:
    def __init__(self, parent):
        self.parent = parent          # strong back-reference -> cycle with Parent


class WeakChild:
    def __init__(self, parent):
        self._parent = weakref.ref(parent)   # weak back-reference -> no cycle

    @property
    def parent(self):
        return self._parent()


# ======================================================================================
# Scenario 1 - A reference cycle keeps objects alive until gc runs.
# ======================================================================================

def _make_family(child_cls) -> weakref.ref:
    p = Parent()
    c = child_cls(p)
    p.children.append(c)
    marker = weakref.ref(p)           # observe whether p gets freed
    del p, c
    return marker


def s1_build() -> bool:
    gc.collect()
    marker = _make_family(WeakChild)  # child -> parent is weak: no cycle
    return marker() is None           # freed immediately by refcounting


def s1_break() -> tuple[bool, bool]:
    gc.disable()                      # so only refcounting is in play
    try:
        marker = _make_family(StrongChild)
        alive_before_gc = marker() is not None   # still alive: p <-> c cycle
    finally:
        gc.enable()
    freed = gc.collect() and marker() is None    # the cyclic collector frees it
    return alive_before_gc, marker() is None


def s1_fix() -> bool:
    gc.collect()
    marker = _make_family(WeakChild)
    return marker() is None


S1_WHY = """
`Parent` holds `children`, each child holds `parent` - a cycle. Reference
counting alone can never bring either count to zero, so with the cyclic collector
disabled the objects leak. `gc.collect()` walks the heap, finds the unreachable
cycle, and frees it - but that runs periodically, not immediately. Break the cycle
at design time: make the back-reference a `weakref`, so only the "downward" link
is strong.
"""


# ======================================================================================
# Scenario 2 - A weakref to an object with no strong reference.
# ======================================================================================

def s2_build() -> str | None:
    obj = Parent()                   # a strong reference keeps it alive
    ref = weakref.ref(obj)
    return type(ref()).__name__      # "Parent"


def s2_break() -> str | None:
    ref = weakref.ref(Parent())      # the Parent() has no other reference...
    gc.collect()
    return ref()                     # ...so it's already gone: None


def s2_fix() -> str:
    obj = Parent()
    ref = weakref.ref(obj)
    return type(ref()).__name__


S2_WHY = """
`weakref.ref(Parent())` never binds the new `Parent` to anything, so its refcount
is zero the moment the expression finishes and it is freed. The weakref then
resolves to `None`. A weakref is only useful alongside a strong reference held
somewhere else.
"""


# ======================================================================================
# Scenario 3 - A plain-dict cache keyed by object keeps everything alive.
# ======================================================================================

def s3_build() -> int:
    cache: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
    for _ in range(100):
        obj = Parent()
        cache[obj] = "metadata"       # entry disappears when obj is collected
    gc.collect()
    return len(cache)  # ~0 - nothing else holds those Parents


def s3_break() -> int:
    cache: dict = {}
    for _ in range(100):
        obj = Parent()
        cache[obj] = "metadata"       # the dict is a STRONG reference
    gc.collect()
    return len(cache)  # 100 - every Parent is pinned alive by the cache forever


def s3_fix() -> int:
    cache: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()
    for _ in range(100):
        obj = Parent()
        cache[obj] = "metadata"
    gc.collect()
    return len(cache)


S3_WHY = """
A dict keyed by objects holds a strong reference to every key, so those objects
can never be freed while the cache lives - a slow leak that grows with traffic.
`weakref.WeakKeyDictionary` (or `WeakValueDictionary`) holds the entry only as
long as something else holds the object; when the last strong reference goes, the
cache entry disappears automatically.
"""


# ======================================================================================
# Scenario 4 - Relying on __del__ for cleanup.
# ======================================================================================

_FLUSHED: list[str] = []


class BufferDel:
    def __init__(self, name):
        self.name = name
        self.buf = []

    def write(self, x):
        self.buf.append(x)

    def __del__(self):
        _FLUSHED.append(f"{self.name}:{len(self.buf)}")


def s4_build() -> list[str]:
    _FLUSHED.clear()

    class Buffer:
        def __init__(self, name):
            self.name, self.buf = name, []

        def write(self, x):
            self.buf.append(x)

        def close(self):
            _FLUSHED.append(f"{self.name}:{len(self.buf)}")

    b = Buffer("explicit")
    b.write("a"); b.write("b")
    b.close()                        # deterministic
    return list(_FLUSHED)  # ['explicit:2']


def s4_break() -> list[str]:
    _FLUSHED.clear()
    b = BufferDel("via_del")
    b.write("a"); b.write("b")
    b.other = b                      # put it in a cycle -> __del__ deferred to gc
    del b
    # At this point (before an explicit collect) nothing has been flushed.
    return list(_FLUSHED)  # []


def s4_fix() -> list[str]:
    _FLUSHED.clear()

    class Buffer:
        def __init__(self, name):
            self.name, self.buf = name, []

        def write(self, x):
            self.buf.append(x)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            _FLUSHED.append(f"{self.name}:{len(self.buf)}")

    with Buffer("ctx") as b:
        b.write("a"); b.write("b")
    return list(_FLUSHED)  # ['ctx:2']


S4_WHY = """
`__del__` runs when the object is collected, not when the variable goes out of
scope. If the object is in a reference cycle, is alive at interpreter shutdown, or
the process is killed, `__del__` may run late or never - and exceptions in it are
ignored. Do cleanup deterministically with a context manager (`with`) or an
explicit `close()`; treat `__del__` only as a last-resort safety net.
"""


SCENARIOS = [
    Scenario("Reference cycle leaks without gc", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("weakref to an unreferenced object", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Object-keyed dict cache leaks", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Relying on __del__ for cleanup", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

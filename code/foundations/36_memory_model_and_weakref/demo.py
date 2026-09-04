"""The memory model & weakref - the practice snippet.

Run it:  python code/foundations/36_memory_model_and_weakref/demo.py

Mental model:
- CPython frees an object the instant its REFERENCE COUNT hits zero. Binding a
  name, appending to a list, passing as an argument - each adds one.
- Reference CYCLES (a -> b -> a) never reach zero on their own; a separate cyclic
  GARBAGE COLLECTOR (`gc` module) finds and frees them, but only when it runs.
- A `weakref` points at an object WITHOUT incrementing its count - so it does not
  keep the object alive. Used for caches, back-references, observers.
- `__del__` runs when the object is collected, which is NOT the same as going out
  of scope. Don't rely on it for cleanup - use a context manager.
"""

from __future__ import annotations

import gc
import sys
import weakref


def reference_counting() -> None:
    obj = object()
    base = sys.getrefcount(obj)
    holder = [obj, obj]              # noqa: F841 - two more references
    print("adding 2 references raised the count by:", sys.getrefcount(obj) - base)


class Node:
    def __init__(self, name):
        self.name = name
        self.other = None

    def __repr__(self):
        return f"Node({self.name})"


def reference_cycle() -> None:
    gc.collect()
    a, b = Node("a"), Node("b")
    a.other, b.other = b, a           # a <-> b cycle
    watch = weakref.ref(a)
    gc.disable()
    del a, b                          # counts drop, but not to zero (they hold each other)
    print("with gc off, cycle still alive after del:", watch() is not None)
    gc.enable()
    gc.collect()                      # the cyclic collector reclaims it
    print("after gc.collect(), alive:", watch() is not None)


def weak_references() -> None:
    node = Node("live")
    ref = weakref.ref(node)
    print("while alive, ref() ->", ref())
    del node
    print("after del,   ref() ->", ref(), "(the weakref does not keep it alive)")


def weak_value_cache() -> None:
    cache: weakref.WeakValueDictionary[str, Node] = weakref.WeakValueDictionary()
    keep = Node("cached")
    cache["k"] = keep
    print("in cache while referenced:", "k" in cache)
    del keep
    gc.collect()
    print("gone once nothing else refers to it:", "k" in cache)


def main() -> None:
    reference_counting()
    print()
    reference_cycle()
    print()
    weak_references()
    print()
    weak_value_cache()


if __name__ == "__main__":
    main()

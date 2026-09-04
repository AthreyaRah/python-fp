"""copy: shallow vs deep - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/41_copy_shallow_vs_deep/scenarios.py
"""

from __future__ import annotations

import copy
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Shallow copy of a nested structure.
# ======================================================================================

def _template() -> dict:
    return {"name": "base", "roles": ["viewer"], "limits": {"rate": 10}}


def s1_build() -> tuple[list, dict]:
    base = _template()
    derived = copy.deepcopy(base)          # fully independent
    derived["roles"].append("editor")
    derived["limits"]["rate"] = 100
    return base["roles"], base["limits"]   # (['viewer'], {'rate': 10}) - untouched


def s1_break() -> tuple[list, dict]:
    base = _template()
    derived = base.copy()                  # shallow: 'roles' and 'limits' are shared
    derived["roles"].append("editor")
    derived["limits"]["rate"] = 100
    # `base` mutated through the "copy".
    assert base["roles"] == ["viewer", "editor"] and base["limits"]["rate"] == 100
    return base["roles"], base["limits"]


def s1_fix() -> tuple[list, dict]:
    base = _template()
    derived = copy.deepcopy(base)
    derived["roles"].append("editor")
    derived["limits"]["rate"] = 100
    return base["roles"], base["limits"]


S1_WHY = """
`dict.copy()` / `copy.copy()` / `{**d}` / `list(x)` make a new OUTER container
whose entries are the SAME nested objects. Mutating `derived["roles"]` mutates the
one list that `base["roles"]` also points at. Use `copy.deepcopy` when the nested
objects must be independent - or, better, don't share mutable defaults / build
each structure fresh.
"""


# ======================================================================================
# Scenario 2 - deepcopy of an object holding an un-copyable resource.
# ======================================================================================

class ReportWriterNaive:
    def __init__(self, sink: io.StringIO):
        self.sink = sink                  # a live stream
        self.rows: list[str] = []


class ReportWriterSafe:
    def __init__(self, sink: io.StringIO):
        self.sink = sink
        self.rows: list[str] = []

    def __deepcopy__(self, memo):
        clone = ReportWriterSafe(self.sink)          # SHARE the sink
        clone.rows = copy.deepcopy(self.rows, memo)  # deep-copy the data
        return clone


def s2_build() -> bool:
    w = ReportWriterSafe(io.StringIO())
    w.rows.append("a")
    c = copy.deepcopy(w)
    c.rows.append("b")
    return w.rows == ["a"] and c.sink is w.sink   # data independent, sink shared


def s2_break() -> str:
    w = ReportWriterNaive(open(__file__, encoding="utf-8"))
    try:
        copy.deepcopy(w)          # deepcopy recurses into the file object
    except TypeError as exc:
        w.sink.close()
        return f"{type(exc).__name__}: {exc}"
    w.sink.close()
    return "no error (unexpected)"


def s2_fix() -> bool:
    w = ReportWriterSafe(io.StringIO())
    w.rows.extend(["x", "y"])
    c = copy.deepcopy(w)
    return c.rows == ["x", "y"] and c.sink is w.sink


S2_WHY = """
`deepcopy` recurses into every attribute, including things that cannot be
meaningfully copied - open files, sockets, locks, DB connections, thread
objects - and raises (e.g. `TypeError: cannot pickle '_io.TextIOWrapper'`).
Define `__deepcopy__(self, memo)` to copy the data you own and SHARE (or re-open)
the external resource; or keep such resources out of the objects you copy.
"""


# ======================================================================================
# Scenario 3 - deepcopy's memo is per-call: separate calls don't stay linked.
# ======================================================================================

def s3_build() -> bool:
    shared = {"v": 1}
    graph = {"a": {"cfg": shared}, "b": {"cfg": shared}}
    clone = copy.deepcopy(graph)                    # one call over the whole graph
    clone["a"]["cfg"]["v"] = 99
    return clone["b"]["cfg"]["v"] == 99             # still linked inside the clone


def s3_break() -> bool:
    shared = {"v": 1}
    node_a = {"cfg": shared}
    node_b = {"cfg": shared}
    copy_a = copy.deepcopy(node_a)                  # separate call
    copy_b = copy.deepcopy(node_b)                  # separate call -> separate cfg
    copy_a["cfg"]["v"] = 99
    return copy_b["cfg"]["v"] == 1                  # NOT linked: two independent copies


def s3_fix() -> bool:
    shared = {"v": 1}
    both = {"a": {"cfg": shared}, "b": {"cfg": shared}}
    clone = copy.deepcopy(both)                     # copy the whole thing at once
    clone["a"]["cfg"]["v"] = 99
    return clone["b"]["cfg"]["v"] == 99


S3_WHY = """
Within a SINGLE `deepcopy` call, a `memo` dict records "I've already copied object
X -> here is its copy", so two references to one object inside the structure end
up pointing at one copy (aliasing preserved). Two SEPARATE `deepcopy` calls each
start with an empty memo, so an object referenced from both gets copied twice and
the copies are unrelated. Deep-copy the whole graph in one call.
"""


# ======================================================================================
# Scenario 4 - copy.copy on a custom object shares its mutable attributes.
# ======================================================================================

class Cart:
    def __init__(self):
        self.items: list[str] = []
        self.totals: dict[str, int] = {}


def s4_build() -> tuple[list, list]:
    a = Cart()
    a.items.append("apple")
    b = copy.deepcopy(a)                            # independent attributes
    b.items.append("banana")
    return a.items, b.items                         # (['apple'], ['apple', 'banana'])


def s4_break() -> tuple[list, list, bool]:
    a = Cart()
    a.items.append("apple")
    b = copy.copy(a)                                # shallow: shares a.items
    b.items.append("banana")
    assert a.items == ["apple", "banana"]
    return a.items, b.items, a.items is b.items


def s4_fix() -> tuple[list, list]:
    a = Cart()
    a.items.append("apple")
    b = copy.deepcopy(a)
    b.items.append("banana")
    return a.items, b.items


S4_WHY = """
`copy.copy(obj)` for a normal object creates a new instance and copies the
attribute dict SHALLOWLY - so `b.items` is the very same list as `a.items`, and it
does NOT call `__init__`. If the object holds mutable attributes you want
independent, use `copy.deepcopy`, or implement `__copy__` to duplicate them.
"""


SCENARIOS = [
    Scenario("Shallow copy of a nested dict", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("deepcopy of an un-copyable resource", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("deepcopy memo is per-call", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("copy.copy shares object attributes", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

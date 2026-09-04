"""The collections module - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/08_the_collections_module/scenarios.py
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict, deque, namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - Reading a defaultdict inserts keys.
# ======================================================================================

def s1_build() -> int:
    seen = defaultdict(int)
    seen["a"] += 1
    # A pure membership question: use `in`, which does NOT insert.
    present = "b" in seen
    assert present is False
    return len(seen)  # 1


def s1_break() -> int:
    counts = defaultdict(int)
    counts["a"] += 1
    users = ["a", "b", "c"]
    active = [u for u in users if counts[u] > 0]  # counts[u] auto-creates u
    assert active == ["a"]
    return len(counts)  # 3 - "b" and "c" were inserted just by looking


def s1_fix() -> int:
    counts = defaultdict(int)
    counts["a"] += 1
    users = ["a", "b", "c"]
    active = [u for u in users if counts.get(u, 0) > 0]  # .get never inserts
    assert active == ["a"]
    return len(counts)  # 1


S1_WHY = """
`defaultdict.__missing__` runs the factory AND stores the result whenever you
index a missing key with `d[k]`. So `if counts[u] > 0` has a side effect: it
creates `u` with value 0. Use `k in d` or `d.get(k, default)` for reads that
should not mutate the dict.
"""


# ======================================================================================
# Scenario 2 - Counter.subtract leaves zero and negative entries.
# ======================================================================================

def s2_build() -> "Counter":
    have = Counter(apple=5, pear=2, plum=1)
    used = Counter(apple=5, pear=1)
    return have - used  # operator form: keeps only positive counts -> {'pear': 1, 'plum': 1}


def s2_break() -> list:
    have = Counter(apple=5, pear=2, plum=1)
    used = Counter(apple=5, pear=1, plum=3)
    have.subtract(used)  # in place; keeps zero and goes negative
    # 'apple' is 0, 'plum' is -2 - both still present.
    assert have["apple"] == 0 and have["plum"] == -2
    return sorted(have.items())


def s2_fix() -> list:
    have = Counter(apple=5, pear=2, plum=1)
    used = Counter(apple=5, pear=1, plum=3)
    remaining = have - used            # operator drops non-positive
    return sorted(remaining.items())   # [('pear', 1)]


S2_WHY = """
`Counter.subtract` mutates in place and is happy to store 0 and negative counts -
useful for inventory deltas, surprising for "what's left". The `-` operator
returns a NEW Counter and, by design, keeps only counts > 0 (as do `+`, `&`,
`|`). Pick the form that matches your intent.
"""


# ======================================================================================
# Scenario 3 - deque(maxlen) silently drops the oldest item.
# ======================================================================================

def s3_build() -> list[int]:
    recent: deque[int] = deque(maxlen=3)   # deliberate: last 3 events only
    for event in range(6):
        recent.append(event)
    return list(recent)  # [3, 4, 5]


def s3_break() -> int:
    audit_log: deque[str] = deque(maxlen=100)  # "should be plenty"
    for i in range(250):
        audit_log.append(f"event-{i}")
    # We wanted every event for the audit; 150 were silently discarded.
    assert "event-0" not in audit_log
    return len(audit_log)  # 100, not 250


def s3_fix() -> int:
    audit_log: deque[str] = deque()  # no maxlen -> nothing dropped
    for i in range(250):
        audit_log.append(f"event-{i}")
    return len(audit_log)  # 250


S3_WHY = """
A `deque` with `maxlen` set discards from the opposite end on every append once
it is full - that is the whole point for ring buffers / "last N". But if you
picked a maxlen as a guess at capacity, real overflow is silent data loss. Use
maxlen only when dropping old items is the intended behaviour.
"""


# ======================================================================================
# Scenario 4 - Trying to mutate a namedtuple.
# ======================================================================================

Config = namedtuple("Config", ["host", "port"])


def s4_build() -> "Config":
    c = Config("localhost", 8000)
    return c._replace(port=9000)  # returns a NEW Config


def s4_break() -> str:
    c = Config("localhost", 8000)
    try:
        c.port = 9000  # namedtuple is a tuple: immutable
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> "Config":
    c = Config("localhost", 8000)
    c = c._replace(port=9000)
    return c


S4_WHY = """
`namedtuple` builds a subclass of `tuple`, so instances are immutable: there is
no `__setattr__` that writes to a slot, hence `AttributeError`. Produce a
modified copy with `_replace(**changes)`. If you need real mutability, use a
plain class or `@dataclass` (non-frozen), or `types.SimpleNamespace`.
"""


SCENARIOS = [
    Scenario("Reading a defaultdict inserts keys", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Counter.subtract keeps zeros/negatives", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("deque(maxlen) drops silently", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Mutating a namedtuple", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""Serialization - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/29_serialization_stdlib/scenarios.py
"""

from __future__ import annotations

import csv
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.dummydata import write_people_csv  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

OUT = generated_dir("serialization_scenarios")


# ======================================================================================
# Scenario 1 - json can't serialize a datetime.
# ======================================================================================

def s1_build() -> str:
    event = {"kind": "login", "at": datetime(2024, 1, 1, tzinfo=timezone.utc)}
    return json.dumps(event, default=str)   # default handles unknown types


def s1_break() -> str:
    event = {"kind": "login", "at": datetime(2024, 1, 1, tzinfo=timezone.utc)}
    try:
        return json.dumps(event)
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> dict:
    event = {"kind": "login", "at": datetime(2024, 1, 1, tzinfo=timezone.utc)}
    serializable = {**event, "at": event["at"].isoformat()}   # convert explicitly
    return json.loads(json.dumps(serializable))


S1_WHY = """
`json` maps only dict/list/str/int/float/bool/None. A `datetime` (or `set`,
`Decimal`, `bytes`, dataclass) has no JSON representation, so `json.dumps` raises
`TypeError: Object of type datetime is not JSON serializable`. Provide a
`default=` callback, or convert to a JSON-friendly form yourself
(`dt.isoformat()`, `list(myset)`, `str(dec)`) before dumping.
"""


# ======================================================================================
# Scenario 2 - JSON object keys are always strings.
# ======================================================================================

def s2_build() -> list:
    data = {2020: 15, 2021: 22, 2022: 30}
    # Keep it round-trippable: store as a list of [key, value] pairs.
    dumped = json.dumps(list(data.items()))
    return [tuple(pair) for pair in json.loads(dumped)]  # [(2020, 15), ...]


def s2_break() -> dict:
    data = {2020: 15, 2021: 22}
    back = json.loads(json.dumps(data))
    # Keys came back as strings; a lookup by int now misses.
    assert list(back) == ["2020", "2021"]
    return back  # {'2020': 15, '2021': 22}


def s2_fix() -> dict:
    data = {2020: 15, 2021: 22}
    back = json.loads(json.dumps(data))
    return {int(k): v for k, v in back.items()}   # coerce keys on the way in


S2_WHY = """
In JSON, an object's keys are always strings - the format has no other kind. So
`json.dumps({2020: 15})` writes `{"2020": 15}` and `json.loads` gives it back with
a string key. Convert keys back to `int` after loading, or avoid the issue by
serializing a list of pairs.
"""


# ======================================================================================
# Scenario 3 - pickle executes code from the data.
# ======================================================================================

_EXECUTED: list[str] = []


def _side_effect(marker: str) -> str:
    _EXECUTED.append(marker)          # stands in for os.system(...) etc.
    return marker


class Exploit:
    """A benign stand-in: its __reduce__ makes unpickling CALL a function."""

    def __reduce__(self):
        return (_side_effect, ("payload ran during unpickling",))


def s3_build() -> list:
    # Untrusted input? Use a data-only format. json can't call functions.
    hostile = json.dumps({"cmd": "rm -rf /"})     # just text, does nothing
    _EXECUTED.clear()
    json.loads(hostile)
    return list(_EXECUTED)  # [] - json never executes anything


def s3_break() -> list:
    _EXECUTED.clear()
    blob = pickle.dumps(Exploit())               # a "file" from an untrusted source
    pickle.loads(blob)                            # <- runs _side_effect during load
    assert _EXECUTED == ["payload ran during unpickling"]
    return list(_EXECUTED)


def s3_fix() -> list:
    # Never unpickle data you don't fully control. For internal caches where you
    # DO control both ends, pickle is fine; otherwise json / msgpack / protobuf.
    _EXECUTED.clear()
    safe = json.loads(json.dumps({"retries": 3, "name": "cache"}))
    return [safe["name"]] if not _EXECUTED else _EXECUTED


S3_WHY = """
A pickle is a little stack program. `__reduce__` tells the unpickler "to rebuild
me, call THIS callable with THESE args" - and the unpickler obeys, for any
callable named in the byte stream. So `pickle.loads` of attacker-controlled bytes
is remote code execution. Treat pickle as trusted-only (your own caches, IPC
between your own processes) and use a data-only format for anything external.
"""


# ======================================================================================
# Scenario 4 - csv values are all strings.
# ======================================================================================

def _people_csv() -> Path:
    path = OUT / "people.csv"
    write_people_csv(path, n=6, seed=9)
    return path


def s4_build() -> int:
    with _people_csv().open(newline="", encoding="utf-8") as fh:
        return sum(int(row["salary"]) for row in csv.DictReader(fh))


def s4_break() -> str:
    with _people_csv().open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    oldest = max(row["age"] for row in rows)   # STRING comparison: "9" > "63"
    assert isinstance(oldest, str)
    return oldest


def s4_fix() -> int:
    with _people_csv().open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return max(int(row["age"]) for row in rows)   # convert, then compare


S4_WHY = """
`csv.DictReader` does no type inference - CSV is untyped text - so every value it
hands you is a `str`. `max(...)` over strings compares lexicographically ("9" >
"63"), and `"12" + "5"` concatenates. Convert at the boundary: `int(row["age"])`,
`float(...)`, `datetime.fromisoformat(...)`, or move to pandas/Polars which infer
dtypes.
"""


SCENARIOS = [
    Scenario("json can't serialize a datetime", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("JSON keys are strings", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("pickle executes code on load", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("csv values are all strings", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

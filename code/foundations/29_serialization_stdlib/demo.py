"""Serialization: json, pickle, csv, struct - the practice snippet.

Run it:  python code/foundations/29_serialization_stdlib/demo.py

Serialization turns objects into bytes/text you can store or send; deserialization
reverses it. The stdlib gives you four, with very different trade-offs:
- json   : text, cross-language, only dict/list/str/number/bool/None. Object keys
           are always strings. No tuples, sets, datetimes.
- pickle : binary, Python-only, arbitrary objects - and UNSAFE: unpickling
           untrusted data can execute arbitrary code.
- csv    : tabular text. Every value read back is a `str` (no type inference).
- struct : fixed binary layouts described by a format string. For protocols and
           file headers.
"""

from __future__ import annotations

import csv
import json
import pickle
import struct
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.dummydata import write_people_csv  # noqa: E402


def json_basics() -> None:
    obj = {"name": "Ada", "tags": ["a", "b"], "score": 9.5, "active": True}
    text = json.dumps(obj, indent=2, sort_keys=True)
    print("json.dumps:\n" + text)
    print("round trip equal:", json.loads(text) == obj)


def json_type_limits() -> None:
    # int keys and tuples do not survive as-is.
    weird = {1: ("x", "y")}
    back = json.loads(json.dumps(weird))
    print("dict {1: ('x','y')} ->", back, " (key is now str, tuple is now list)")

    # datetimes need help.
    payload = {"created": date(2024, 5, 1)}
    print("with default=str:", json.dumps(payload, default=str))


class Config:  # module level: pickle needs to find the class by qualified name
    def __init__(self, retries):
        self.retries = retries

    def __repr__(self):
        return f"Config(retries={self.retries})"


def pickle_roundtrip() -> None:
    blob = pickle.dumps(Config(3))
    print("pickle bytes length:", len(blob), "| restored:", pickle.loads(blob))


def csv_is_all_strings() -> None:
    path = generated_dir("serialization_demo") / "people.csv"
    write_people_csv(path, n=4, seed=5)
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    first = rows[0]
    print("csv row:", first)
    print("types  :", {k: type(v).__name__ for k, v in first.items()})
    total = sum(int(r["salary"]) for r in rows)   # must convert first
    print("total salary (after int()):", f"{total:,}")


def struct_fixed_layout() -> None:
    # A 3-field record: unsigned int, float, 4-byte tag. '>' = big-endian.
    packed = struct.pack(">I f 4s", 42, 3.5, b"TEMP")
    print("packed bytes:", packed, "| size:", struct.calcsize(">I f 4s"))
    print("unpacked:", struct.unpack(">I f 4s", packed))


def main() -> None:
    json_basics()
    print()
    json_type_limits()
    print()
    pickle_roundtrip()
    print()
    csv_is_all_strings()
    print()
    struct_fixed_layout()


if __name__ == "__main__":
    main()

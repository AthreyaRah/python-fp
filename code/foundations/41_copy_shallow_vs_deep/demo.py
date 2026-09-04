"""copy: shallow vs deep - the practice snippet.

Run it:  python code/foundations/41_copy_shallow_vs_deep/demo.py

Mental model (building on "names & references"):
- `b = a`                : no copy. Two names, one object.
- SHALLOW copy           : a new OUTER object; its elements are the SAME objects
  (`copy.copy(a)`, `a.copy()`, `a[:]`, `list(a)`, `dict(a)`, `{**a}`).
- DEEP copy              : `copy.deepcopy(a)` recursively copies every object it
  reaches. Independent all the way down. Handles cycles via a `memo` dict, and
  preserves sharing that exists WITHIN the copied structure.
- For an immutable with immutable contents, `copy.copy` may return the original.
"""

from __future__ import annotations

import copy


def alias_vs_shallow_vs_deep() -> None:
    original = {"name": "cfg", "servers": ["a", "b"]}

    alias = original
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)

    original["servers"].append("c")     # mutate the nested list

    print("alias  :", alias["servers"])    # ['a', 'b', 'c'] - same dict
    print("shallow:", shallow["servers"])  # ['a', 'b', 'c'] - shares the list
    print("deep   :", deep["servers"])     # ['a', 'b']      - fully independent


def deepcopy_handles_cycles() -> None:
    a: dict = {}
    a["self"] = a                        # a references itself
    b = copy.deepcopy(a)                 # would infinite-loop without the memo
    print("cycle deep-copied:", b["self"] is b, "| b is not a:", b is not a)


def deepcopy_preserves_internal_sharing() -> None:
    shared = ["S"]
    tree = {"left": shared, "right": shared}
    clone = copy.deepcopy(tree)
    print("internal sharing kept:", clone["left"] is clone["right"],
          "| but separate from the original:", clone["left"] is not shared)


def main() -> None:
    alias_vs_shallow_vs_deep()
    print()
    deepcopy_handles_cycles()
    print()
    deepcopy_preserves_internal_sharing()


if __name__ == "__main__":
    main()

"""Mutability & the mutable-default trap — the practice snippet.

Run it:  python code/foundations/03_mutability_and_the_default_arg_trap/demo.py

Mental model: every object is either MUTABLE (its state can change after
creation: list, dict, set, bytearray, most custom objects) or IMMUTABLE (it
cannot: int, float, str, bytes, tuple, frozenset, bool). "Changing" an immutable
value always means building a new object and rebinding a name to it — the old
object is untouched. This one property explains hashability, dict keys, the
mutable-default bug, and shared-state bugs.
"""

from __future__ import annotations


def immutable_rebinds_mutable_mutates() -> None:
    s = "abc"
    before = id(s)
    s += "d"
    print(f"str  += : same object? {id(s) == before}  (immutable -> new object)")

    lst = [1, 2, 3]
    before = id(lst)
    lst += [4]
    print(f"list += : same object? {id(lst) == before}  (mutable -> changed in place)")


def aliases_see_mutation_not_rebinding() -> None:
    a = [1, 2]
    b = a
    a.append(3)
    print("after a.append(3):   b ==", b, "(alias sees the mutation)")
    a = a + [4]
    print("after a = a + [4]:   b ==", b, "(rebinding a leaves b on the old object)")


def immutable_container_mutable_contents() -> None:
    pair = ([1, 2], "tag")  # a tuple: you cannot swap its slots...
    pair[0].append(3)        # ...but slot 0 points at a list, which you can mutate
    print("tuple with a list inside:", pair)
    try:
        pair[0] = [9]
    except TypeError as exc:
        print("  pair[0] = [9] ->", type(exc).__name__, "-", exc)


def hashability_follows_immutability() -> None:
    ok = {(1, 2): "point"}          # tuple key: fine
    print("dict with tuple key:", ok)
    try:
        {[1, 2]: "point"}           # list key: not allowed
    except TypeError as exc:
        print("  list as dict key ->", type(exc).__name__, "-", exc)


def the_mutable_default_trap() -> None:
    def bad(item, bucket=[]):       # one list, created at def time, shared
        bucket.append(item)
        return bucket

    # Call separately: passing all three to one print() would evaluate them
    # before printing, so every name would show the final list.
    print("bad('a'):", bad("a"))
    print("bad('b'):", bad("b"))
    print("bad('c'):", bad("c"))
    print("  bad.__defaults__ is now:", bad.__defaults__)

    def good(item, bucket=None):
        bucket = [] if bucket is None else bucket
        bucket.append(item)
        return bucket

    print("good('a'):", good("a"))
    print("good('b'):", good("b"))


def main() -> None:
    immutable_rebinds_mutable_mutates()
    print()
    aliases_see_mutation_not_rebinding()
    print()
    immutable_container_mutable_contents()
    print()
    hashability_follows_immutability()
    print()
    the_mutable_default_trap()


if __name__ == "__main__":
    main()

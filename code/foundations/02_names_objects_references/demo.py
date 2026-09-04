"""Names, objects & references — the practice snippet.

Run it:  python code/foundations/02_names_objects_references/demo.py

Mental model: a Python object lives somewhere in memory. A *name* is a label
stuck onto it. Assignment (`=`) moves a label; it never copies the object.
Everything surprising about references follows from that one sentence.
"""

from __future__ import annotations


def names_are_labels() -> None:
    a = [1, 2, 3]
    b = a  # not a copy: `b` is a second label on the same list object
    b.append(4)
    print("names_are_labels:", a, b, "same object?", a is b)
    # a is now [1, 2, 3, 4] too — there was only ever one list.


def identity_vs_equality() -> None:
    x = [1, 2]
    y = [1, 2]
    print("identity_vs_equality: x == y ->", x == y, "| x is y ->", x is y)
    # Equal values, different objects. `==` asks "same value?"; `is` asks
    # "same object?" (identical id()).
    print("  id(x) =", id(x), " id(y) =", id(y))


def the_small_int_cache() -> None:
    # CPython pre-builds int objects for -5..256 and reuses them, so `is` can
    # look like it works on small ints. It is an implementation detail — never
    # rely on it.
    m, n = 256, 256
    p, q = 257, 257
    print("small_int_cache: 256 is 256 ->", m is n, "| 257 is 257 ->", p is q)


def rebinding_is_not_mutating() -> None:
    def rebind(seq: list[int]) -> None:
        seq = seq + [99]  # builds a NEW list, points the local name at it
        print("  inside rebind, local seq =", seq)

    def mutate(seq: list[int]) -> None:
        seq.append(99)  # changes the object the caller still holds

    data = [1, 2, 3]
    rebind(data)
    print("rebinding_is_not_mutating: after rebind ->", data)
    mutate(data)
    print("rebinding_is_not_mutating: after mutate ->", data)


def default_shared_reference() -> None:
    # The default value object is created ONCE, when the function is defined,
    # and shared by every call that does not pass the argument.
    def append_to(value: int, bucket: list[int] = []) -> list[int]:
        bucket.append(value)
        return bucket

    # Call one at a time: all three names would otherwise be evaluated before
    # print() runs, and by then they all show the final [1, 2, 3].
    print("default_shared_reference:", append_to(1))
    print("default_shared_reference:", append_to(2))
    print("default_shared_reference:", append_to(3))
    # -> [1] then [1, 2] then [1, 2, 3]: it is the same list object every call.


def main() -> None:
    names_are_labels()
    identity_vs_equality()
    the_small_int_cache()
    rebinding_is_not_mutating()
    default_shared_reference()


if __name__ == "__main__":
    main()

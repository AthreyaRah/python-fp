"""Iterators & the iterator protocol - the practice snippet.

Run it:  python code/foundations/10_iterators_and_the_iterator_protocol/demo.py

Mental model:
- An ITERABLE has `__iter__()` which returns a fresh iterator. Lists, dicts,
  sets, strings, files, ranges are iterables.
- An ITERATOR has `__next__()` (returns the next item or raises StopIteration)
  and `__iter__()` (returns self). It carries the "where am I" state.
- `for x in obj:` is sugar for: it = iter(obj); while True: try x = next(it)
  except StopIteration: break.
- An iterator is consumed. An iterable can be walked again (it makes a new
  iterator each time).
"""

from __future__ import annotations

import itertools


def for_loop_desugared() -> None:
    it = iter([10, 20, 30])
    print("iter([...]) ->", type(it).__name__)
    while True:
        try:
            print("  next ->", next(it))
        except StopIteration:
            print("  StopIteration: done")
            break


def iterable_vs_iterator() -> None:
    data = [1, 2, 3]                 # an iterable
    print("list is its own iterator?", iter(data) is data)  # False - fresh each time
    it = iter(data)
    print("an iterator is its own iterator?", iter(it) is it)  # True


class Countdown:
    """A self-contained iterator: __next__ + __iter__ returning self."""

    def __init__(self, start: int) -> None:
        self.n = start

    def __iter__(self) -> Countdown:
        return self

    def __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1


def custom_iterator() -> None:
    print("Countdown(4):", list(Countdown(4)))


def infinite_iterator_sliced() -> None:
    evens = (n for n in itertools.count(0, 2))  # infinite
    print("first 5 evens:", list(itertools.islice(evens, 5)))


def iter_with_sentinel() -> None:
    chunks = iter(itertools.count().__next__, 5)  # call until it returns 5
    print("iter(callable, sentinel):", list(chunks))  # [0, 1, 2, 3, 4]


def main() -> None:
    for_loop_desugared()
    print()
    iterable_vs_iterator()
    print()
    custom_iterator()
    print()
    infinite_iterator_sliced()
    print()
    iter_with_sentinel()


if __name__ == "__main__":
    main()

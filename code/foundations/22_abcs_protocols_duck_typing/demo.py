"""ABCs, Protocols & duck typing - the practice snippet.

Run it:  python code/foundations/22_abcs_protocols_duck_typing/demo.py

Three ways to talk about "what an object can do":
- Duck typing: don't check the type at all - just call the method and let it
  fail if it's absent. Pythonic default.
- abc.ABC + @abstractmethod: a base class that CANNOT be instantiated until every
  abstract method is implemented. Enforced at construction, `isinstance` works.
- typing.Protocol: structural typing for static checkers - "anything with these
  methods" - no inheritance required. `@runtime_checkable` enables a shallow
  `isinstance`.
"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Protocol, runtime_checkable


def total_size(source) -> int:
    """Duck typing: works on anything with .read() returning bytes/str."""
    return len(source.read())


class Exporter(ABC):
    @abstractmethod
    def export(self, rows: list[dict]) -> str: ...

    def summary(self, rows: list[dict]) -> str:   # concrete helper, inherited
        return f"{len(rows)} rows -> {len(self.export(rows))} chars"


class CsvExporter(Exporter):
    def export(self, rows: list[dict]) -> str:
        if not rows:
            return ""
        header = ",".join(rows[0])
        body = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
        return header + "\n" + body


class Pair(Sequence):
    """Implement __getitem__ + __len__; get __contains__, __iter__, index, count free."""

    def __init__(self, a, b):
        self._data = (a, b)

    def __getitem__(self, i):
        return self._data[i]

    def __len__(self):
        return 2


@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...


def duck_typing() -> None:
    print("total_size(BytesIO):", total_size(io.BytesIO(b"hello")))
    print("total_size(StringIO):", total_size(io.StringIO("hi there")))


def abc_enforcement() -> None:
    exp = CsvExporter()
    rows = [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Bo"}]
    print("CsvExporter.summary:", exp.summary(rows))
    print("isinstance(exp, Exporter):", isinstance(exp, Exporter))


def abc_mixins() -> None:
    p = Pair("x", "y")
    print("Pair supports 'in':", "x" in p, "| iter:", list(p), "| index:", p.index("y"))


def protocol_check() -> None:
    print("isinstance([1,2,3], Sized):", isinstance([1, 2, 3], Sized))
    print("isinstance(42, Sized):", isinstance(42, Sized))


def main() -> None:
    duck_typing()
    print()
    abc_enforcement()
    print()
    abc_mixins()
    print()
    protocol_check()


if __name__ == "__main__":
    main()

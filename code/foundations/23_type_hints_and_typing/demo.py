"""Type hints, typing & mypy - the practice snippet.

Run it:  python code/foundations/23_type_hints_and_typing/demo.py

Mental model:
- Annotations are METADATA. Python stores them on `__annotations__` and does
  NOTHING else - `def f(x: int)` never checks that `x` is an int at runtime.
- A separate static checker (mypy, pyright) reads them and flags mismatches
  before you run the code.
- `X | None` (aka `Optional[X]`) means "X or None" - it does not make a parameter
  optional; only a default value does that.
- `from __future__ import annotations` stores annotations as strings; read them
  back with `typing.get_type_hints`, not raw `__annotations__`.
"""

from __future__ import annotations

from typing import Literal, TypedDict, TypeVar, get_type_hints

T = TypeVar("T")


def first(items: list[T]) -> T | None:      # generic: return type follows input
    return items[0] if items else None


class UserRow(TypedDict):
    id: int
    name: str
    active: bool


def make_row(raw: dict) -> UserRow:
    return {"id": int(raw["id"]), "name": raw["name"], "active": raw.get("active", True)}


Mode = Literal["r", "w", "a"]


def open_mode(mode: Mode) -> str:
    return f"opening in {mode!r}"


def annotations_are_not_enforced() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    # Passing strings: no TypeError. The annotation is ignored at runtime.
    print("add('x', 'y') =", add("x", "y"), " <- str concatenation, no complaint")
    print("add.__annotations__ =", add.__annotations__)


def reading_hints_at_runtime() -> None:
    print("get_type_hints(first):", get_type_hints(first))
    print("get_type_hints(UserRow):", get_type_hints(UserRow))


def generics_and_typeddict() -> None:
    print("first([10, 20]) =", first([10, 20]))
    print("first([]) =", first([]))
    print("make_row:", make_row({"id": "7", "name": "Ada"}))


def main() -> None:
    annotations_are_not_enforced()
    print()
    reading_hints_at_runtime()
    print()
    generics_and_typeddict()
    print()
    print(open_mode("w"))


if __name__ == "__main__":
    main()

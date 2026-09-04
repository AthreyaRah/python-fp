"""The match statement: structural pattern matching - the practice snippet.

Run it:  python code/foundations/42_match_statement/demo.py

Mental model: `match` is NOT a switch. It DESTRUCTURES a value against patterns
and binds names from the pieces. Pattern kinds:
- literal   : `case 200:` `case "GET":`        - compares with ==
- capture   : `case x:`                        - always matches, binds x
- wildcard  : `case _:`                        - always matches, binds nothing
- sequence  : `case [a, b]:` `case [h, *t]:`   - NOT str/bytes
- mapping   : `case {"k": v}:`                  - extra keys ignored
- class     : `case Point(x=0, y=y):`          - by attribute; positional needs
                                                 __match_args__ (dataclasses have it)
- or        : `case 1 | 2 | 3:`
- guard     : `case x if x > 0:`
A BARE NAME is a capture, not a comparison - use a dotted name (`Color.RED`) or a
literal to match against a value.
"""

from __future__ import annotations

from dataclasses import dataclass


def classify_status(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "ok"
        case 301 | 302:
            return "redirect"
        case 400 | 404 | 409:
            return "client error"
        case int() if code >= 500:
            return "server error"
        case _:
            return "unknown"


def run_command(line: str) -> str:
    match line.split():
        case ["go", ("north" | "south" | "east" | "west") as direction]:
            return f"moving {direction}"
        case ["take", *items]:
            return f"taking {', '.join(items)}"
        case ["quit" | "exit"]:
            return "bye"
        case []:
            return "(no command)"
        case _:
            return f"unknown: {line!r}"


@dataclass
class Point:
    x: int
    y: int


def describe_point(p: Point) -> str:
    match p:
        case Point(0, 0):
            return "origin"
        case Point(0, y):
            return f"on the y-axis at {y}"
        case Point(x, 0):
            return f"on the x-axis at {x}"
        case Point(x, y) if x == y:
            return f"on the diagonal at {x}"
        case Point():
            return "somewhere else"


def handle_event(event: dict) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at ({x}, {y})"
        case {"type": "key", "code": code, **rest}:
            return f"key {code} (extra: {sorted(rest)})"
        case {"type": kind}:
            return f"other event: {kind}"
        case _:
            return "not an event"


def main() -> None:
    print("status:", [classify_status(c) for c in (200, 302, 404, 503, 100)])
    for line in ("go north", "take sword shield", "quit", "", "dance"):
        print(f"  {line!r:20} -> {run_command(line)}")
    print("points:", [describe_point(p) for p in
                      (Point(0, 0), Point(0, 5), Point(3, 0), Point(4, 4), Point(1, 2))])
    print("event:", handle_event({"type": "key", "code": "ESC", "shift": True}))


if __name__ == "__main__":
    main()

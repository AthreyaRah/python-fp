"""Functions: args/kwargs, closures, nonlocal - the practice snippet.

Run it:  python code/foundations/12_functions_args_closures/demo.py

Mental model:
- Functions are ordinary objects: bind them to names, pass them, return them,
  give them attributes.
- A parameter is one of: positional-or-keyword, positional-only (before `/`),
  keyword-only (after `*`), `*args` (extra positionals), `**kwargs` (extra
  keywords).
- A CLOSURE is a nested function plus the variables it captures from the
  enclosing scope. It captures the VARIABLE (a "cell"), not a snapshot.
- Assigning to a name anywhere in a function makes that name local for the whole
  body. `nonlocal` / `global` opt out of that.
"""

from __future__ import annotations


def parameter_kinds(pos_only, /, normal, *args, kw_only, **kwargs):
    return {
        "pos_only": pos_only,
        "normal": normal,
        "args": args,
        "kw_only": kw_only,
        "kwargs": kwargs,
    }


def functions_are_objects() -> None:
    def greet(name: str) -> str:
        return f"hi {name}"

    greet.calls = 0                       # attach an attribute
    alias = greet                         # bind to another name
    print("name:", alias.__name__, "| result:", alias("Ada"), "| attr:", greet.calls)
    print("sorted with a function key:", sorted(["bb", "a", "ccc"], key=len))


def a_closure_captures_a_cell() -> None:
    def make_adder(n: int):
        def add(x: int) -> int:
            return x + n                  # `n` is free - captured from make_adder
        return add

    add10 = make_adder(10)
    print("add10(5) =", add10(5))
    print("free vars:", add10.__code__.co_freevars,
          "| cell contents:", [c.cell_contents for c in add10.__closure__])


def nonlocal_rebinds_the_enclosing_name() -> None:
    def make_counter():
        count = 0

        def tick() -> int:
            nonlocal count               # without this: UnboundLocalError
            count += 1
            return count

        return tick

    c = make_counter()
    print("counter:", c(), c(), c())


def main() -> None:
    print("parameter_kinds:", parameter_kinds(1, 2, 3, 4, kw_only=5, extra=6))
    print()
    functions_are_objects()
    print()
    a_closure_captures_a_cell()
    print()
    nonlocal_rebinds_the_enclosing_name()


if __name__ == "__main__":
    main()

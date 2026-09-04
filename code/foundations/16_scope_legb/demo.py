"""Scope & namespaces (LEGB) - the practice snippet.

Run it:  python code/foundations/16_scope_legb/demo.py

Mental model: to resolve a bare name, Python searches four namespaces in order:
    Local      - names assigned in the current function
    Enclosing  - locals of any enclosing function(s)
    Global     - names at module top level
    Built-in   - print, len, list, sum, ...
The first match wins. ASSIGNING to a name makes it Local for the whole function
(unless declared `global` or `nonlocal`). Class bodies and comprehensions have
their own namespaces too.
"""

from __future__ import annotations

VALUE = "global"


def legb_order() -> None:
    VALUE = "enclosing"

    def inner() -> None:
        VALUE = "local"
        print("  inner sees:", VALUE)                # Local

    def inner_reads_enclosing() -> None:
        print("  inner_reads_enclosing sees:", VALUE)  # Enclosing

    inner()
    inner_reads_enclosing()
    print("  module-level VALUE is still:", VALUE)   # enclosing here, not touched


def global_needs_declaring() -> None:
    global VALUE
    VALUE = "reassigned via global"


def class_body_is_not_an_enclosing_scope() -> None:
    class Config:
        DEFAULT_TIMEOUT = 30

        def describe(self) -> str:
            # Bare `DEFAULT_TIMEOUT` would be a NameError here - the class body is
            # not part of the method's scope chain. Reach it via the class/instance.
            return f"timeout={self.DEFAULT_TIMEOUT}"

    print("  ", Config().describe())


def comprehension_has_its_own_scope() -> None:
    data = [1, 2, 3]
    squares = [n * n for n in data]
    print("  squares:", squares, "| is 'n' visible here?", "n" in dir())


def inspecting_namespaces() -> None:
    x = 1  # noqa: F841
    print("  locals() keys:", sorted(locals()))
    print("  'VALUE' in globals():", "VALUE" in globals())
    print("  'len' in dir(__builtins__) or builtins:", callable(len))


def main() -> None:
    print("start: VALUE =", VALUE)
    legb_order()
    global_needs_declaring()
    print("after global_needs_declaring: VALUE =", VALUE)
    class_body_is_not_an_enclosing_scope()
    comprehension_has_its_own_scope()
    inspecting_namespaces()


if __name__ == "__main__":
    main()

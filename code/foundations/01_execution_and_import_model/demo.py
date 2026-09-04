"""The execution & import model — the practice snippet.

Run it:  python code/foundations/01_execution_and_import_model/demo.py

Mental model: CPython does NOT interpret your source line by line. It first
*compiles* the whole file to bytecode (a list of simple instructions for a stack
machine), caches that as a .pyc, and then a loop called the evaluation loop
executes the bytecode. `import` is just "find a file, compile it, run its body
top to bottom, once, and cache the resulting module object".
"""

from __future__ import annotations

import dis
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402


def source_becomes_bytecode() -> None:
    src = "x = 1\ny = x + 2\nprint(y)"
    code = compile(src, "<demo>", "exec")
    print("co_consts:", code.co_consts)
    print("co_names :", code.co_names)
    print("disassembly:")
    dis.dis(code)


def a_module_is_an_object_imported_once() -> None:
    pkg = generated_dir("exec_model")
    mod_path = pkg / "greeter.py"
    mod_path.write_text(
        textwrap.dedent(
            '''
            print("  [greeter.py body is running]")
            GREETING = "hello"

            def greet(name):
                return f"{GREETING}, {name}"
            '''
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    sys.path.insert(0, str(pkg))
    for attempt in (1, 2, 3):
        print(f"import attempt {attempt}:")
        import greeter  # noqa: PLC0415 - importing repeatedly on purpose

    print("  body ran exactly once; 'greeter' is now in sys.modules:",
          "greeter" in sys.modules)
    print("  greet('world') ->", greeter.greet("world"))
    sys.path.pop(0)
    del sys.modules["greeter"]


def name_main() -> None:
    print("  __name__ in this file is:", repr(__name__))
    print("  -> the `if __name__ == \"__main__\":` block runs only when this file")
    print("     is the program entry point, not when it is imported.")


def where_pyc_files_live() -> None:
    cache = Path(__file__).parent / "__pycache__"
    print("  __pycache__ for this dir:", cache if cache.exists() else "(not created yet)")
    if cache.exists():
        for pyc in sorted(cache.glob("*.pyc")):
            print("   ", pyc.name)


def main() -> None:
    print("1) source -> bytecode")
    source_becomes_bytecode()
    print("\n2) a module's body runs once, then it is cached")
    a_module_is_an_object_imported_once()
    print("\n3) __name__ and the main guard")
    name_main()
    print("\n4) compiled bytecode is cached on disk as .pyc")
    where_pyc_files_live()


if __name__ == "__main__":
    main()

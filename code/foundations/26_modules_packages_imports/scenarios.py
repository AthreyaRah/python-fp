"""Modules & packages - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/26_modules_packages_imports/scenarios.py

Each scenario writes a throwaway package to a scratch dir and imports it.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

ROOT = generated_dir("modules_scenarios")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _write(rel: str, body: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")


def _fresh(name: str):
    for mod in [m for m in sys.modules if m == name or m.startswith(name + ".")]:
        del sys.modules[mod]
    importlib.invalidate_caches()
    return importlib.import_module(name)


# ======================================================================================
# Scenario 1 - Circular import with `from x import name`.
# ======================================================================================

def s1_build() -> str:
    _write("circ_ok/__init__.py", "")
    _write("circ_ok/a.py", """
        import circ_ok.b            # import the MODULE, not a name from it

        def a_val():
            return "A calls " + circ_ok.b.b_val()
    """)
    _write("circ_ok/b.py", """
        import circ_ok.a

        def b_val():
            return "B"
    """)
    return _fresh("circ_ok.a").a_val()  # "A calls B"


def s1_break() -> str:
    _write("circ_bad/__init__.py", "")
    _write("circ_bad/a.py", """
        from circ_bad.b import b_val   # needs b_val NOW, during import

        def a_val():
            return "A calls " + b_val()
    """)
    _write("circ_bad/b.py", """
        from circ_bad.a import a_val   # ...but a_val isn't defined yet

        def b_val():
            return "B"
    """)
    try:
        _fresh("circ_bad.a")
    except ImportError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s1_fix() -> str:
    _write("circ_fixed/__init__.py", "")
    _write("circ_fixed/a.py", """
        def a_val():
            from circ_fixed.b import b_val   # deferred: runs at call time
            return "A calls " + b_val()
    """)
    _write("circ_fixed/b.py", """
        from circ_fixed.a import a_val

        def b_val():
            return "B"
    """)
    return _fresh("circ_fixed.a").a_val()


S1_WHY = """
When `circ_bad.a` starts running, `from circ_bad.b import b_val` triggers
`circ_bad.b`, which runs `from circ_bad.a import a_val` - but `circ_bad.a` is only
half executed and `a_val` is not defined yet, so `ImportError: cannot import name
'a_val' from partially initialized module`. Fixes: `import circ_bad.b` and use
`circ_bad.b.b_val()` (binds the module, which exists), defer the import into the
function body, or break the cycle by moving shared code to a third module.
"""


# ======================================================================================
# Scenario 2 - Relative import run as a script.
# ======================================================================================

def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)


def s2_build() -> str:
    _write("relpkg/__init__.py", "")
    _write("relpkg/helpers.py", "GREETING = 'hi'")
    _write("relpkg/main.py", """
        from . import helpers

        if __name__ == "__main__":
            print(helpers.GREETING)
    """)
    proc = _run(["-m", "relpkg.main"])       # run as a module -> package context
    return proc.stdout.strip()  # "hi"


def s2_break() -> str:
    _write("relpkg2/__init__.py", "")
    _write("relpkg2/helpers.py", "GREETING = 'hi'")
    _write("relpkg2/main.py", """
        from . import helpers
        print(helpers.GREETING)
    """)
    proc = _run(["relpkg2/main.py"])         # run the file directly
    return proc.stderr.strip().splitlines()[-1]  # the ImportError line


def s2_fix() -> str:
    proc = _run(["-m", "relpkg2.main"])
    return proc.stdout.strip()


S2_WHY = """
A relative import resolves against `__package__`. When you run a file directly
(`python pkg/main.py`), `__name__` is `"__main__"` and `__package__` is empty, so
`from . import helpers` raises
`ImportError: attempted relative import with no known parent package`. Run it as a
module (`python -m pkg.main`), which sets the package context, or use absolute
imports.
"""


# ======================================================================================
# Scenario 3 - `from pkg import *` without __all__.
# ======================================================================================

def s3_build() -> list[str]:
    _write("star_ok/__init__.py", """
        import os   # a helper the package uses internally
        VERSION = "1.0"

        def public_api():
            return "ok"

        __all__ = ["VERSION", "public_api"]   # only these are exported
    """)
    ns: dict = {}
    exec("from star_ok import *", ns)
    _fresh("star_ok")
    return sorted(k for k in ns if not k.startswith("__"))  # ['VERSION', 'public_api']


def s3_break() -> bool:
    _write("star_bad/__init__.py", """
        import os
        import sys
        VERSION = "1.0"

        def public_api():
            return "ok"
        # no __all__
    """)
    _fresh("star_bad")
    ns: dict = {}
    exec("from star_bad import *", ns)
    # `os` and `sys` leaked into the importing namespace along with the real API.
    return "os" in ns and "sys" in ns


def s3_fix() -> list[str]:
    _write("star_fixed/__init__.py", """
        import os
        VERSION = "1.0"

        def public_api():
            return "ok"

        __all__ = ["VERSION", "public_api"]
    """)
    _fresh("star_fixed")
    ns: dict = {}
    exec("from star_fixed import *", ns)
    return sorted(k for k in ns if not k.startswith("__"))


S3_WHY = """
`from pkg import *` copies every name in the module that doesn't start with `_` -
including modules you imported for internal use (`os`, `sys`). Define `__all__` as
the explicit export list and `*` copies only those. (Better: avoid `import *`
entirely outside the REPL.)
"""


# ======================================================================================
# Scenario 4 - `import a.b.c` binds only `a`.
# ======================================================================================

def s4_build() -> int:
    _write("deep/__init__.py", "")
    _write("deep/inner/__init__.py", "")
    _write("deep/inner/calc.py", "def triple(n):\n    return n * 3")
    _fresh("deep")
    from deep.inner import calc  # binds `calc`
    return calc.triple(5)  # 15


def s4_break() -> str:
    _write("deep2/__init__.py", "")
    _write("deep2/inner/__init__.py", "")
    _write("deep2/inner/calc.py", "def triple(n):\n    return n * 3")
    _fresh("deep2")
    ns: dict = {}
    try:
        exec("import deep2.inner.calc\nresult = calc.triple(5)", ns)  # NameError: calc
    except NameError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> int:
    _fresh("deep2")
    ns: dict = {}
    exec("import deep2.inner.calc as calc\nresult = calc.triple(5)", ns)
    return ns["result"]  # 15


S4_WHY = """
`import deep2.inner.calc` executes all three modules and caches them, but binds
only the TOP name `deep2` in your namespace. You then reach the function as
`deep2.inner.calc.triple(...)`. To bind `calc` directly use `from deep2.inner
import calc` or `import deep2.inner.calc as calc`.
"""


SCENARIOS = [
    Scenario("Circular import with from-import", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Relative import run as a script", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("from pkg import * without __all__", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("import a.b.c binds only a", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

"""The execution & import model — four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/01_execution_and_import_model/scenarios.py

Each scenario writes a tiny throwaway module to a generated directory and imports
it, so you can watch import behaviour directly.
"""

from __future__ import annotations

import importlib
import os
import sys
import textwrap
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

PKG = generated_dir("exec_model_scenarios")
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

_clock = [time.time()]


def _write_module(name: str, body: str) -> None:
    path = PKG / f"{name}.py"
    path.write_text(textwrap.dedent(body).strip() + "\n", encoding="utf-8")
    # Force a strictly-increasing mtime so importlib.reload always recompiles
    # rather than trusting a .pyc written < 1s earlier in the same run.
    _clock[0] += 2
    os.utime(path, (_clock[0], _clock[0]))
    importlib.invalidate_caches()


def _fresh_import(name: str):
    sys.modules.pop(name, None)
    return importlib.import_module(name)


# ======================================================================================
# Scenario 1 — A module body runs once; editing the file does not re-run it.
# ======================================================================================

def s1_build() -> int:
    _write_module("cfg_a", "LOADS = 0\nLOADS += 1\nVALUE = 42")
    mod = _fresh_import("cfg_a")
    # Simulate the file changing on disk, then reload explicitly.
    _write_module("cfg_a", "LOADS = 0\nLOADS += 1\nVALUE = 99")
    mod = importlib.reload(mod)
    return mod.VALUE  # 99 — reload re-ran the (new) body


def s1_break() -> int:
    sys.modules.pop("cfg_b", None)
    _write_module("cfg_b", "VALUE = 1")
    first = importlib.import_module("cfg_b")
    _write_module("cfg_b", "VALUE = 2")  # file changed on disk
    second = importlib.import_module("cfg_b")  # plain import — cache hit
    assert first is second, "same cached module object"
    assert second.VALUE == 1, "still the old value; the new body never ran"
    return second.VALUE


def s1_fix() -> int:
    _write_module("cfg_c", "VALUE = 1")
    mod = _fresh_import("cfg_c")
    _write_module("cfg_c", "VALUE = 2")
    mod = importlib.reload(mod)  # or drop it from sys.modules and re-import
    return mod.VALUE  # 2


S1_WHY = """
The first `import name` compiles the file, runs its body, and stores the module
object in `sys.modules["name"]`. Every later `import name` — anywhere in the
program — finds it there and skips straight to binding the name. The file on disk
is irrelevant after that first load. `importlib.reload` (or deleting the
sys.modules entry) is what forces the body to run again.
"""


# ======================================================================================
# Scenario 2 — The missing `if __name__ == "__main__"` guard.
# ======================================================================================

def s2_build() -> list[str]:
    _write_module(
        "tool_ok",
        '''
        RAN_AS_MAIN = []

        def main():
            RAN_AS_MAIN.append("did work")

        if __name__ == "__main__":
            main()
        ''',
    )
    mod = _fresh_import("tool_ok")
    return mod.RAN_AS_MAIN  # [] — importing did not run main()


def s2_break() -> list[str]:
    _write_module(
        "tool_bad",
        '''
        SIDE_EFFECTS = []

        def main():
            SIDE_EFFECTS.append("did work")

        main()   # top level: runs on import too
        ''',
    )
    mod = _fresh_import("tool_bad")
    assert mod.SIDE_EFFECTS == ["did work"], "import triggered the side effect"
    return mod.SIDE_EFFECTS


def s2_fix() -> list[str]:
    _write_module(
        "tool_fixed",
        '''
        SIDE_EFFECTS = []

        def main():
            SIDE_EFFECTS.append("did work")

        if __name__ == "__main__":
            main()
        ''',
    )
    mod = _fresh_import("tool_fixed")
    return mod.SIDE_EFFECTS  # []


S2_WHY = """
`import`ing a module runs its entire top-level body. A bare `main()` call at
module level therefore fires every time something imports the file — including
test collectors and, notoriously, `multiprocessing` on spawn platforms, where it
causes recursive process creation. `__name__` is `"__main__"` only for the file
you launched; for an imported file it is the module name, so the guard skips it.
"""


# ======================================================================================
# Scenario 3 — Expensive work at import time.
# ======================================================================================

def s3_build() -> int:
    _write_module(
        "lazy_ok",
        '''
        _cache = {}

        def get_table():
            if "t" not in _cache:
                _cache["t"] = sum(i * i for i in range(10_000))
            return _cache["t"]
        ''',
    )
    mod = _fresh_import("lazy_ok")
    assert mod._cache == {}, "nothing computed until first use"
    return mod.get_table()


def s3_break() -> tuple[bool, int]:
    _write_module(
        "eager_bad",
        '''
        # Runs during import, before anyone asked for it.
        TABLE = sum(i * i for i in range(10_000))
        IMPORT_DID_WORK = True
        ''',
    )
    mod = _fresh_import("eager_bad")
    # Every importer pays this cost, even one that never touches TABLE.
    return mod.IMPORT_DID_WORK, mod.TABLE


def s3_fix() -> int:
    _write_module(
        "eager_fixed",
        '''
        import functools

        @functools.cache
        def table():
            return sum(i * i for i in range(10_000))
        ''',
    )
    mod = _fresh_import("eager_fixed")
    return mod.table()


S3_WHY = """
Import executes the module body. Anything at top level — a big computation, a file
read, a network call, a DB connection — happens the moment the module is first
imported, and blocks the importer. Put such work behind a function (optionally
cached), so the cost is paid once, on demand, by code that actually needs it.
"""


# ======================================================================================
# Scenario 4 — A local file shadows a standard-library module.
# ======================================================================================

def _restore_tabnanny() -> None:
    (PKG / "tabnanny.py").unlink(missing_ok=True)
    sys.modules.pop("tabnanny", None)


def s4_build() -> bool:
    _restore_tabnanny()
    import tabnanny

    return hasattr(tabnanny, "check")  # True — the real stdlib module


def s4_break() -> str:
    # A file named tabnanny.py, earlier on sys.path, wins over the stdlib.
    _write_module("tabnanny", "IS_THE_REAL_STDLIB_MODULE = False")
    shadow = _fresh_import("tabnanny")
    hijacked = getattr(shadow, "IS_THE_REAL_STDLIB_MODULE", "MISSING")
    assert hijacked is False, "we imported the local file, not the stdlib"
    assert not hasattr(shadow, "check"), "stdlib API is gone"
    return f"IS_THE_REAL_STDLIB_MODULE={hijacked}"


def s4_fix() -> bool:
    # Remove the shadow (in real life: rename your file), clear the cache.
    _restore_tabnanny()
    import tabnanny

    return hasattr(tabnanny, "check")  # True again


S4_WHY = """
`import tabnanny` searches `sys.path` in order and takes the first match.
`sys.path` starts with the script's own directory (or "" for the cwd), so a file
you named `queue.py`, `random.py`, `email.py`, `tabnanny.py` etc. is found before
the standard library's copy. The fix is always: do not name your files after
stdlib modules.
"""


SCENARIOS = [
    Scenario("A module body runs once", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Missing the __main__ guard", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Expensive work at import time", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("A local file shadows a stdlib module", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    try:
        run_all(SCENARIOS)
    finally:
        _restore_tabnanny()  # never leave the shadow behind


if __name__ == "__main__":
    main()

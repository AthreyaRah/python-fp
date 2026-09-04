"""Environments & packaging - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/27_environments_and_packaging/scenarios.py
"""

from __future__ import annotations

import importlib
import sys
import tomllib
from importlib import metadata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

PKG = generated_dir("packaging_scenarios")
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))


# ======================================================================================
# Scenario 1 - A local file shadows an installed package.
# ======================================================================================

def _restore(name: str) -> None:
    (PKG / f"{name}.py").unlink(missing_ok=True)
    sys.modules.pop(name, None)


def s1_build() -> bool:
    _restore("tabnanny")
    import tabnanny
    return hasattr(tabnanny, "check")  # the real stdlib module (stands in for any
                                       # pip-installed package you might shadow)


def s1_break() -> bool:
    (PKG / "tabnanny.py").write_text("IS_THE_REAL_ONE = False\n", encoding="utf-8")
    sys.modules.pop("tabnanny", None)
    importlib.invalidate_caches()
    shadow = importlib.import_module("tabnanny")
    return getattr(shadow, "IS_THE_REAL_ONE", True) is False  # imported our file


def s1_fix() -> bool:
    _restore("tabnanny")
    importlib.invalidate_caches()
    import tabnanny
    return hasattr(tabnanny, "check")


S1_WHY = """
`sys.path` starts with the script directory / cwd, ahead of site-packages. A file
named the same as a dependency (`requests.py`, `click.py`, `email.py`) is found
first, so `import requests` gets YOUR file and the real package is unreachable.
Fixes: don't name modules after packages; use a `src/` layout so your package
isn't importable from the repo root by accident.
"""


# ======================================================================================
# Scenario 2 - tomllib.load without binary mode.
# ======================================================================================

def _toml_file() -> Path:
    p = PKG / "conf.toml"
    p.write_text('[project]\nname = "x"\nversion = "1.0"\n', encoding="utf-8")
    return p


def s2_build() -> dict:
    with _toml_file().open("rb") as fh:      # binary mode
        return tomllib.load(fh)


def s2_break() -> str:
    with _toml_file().open("r", encoding="utf-8") as fh:  # text mode
        try:
            return str(tomllib.load(fh))
        except TypeError as exc:
            return f"{type(exc).__name__}: {exc}"


def s2_fix() -> dict:
    with _toml_file().open("rb") as fh:
        return tomllib.load(fh)


S2_WHY = """
`tomllib.load` reads bytes and does its own UTF-8 decoding (the TOML spec mandates
UTF-8), so it requires a file opened in BINARY mode ('rb'). A text-mode handle
raises `TypeError: File must be opened in binary mode, e.g. use open('foo.toml',
'rb')`. Use `tomllib.loads(text)` if you already have a string.
"""


# ======================================================================================
# Scenario 3 - tomllib is a read-only parser (no dump).
# ======================================================================================

def s3_build() -> str:
    # Round-trip by templating the text yourself (or use the third-party tomli_w).
    data = {"name": "demo", "version": "0.3.0"}
    return f'name = "{data["name"]}"\nversion = "{data["version"]}"\n'


def s3_break() -> str:
    try:
        tomllib.dump({"name": "demo"}, None)  # no such function
    except AttributeError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s3_fix() -> dict:
    text = s3_build()
    return tomllib.loads(text)  # can still read what we wrote


S3_WHY = """
The standard library added a TOML *parser* (`tomllib`) in 3.11 but deliberately
not a writer - `tomllib.dump` / `dumps` do not exist. To emit TOML, template the
string yourself for simple cases, or add the third-party `tomli-w` / `tomlkit`
(the latter preserves comments and formatting).
"""


# ======================================================================================
# Scenario 4 - Import name vs distribution name.
# ======================================================================================

def s4_build() -> bool:
    # `_pytest` is the import package; the DISTRIBUTION that ships it is `pytest`.
    dist = metadata.packages_distributions().get("_pytest", ["pytest"])[0]
    return bool(metadata.version(dist))


def s4_break() -> str:
    try:
        # Querying by the IMPORT name of a package whose distribution differs.
        # (In the wild: `import yaml` <- `PyYAML`, `import cv2` <- `opencv-python`.)
        metadata.version("_pytest")
    except metadata.PackageNotFoundError as exc:
        return f"{type(exc).__name__}: {exc}"
    return "no error (unexpected)"


def s4_fix() -> bool:
    dist = metadata.packages_distributions().get("_pytest", ["pytest"])[0]
    return bool(metadata.version(dist))


S4_WHY = """
The name you `import` and the name pip installs are independent: `import yaml`
comes from `PyYAML`, `import bs4` from `beautifulsoup4`, `import cv2` from
`opencv-python`, `import _pytest` from `pytest`. `importlib.metadata.version(...)`
wants the DISTRIBUTION name (normalized: dashes, not underscores). Use
`importlib.metadata.packages_distributions()` to map an import name to its
distribution.
"""


SCENARIOS = [
    Scenario("Local file shadows a package", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("tomllib needs binary mode", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("tomllib has no writer", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Import name vs distribution name", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    try:
        run_all(SCENARIOS)
    finally:
        _restore("tabnanny")


if __name__ == "__main__":
    main()

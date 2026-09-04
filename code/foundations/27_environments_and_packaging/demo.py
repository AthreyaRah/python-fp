"""venv, pip, pyproject.toml & wheels - the practice snippet.

Run it:  python code/foundations/27_environments_and_packaging/demo.py

Mental model:
- A VIRTUAL ENVIRONMENT is a directory with its own `python` and `site-packages`.
  `sys.prefix` points into it; `sys.base_prefix` points at the interpreter that
  created it. When they differ, you are in a venv.
- `pip install X` unpacks a WHEEL (a pre-built .whl zip) into the active
  environment's site-packages. `pip install -e .` instead links your source
  directory so edits take effect immediately.
- `pyproject.toml` is the standard project file: `[build-system]` (how to build)
  and `[project]` (name, version, dependencies). Parse it with `tomllib` (stdlib,
  read-only, binary mode).
- The IMPORT name and the DISTRIBUTION name can differ (`import yaml` <- `PyYAML`).
"""

from __future__ import annotations

import sys
import sysconfig
import textwrap
import tomllib
from importlib import metadata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402


def where_am_i() -> None:
    in_venv = sys.prefix != sys.base_prefix
    print("in a virtual environment:", in_venv)
    print("sys.prefix       :", sys.prefix)
    print("site-packages    :", sysconfig.get_path("purelib"))
    print("sys.path[0]       :", repr(sys.path[0] or "<cwd>"))


def parse_pyproject() -> None:
    p = generated_dir("packaging_demo") / "pyproject.toml"
    p.write_text(
        textwrap.dedent(
            """
            [build-system]
            requires = ["setuptools>=68"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "demo-app"
            version = "0.2.0"
            requires-python = ">=3.11"
            dependencies = ["httpx>=0.27", "rich"]

            [project.optional-dependencies]
            dev = ["pytest", "mypy"]
            """
        ).strip() + "\n",
        encoding="utf-8",
    )
    with p.open("rb") as fh:                 # tomllib requires binary mode
        cfg = tomllib.load(fh)
    proj = cfg["project"]
    print("name/version   :", proj["name"], proj["version"])
    print("dependencies   :", proj["dependencies"])
    print("dev extra      :", cfg["project"]["optional-dependencies"]["dev"])


def query_installed() -> None:
    for dist in ("pytest", "hypothesis", "definitely-not-installed"):
        try:
            print(f"{dist:24} version {metadata.version(dist)}")
        except metadata.PackageNotFoundError:
            print(f"{dist:24} not installed")
    mapping = metadata.packages_distributions()
    # `import _pytest` is shipped by the `pytest` distribution.
    print("import '_pytest' comes from:", mapping.get("_pytest", ["<none>"]))


def main() -> None:
    where_am_i()
    print()
    parse_pyproject()
    print()
    query_installed()


if __name__ == "__main__":
    main()

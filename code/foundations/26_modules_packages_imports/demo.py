"""Modules, packages & circular imports - the practice snippet.

Run it:  python code/foundations/26_modules_packages_imports/demo.py

Mental model:
- A MODULE is one .py file. A PACKAGE is a directory (usually with __init__.py).
- `import a.b.c` runs a, a.b, a.b.c once each and binds only the name `a`.
- `from a.b import c` binds `c`.
- Relative imports (`from . import x`, `from ..pkg import y`) resolve against the
  current package - they only work when the file is imported AS part of a package,
  not run directly.
- Every imported module is cached in `sys.modules`; the body runs once.

This script builds a tiny package on disk, then imports it.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402


def build_package() -> Path:
    root = generated_dir("demo_pkg_area")
    pkg = root / "shapes"
    pkg.mkdir(exist_ok=True)
    (pkg / "__init__.py").write_text(
        textwrap.dedent(
            '''
            """The shapes package."""
            from .circle import area as circle_area   # relative import
            from .square import area as square_area

            __all__ = ["circle_area", "square_area"]   # controls `from shapes import *`
            '''
        ).strip() + "\n",
        encoding="utf-8",
    )
    (pkg / "circle.py").write_text(
        'import math\n\ndef area(r):\n    return math.pi * r * r\n', encoding="utf-8"
    )
    (pkg / "square.py").write_text(
        'def area(side):\n    return side * side\n', encoding="utf-8"
    )
    return root


def main() -> None:
    root = build_package()
    sys.path.insert(0, str(root))

    import shapes
    print("shapes.circle_area(2) =", round(shapes.circle_area(2), 3))
    print("shapes.square_area(3) =", shapes.square_area(3))

    # `import a.b` binds only `a`; the submodule is reachable as an attribute.
    import shapes.square
    print("shapes.square.area(4) =", shapes.square.area(4))

    loaded = sorted(m for m in sys.modules if m.startswith("shapes"))
    print("sys.modules entries for the package:", loaded)
    print("shapes.__all__ =", shapes.__all__)

    for name in ("shapes", "shapes.circle", "shapes.square"):
        sys.modules.pop(name, None)
    sys.path.pop(0)


if __name__ == "__main__":
    main()

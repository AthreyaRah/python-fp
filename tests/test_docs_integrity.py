"""Structural checks on the docs tree.

- Every `--8<--` snippet include in a page points at a file that exists.
- Every authored topic page has a matching code/ directory.
- Every topic listed in scripts/scaffold.py has a page on disk.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"

SNIPPET_RE = re.compile(r'--8<--\s+"([^"]+)"')
TOPIC_RE = re.compile(r"^\d{2}-")
TRACKS = ("foundations",)


def _load_scaffold():
    spec = importlib.util.spec_from_file_location("scaffold", REPO / "scripts" / "scaffold.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_all_snippet_includes_resolve():
    missing = []
    for md in DOCS.rglob("*.md"):
        for target in SNIPPET_RE.findall(md.read_text(encoding="utf-8")):
            path = target.split(":", 1)[0].strip()  # strip any section/line spec
            if not (REPO / path).exists():
                missing.append(f"{md.relative_to(REPO)} -> {path}")
    assert not missing, "broken snippet includes:\n" + "\n".join(missing)


def test_authored_pages_have_code_dirs():
    """A page marked '<!-- status: authored -->' under a track must have code."""
    offenders = []
    for track in TRACKS:
        for md in (DOCS / track).glob("*.md"):
            if not TOPIC_RE.match(md.name):
                continue
            head = md.read_text(encoding="utf-8")[:40]
            if "status: authored" not in head:
                continue
            num = md.stem.split("-", 1)[0]
            if not list((REPO / "code" / track).glob(f"{num}_*")):
                offenders.append(str(md.relative_to(REPO)))
    assert not offenders, "authored pages without code/:\n" + "\n".join(offenders)


def test_every_curriculum_topic_has_a_page():
    scaffold = _load_scaffold()
    missing = []
    for track, _title, topics in scaffold.TRACKS:
        for i, (slug, _t) in enumerate(topics, start=1):
            page = DOCS / track / f"{i:02d}-{slug}.md"
            if not page.exists():
                missing.append(str(page.relative_to(REPO)))
    assert not missing, "curriculum topics with no page (run scripts/scaffold.py):\n" + "\n".join(
        missing
    )

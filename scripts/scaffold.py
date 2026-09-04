"""Generate stub doc pages and the mkdocs nav from the curriculum definition.

Run from the repo root:  python scripts/scaffold.py

- Creates docs/foundations/<nn>-<slug>.md for every topic that does not yet exist.
- Never overwrites a page that has been authored (looks for the marker
  "<!-- status: authored -->" on the first line).
- Rewrites the `nav:` block of mkdocs.yml to match the curriculum order.

Scope: this site is the pure-Python Foundations common core only - the basics
that every domain (backend, data engineering, data science, ML/AI) needs. There
are no domain-specific tracks.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# --------------------------------------------------------------------------------------
# Curriculum. Numbers are assigned automatically from list order.
# --------------------------------------------------------------------------------------

FOUNDATIONS = [
    ("execution-and-import-model", "The execution & import model"),
    ("names-objects-references", "Names, objects & references"),
    ("mutability-and-the-default-arg-trap", "Mutability & the mutable-default trap"),
    ("the-data-model-and-dunders", "The data model & dunder methods"),
    ("numeric-types", "Numeric types: int, float, Decimal, Fraction"),
    ("strings-bytes-unicode", "Strings, bytes & Unicode"),
    ("builtin-containers-and-complexity", "list, tuple, dict, set: internals & complexity"),
    ("the-collections-module", "The collections module"),
    ("comprehensions", "Comprehensions & generator expressions"),
    ("iterators-and-the-iterator-protocol", "Iterators & the iterator protocol"),
    ("generators-and-yield-from", "Generators & yield from"),
    ("functions-args-closures", "Functions: args/kwargs, closures, nonlocal"),
    ("decorators", "Decorators"),
    ("functools", "functools"),
    ("itertools", "itertools"),
    ("scope-legb", "Scope & namespaces (LEGB)"),
    ("exceptions", "Exceptions: EAFP, chaining, groups"),
    ("context-managers", "Context managers & with"),
    ("classes-and-oop", "Classes & OOP from first principles"),
    ("inheritance-and-mro", "Inheritance, MRO & super()"),
    ("dataclasses-and-slots", "dataclasses & __slots__"),
    ("abcs-protocols-duck-typing", "ABCs, Protocols & duck typing"),
    ("type-hints-and-typing", "Type hints, typing & mypy"),
    ("descriptors", "Descriptors"),
    ("metaclasses", "Metaclasses & __init_subclass__"),
    ("modules-packages-imports", "Modules, packages & circular imports"),
    ("environments-and-packaging", "venv, pip, pyproject.toml & wheels"),
    ("file-io-and-pathlib", "File I/O & pathlib"),
    ("serialization-stdlib", "Serialization: json, pickle, csv, struct"),
    ("dates-and-times", "Dates & times: aware vs naive, zoneinfo"),
    ("floating-point-and-random", "Floating point, random & reproducibility"),
    ("regex", "Regular expressions & catastrophic backtracking"),
    ("gil-threads-races", "The GIL, threads & race conditions"),
    ("multiprocessing-and-futures", "multiprocessing & concurrent.futures"),
    ("asyncio", "asyncio: the event loop & coroutines"),
    ("memory-model-and-weakref", "The memory model & weakref"),
    ("profiling-and-dis", "Profiling: timeit, cProfile, dis"),
    ("testing-with-pytest", "Testing with pytest & hypothesis"),
    ("logging", "Logging"),
    ("stdlib-toolkit", "stdlib toolkit: argparse, enum, subprocess"),
    ("copy-shallow-vs-deep", "copy: shallow vs deep"),
    ("match-statement", "The match statement: structural pattern matching"),
    ("idioms-and-anti-patterns", "Idioms & anti-patterns"),
]

TRACKS = [
    ("foundations", "Foundations", FOUNDATIONS),
]

STUB_TEMPLATE = """<!-- status: stub -->
# {title}

!!! warning "Stub"
    This page is not written yet. It is on the build list. The structure below is
    what every topic on this site follows.

## First principles

_What problem does this primitive exist to solve? What is the mental model? What
does the interpreter actually do underneath?_

## The mechanism

_Under the hood, with a diagram where it helps._

## Practice

_A runnable snippet, embedded from `code/{track}/{nn}_{code_slug}/demo.py`, that
generates its own data and then demonstrates the concept._

## Scenarios

_Four Build -> Break -> Fix -> Understand scenarios._

## Pitfalls & idioms

## See also

## Check yourself
"""


def page_path(track: str, num: int, slug: str) -> Path:
    return DOCS / track / f"{num:02d}-{slug}.md"


def is_authored(path: Path) -> bool:
    if not path.exists():
        return False
    first = path.read_text(encoding="utf-8").splitlines()[:1]
    return bool(first) and "status: authored" in first[0]


def write_stubs() -> None:
    for track, _title, topics in TRACKS:
        (DOCS / track).mkdir(parents=True, exist_ok=True)
        for i, (slug, title) in enumerate(topics, start=1):
            path = page_path(track, i, slug)
            if is_authored(path):
                continue
            if path.exists() and "status: stub" not in path.read_text(encoding="utf-8")[:40]:
                continue  # something hand-made lives here; leave it
            code_slug = slug.replace("-", "_")
            path.write_text(
                STUB_TEMPLATE.format(title=title, track=track, nn=f"{i:02d}", code_slug=code_slug),
                encoding="utf-8",
            )


def build_nav() -> str:
    lines = ["nav:", "  - Home: index.md", "  - How to use this site: how-to-use.md"]
    for track, title, topics in TRACKS:
        lines.append(f"  - {title}:")
        lines.append(f"      - {track}/index.md")
        for i, (slug, _t) in enumerate(topics, start=1):
            lines.append(f"      - {track}/{i:02d}-{slug}.md")
    lines.append("  - Appendix:")
    lines.append("      - appendix/glossary.md")
    lines.append("      - appendix/cheatsheets.md")
    lines.append('      - "Check yourself: answers": appendix/check-yourself-answers.md')
    return "\n".join(lines) + "\n"


def rewrite_nav() -> None:
    cfg_path = ROOT / "mkdocs.yml"
    text = cfg_path.read_text(encoding="utf-8")
    text = re.sub(r"\nnav:\n(?: .*\n?|\n)*$", "\n" + build_nav(), text)
    if "\nnav:\n" not in text:
        text = text.rstrip() + "\n\n" + build_nav()
    cfg_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    write_stubs()
    rewrite_nav()
    total = sum(len(t) for _, _, t in TRACKS)
    print(f"scaffolded {total} Foundations topic pages; nav rewritten")

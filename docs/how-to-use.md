<!-- status: authored -->
# How to use this site

## Read in order, at least the first time

Within a track, topics are numbered because each one leans on the ones before it.
Foundations especially: [names and references](foundations/02-names-objects-references.md)
has to land before [mutability](foundations/03-mutability-and-the-default-arg-trap.md)
will make sense.

If you already know the material, use the numbers as a checklist: can you do the
**Break** and **Understand** parts without looking? If not, you have found a gap.

## Every topic has a script — run it

Each topic maps to a directory under `code/`:

```
code/foundations/<nn>_<topic>/
    demo.py         # the practice snippet from the page. Run this first.
    scenarios.py    # s1_build / s1_break / s1_fix … — the four scenarios
    test_topic.py   # what CI asserts: demo runs, and each break actually breaks
```

Run a demo straight from the repo root:

```bash
python code/foundations/02_names_objects_references/demo.py
```

`scenarios.py` is also runnable and prints each step:

```bash
python code/foundations/02_names_objects_references/scenarios.py
```

The code embedded in each page is pulled directly from these files, so what you
read is exactly what runs. A CI check fails the build if they ever drift.

## The data is fake and self-generating

No topic asks you to "download a dataset first." If a demo needs a CSV, a SQLite
database, a JSON-Lines log, or a text corpus, it builds one at the top of the
script — deterministically, from a fixed seed — writes it into a git-ignored
`_generated/` folder, and then works on it. Open those files and look at them;
that is the point.

Shared generators live in `code/_harness/dummydata.py`
(`people_rows`, `write_people_csv`, `write_events_jsonl`, `build_shop_db`,
`text_documents`, …) — all standard-library, all seeded. A topic uses the shared
one unless the topic *is* about making the data.

## The four scenarios

!!! example "🔨 Build"
    A minimal thing that works. Small enough to hold in your head.

!!! failure "💥 Break"
    One change — a moved line, a wrong flag, a shared default — and the exact
    error or wrong answer it produces. Reproduce it yourself.

!!! success "🔧 Fix"
    The correction, and why it is the right one rather than a workaround.

!!! quote "🧠 Why it behaved that way"
    The failure explained through the mechanism from the top of the page. This is
    the part that transfers to code you have never seen.

## Check yourself

Every topic ends with five questions. Answer them from memory before moving on —
if you can't, you've found a gap. Worked answers for all of them are in
[Check yourself: answers](appendix/check-yourself-answers.md).

## Local setup for contributors

```bash
pip install -e ".[dev]"           # docs + test runner + ruff + mypy
mkdocs serve                      # live preview at http://127.0.0.1:8000
pytest                            # fast — everything is standard-library only
ruff check . && mypy              # lint + type-check
python scripts/scaffold.py        # regenerate stubs + nav after editing the curriculum
```

CI runs the same four checks (`pytest`, `run_all.py`, `ruff`/`mypy`,
`mkdocs build --strict`) on Python 3.11–3.13.

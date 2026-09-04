# Contributing

Thanks for helping. The bar for this repo is: **every claim is demonstrated by
code that runs in CI, and every "break" is asserted to actually break.**

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## The shape of a topic

Each topic is a page under `docs/foundations/NN-slug.md` plus a directory
`code/foundations/NN_slug/` containing three files:

| File | Purpose |
|---|---|
| `demo.py` | The practice snippet from the page. Runs with `python <file>`. Generates any data it needs (CSV, SQLite, corpus…) at the top — nothing to download. Has a `main()` and an `if __name__ == "__main__":` guard. |
| `scenarios.py` | Four scenarios, each `s1_build` / `s1_break` / `s1_fix` (…`s4_…`) plus an `S1_WHY` string. A `SCENARIOS` list of `Scenario(...)` and a `main()` that calls `run_all(SCENARIOS)`. |
| `test_topic.py` | Asserts `demo.main()` runs and produces the expected output, and that each scenario's `break` genuinely misbehaves (`pytest.raises`, or asserted wrong value) while `fix` works. |

The page follows a fixed template — copy an authored page
(`02-names-objects-references.md` is a good model):

1. **First principles** — the primitive from zero: the problem it solves, the
   mental model, what the interpreter/library actually does.
2. **The mechanism** — under the hood, with a Mermaid diagram where it earns its
   place.
3. **Practice** — the `demo.py` embedded via `--8<-- "code/foundations/NN_slug/demo.py"`
   and a `python code/foundations/NN_slug/demo.py` run line.
4. **Scenarios** — the four Build → Break → Fix → Understand-why blocks as
   Material admonitions (`!!! example "🔨 Build"` etc.).
5. **Pitfalls & idioms** — a quick list.
6. **See also** — cross-links (relative `.md` paths).
7. **Check yourself** — 3–5 questions. Add worked answers to
   `docs/appendix/check-yourself-answers.md`.

Mark the page authored with `<!-- status: authored -->` on the first line.

## Rules for scenario code

- Deterministic. No wall-clock-ratio assertions (they flake in CI). Count
  operations, assert exact values, or `pytest.raises`.
- Standard library only.
- Guard platform-specific behaviour (`@pytest.mark.skipif(sys.platform == "win32", …)`).
- The scenario files *demonstrate* anti-patterns — the linter is configured to
  allow that in `scenarios.py` / `demo.py`.

## Before opening a PR

```bash
pytest                                          # every demo runs; every break breaks
python code/_harness/run_all.py                 # every demo, as a subprocess
ruff check . && ruff format --check code/_harness scripts tests conftest.py
mypy                                            # code/_harness + scripts
mkdocs build --strict                           # no broken links / nav / snippet paths
```

## Changing the curriculum

`scripts/scaffold.py` owns the topic list, generates stub pages, and rewrites the
`mkdocs.yml` nav. Edit the `FOUNDATIONS` list there, then run
`python scripts/scaffold.py`. Renumbering an existing topic means renaming its
`code/` directory and `docs/` file and updating cross-links.

## Scope

This repo is the **pure-Python common core** only. Domain-specific material
(web frameworks, pandas, PyTorch, …) is deliberately out of scope.

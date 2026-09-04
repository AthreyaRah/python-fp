# Python from First Principles

A first-principles learning path for the **pure-Python common core** — the
language and standard-library concepts that every Python job relies on, whether
you go on to backend, data engineering, data science, or ML/AI.

Deliberately scoped to that shared foundation: no web frameworks, no pandas, no
PyTorch. One track, **Foundations**, **43 topics**, in dependency order.

Every topic has:

- a **first-principles** explanation — the mechanism from zero, not "trust the
  library";
- a **runnable script** (`demo.py`) that generates its own data if it needs any;
- **four scenarios** (`scenarios.py`), each a **Build → Break → Fix →
  Understand-why** arc;
- **tests** (`test_topic.py`) that assert the demo runs and each break really
  breaks.

Plus a glossary, cheat sheets, and worked answers to every "Check yourself"
question.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"           # docs + tests + ruff + mypy (no runtime deps)

mkdocs serve                      # http://127.0.0.1:8000
python code/foundations/02_names_objects_references/demo.py
python code/foundations/02_names_objects_references/scenarios.py
pytest                            # every demo runs; every documented "break" breaks
ruff check . && mypy              # lint + type-check
```

## Layout

```
docs/
  foundations/            43 topics, in order (index.md is the syllabus)
  appendix/               glossary · cheat sheets · check-yourself answers
  assets/                 favicon
code/
  _harness/               shared stdlib-only dummy-data generators + Scenario helper
  foundations/<nn>_<topic>/
    demo.py               the practice snippet — run it
    scenarios.py          s1_build / s1_break / s1_fix … for four scenarios
    test_topic.py         CI: demo runs, and each "break" really breaks
tests/                    cross-cutting checks (all demos run, docs integrity)
scripts/scaffold.py       regenerate stub pages + nav from the curriculum list
```

## Status

**All 43 Foundations topics authored.** 348 tests pass; `ruff check`, `mypy`, and
`mkdocs build --strict` are clean; all 43 demos run clean — Python 3.14 locally,
3.11–3.13 in CI.

`.github/workflows/`:

- `ci.yml` — `pytest` + `run_all.py` on 3.11–3.13, `ruff` + `mypy`, strict docs
  build.
- `deploy.yml` — publishes the docs to GitHub Pages on push to `main` (enable
  once: *Settings → Pages → Source: GitHub Actions*).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The bar: every claim is demonstrated by
code that runs in CI, and every "break" is asserted to actually break.

## License

MIT — see [LICENSE](LICENSE).

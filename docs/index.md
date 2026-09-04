<!-- status: authored -->
# Python from First Principles

Most Python material teaches a library. This teaches the machinery underneath it —
what each primitive *is*, what problem it exists to solve, and what the interpreter
actually does when you use it. Then it makes you break it on purpose, because you
do not understand a thing until you have seen it fail and know exactly why.

This is the **pure-Python common core**: the concepts and standard-library tools
that every Python job relies on, whether you go on to build a web service, an ETL
pipeline, a data-science analysis, or a model training loop. It is deliberately
scoped to that shared foundation — no web frameworks, no pandas, no PyTorch. Just
the language and its standard library, from the ground up.

## The shape of every topic

<div class="grid cards" markdown>

-   :material-lightbulb-on: __First principles__

    The primitive from zero: the problem it solves, the mental model, and what
    happens underneath — bytecode, reference counts, the protocol, the data
    structure. No "just trust the framework."

-   :material-cog: __The mechanism__

    How it actually works, with a diagram when a diagram earns its place.

-   :material-play: __Practice__

    A single runnable script. If the topic needs a CSV, a database, or a corpus,
    **the script generates that data itself** and then teaches the topic. Copy,
    run, read the output.

-   :material-hammer-wrench: __Build → Break → Fix → Understand__

    Four scenarios per topic. Build a small working artifact. Break it with one
    precise change and watch it fail. Fix it. Then explain *why* it behaved that
    way, tracing the failure back to the mechanism.

</div>

## What's here

One track — [**Foundations**](foundations/index.md), **43 topics** — in
dependency order, from the execution model through concurrency, testing, and
idioms. Work top to bottom the first time; each topic leans on the ones before
it. When you finish, you should be able to open an unfamiliar Python file and
predict what it does, where it will be slow, and how it will fail.

Also: a [glossary](appendix/glossary.md), [cheat sheets](appendix/cheatsheets.md),
and [worked answers](appendix/check-yourself-answers.md) to every topic's
"Check yourself" questions.

## Start here

1. Read [How to use this site](how-to-use.md) (2 minutes).
2. Begin with [The execution & import model](foundations/01-execution-and-import-model.md).
3. For each topic: read the page, run its `demo.py`, run its `scenarios.py`, then
   answer the "Check yourself" questions before moving on.

## Running the code

```bash
git clone https://github.com/AthreyaRah/python-fp && cd python-fp
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"          # standard-library only — this is just the test runner

python code/foundations/02_names_objects_references/demo.py
python code/foundations/02_names_objects_references/scenarios.py
pytest                            # every demo runs; every documented "break" really breaks
```

CI runs `pytest` on Python 3.11–3.13, `ruff` + `mypy`, and `mkdocs build
--strict`. See [How to use this site](how-to-use.md).

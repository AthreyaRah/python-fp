"""Logging - the practice snippet.

Run it:  python code/foundations/39_logging/demo.py

Mental model:
- `logging` routes leveled diagnostic messages. Levels:
  DEBUG < INFO < WARNING < ERROR < CRITICAL. A message is emitted only if its
  level >= the logger's (and the handler's) threshold.
- LOGGER  = who is speaking. Name them by module: `logging.getLogger(__name__)`.
  Loggers form a hierarchy on the dotted name and messages PROPAGATE up to the
  root.
- HANDLER = where it goes (stderr, a file, syslog). FORMATTER = how it looks.
- Pass values as ARGS, not f-strings: `log.info("user %s", uid)` - the `%s`
  substitution is skipped entirely when the level is disabled.
- In an `except` block, `log.exception("...")` records the traceback.
- Configure ONCE, at program startup. Never use `print` for app diagnostics.
"""

from __future__ import annotations

import io
import logging

log = logging.getLogger("demo")


def configure() -> io.StringIO:
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return buffer


def levels_and_routing(buf: io.StringIO) -> None:
    log.debug("this is DEBUG - below the INFO threshold, dropped")
    log.info("app started")
    log.warning("disk at %d%%", 91)              # lazy arg substitution
    child = logging.getLogger("demo.worker")
    child.info("worker ready")                    # propagates up to the root handler
    print(buf.getvalue().strip())


def exception_logging(buf: io.StringIO) -> None:
    buf.seek(0), buf.truncate(0)
    try:
        int("not a number")
    except ValueError:
        log.exception("parse failed")            # includes the traceback
    out = buf.getvalue()
    print("contains 'Traceback':", "Traceback" in out, "| level:", "ERROR" in out)


def lazy_formatting_saves_work(buf: io.StringIO) -> None:
    calls = {"n": 0}

    class Expensive:
        def __str__(self):
            calls["n"] += 1
            return "computed"

    log.debug("value = %s", Expensive())         # DEBUG disabled -> __str__ NOT called
    print("Expensive.__str__ calls at INFO level:", calls["n"])


def main() -> None:
    buf = configure()
    levels_and_routing(buf)
    print()
    exception_logging(buf)
    print()
    lazy_formatting_saves_work(buf)


if __name__ == "__main__":
    main()

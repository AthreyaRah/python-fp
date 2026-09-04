"""Logging - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/39_logging/scenarios.py
"""

from __future__ import annotations

import io
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402


def _fresh_root() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.WARNING)


def _capture(logger_name: str) -> tuple[logging.Logger, io.StringIO]:
    buf = io.StringIO()
    h = logging.StreamHandler(buf)
    h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    lg = logging.getLogger(logger_name)
    lg.handlers.clear()
    lg.addHandler(h)
    lg.setLevel(logging.DEBUG)
    lg.propagate = False
    return lg, buf


# ======================================================================================
# Scenario 1 - basicConfig() called after logging has already happened.
# ======================================================================================

def s1_build() -> bool:
    _fresh_root()
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", force=True)
    buf = io.StringIO()
    logging.getLogger().handlers[0].stream = buf   # point it at our buffer
    logging.getLogger("s1").debug("hello debug")
    return "hello debug" in buf.getvalue()


def s1_break() -> bool:
    _fresh_root()
    logging.warning("something happened")          # auto-installs a handler at WARNING
    logging.basicConfig(level=logging.DEBUG)        # too late: root already has a handler
    buf = io.StringIO()
    for h in logging.getLogger().handlers:
        if isinstance(h, logging.StreamHandler):
            h.stream = buf
    logging.getLogger("s1b").debug("hello debug")
    return "hello debug" not in buf.getvalue()      # DEBUG still suppressed


def s1_fix() -> bool:
    _fresh_root()
    logging.warning("something happened")
    logging.basicConfig(level=logging.DEBUG, force=True)   # force=True replaces handlers
    buf = io.StringIO()
    for h in logging.getLogger().handlers:
        if isinstance(h, logging.StreamHandler):
            h.stream = buf
    logging.getLogger("s1c").debug("hello debug")
    return "hello debug" in buf.getvalue()


S1_WHY = """
`logging.basicConfig()` does NOTHING if the root logger already has handlers -
and the first call to `logging.warning()`/`error()` etc. auto-installs one. So a
`basicConfig(level=DEBUG)` that runs after any logging has occurred is silently
ignored and DEBUG stays hidden. Call `basicConfig` first thing at startup, or
pass `force=True` to replace the existing handlers.
"""


# ======================================================================================
# Scenario 2 - f-string in a log call does the work even when the level is off.
# ======================================================================================

class _Expensive:
    calls = 0

    def __str__(self):
        type(self).calls += 1
        return "rendered"


def s2_build() -> int:
    _Expensive.calls = 0
    lg, _ = _capture("s2a")
    lg.setLevel(logging.INFO)                     # DEBUG disabled
    lg.debug("value = %s", _Expensive())         # lazy: __str__ skipped
    return _Expensive.calls  # 0


def s2_break() -> int:
    _Expensive.calls = 0
    lg, _ = _capture("s2b")
    lg.setLevel(logging.INFO)
    lg.debug(f"value = {_Expensive()}")          # f-string: rendered right now
    return _Expensive.calls  # 1 - wasted work for a message that is dropped


def s2_fix() -> int:
    _Expensive.calls = 0
    lg, _ = _capture("s2c")
    lg.setLevel(logging.INFO)
    lg.debug("value = %s", _Expensive())         # pass as an arg
    if lg.isEnabledFor(logging.DEBUG):           # or guard genuinely expensive work
        lg.debug("expensive = %s", _Expensive())
    return _Expensive.calls  # 0


S2_WHY = """
`log.debug(f"{obj}")` builds the whole string - calling `obj.__str__()` and the
f-string machinery - BEFORE `debug()` is invoked, so the cost is paid even though
the message is immediately discarded at INFO level. Passing `("value = %s", obj)`
lets `logging` skip the `%`-formatting entirely when the level is disabled. For
genuinely costly arguments, guard with `if log.isEnabledFor(logging.DEBUG):`.
"""


# ======================================================================================
# Scenario 3 - Logging an exception without the traceback.
# ======================================================================================

def s3_build() -> bool:
    lg, buf = _capture("s3a")
    try:
        {}["missing"]
    except KeyError:
        lg.exception("lookup failed")            # traceback included
    return "Traceback" in buf.getvalue()


def s3_break() -> bool:
    lg, buf = _capture("s3b")
    try:
        {}["missing"]
    except KeyError as exc:
        lg.error("lookup failed: %s", exc)       # just the message, no traceback
    out = buf.getvalue()
    return "Traceback" not in out and "lookup failed" in out


def s3_fix() -> bool:
    lg, buf = _capture("s3c")
    try:
        {}["missing"]
    except KeyError:
        lg.error("lookup failed", exc_info=True)  # or lg.exception("lookup failed")
    return "Traceback" in buf.getvalue()


S3_WHY = """
`log.error("failed: %s", exc)` records only the message you passed - the
stack trace is lost, so you know THAT it failed but not WHERE. Inside an `except`
block use `log.exception("failed")` (which sets `exc_info=True` and logs at ERROR)
or `log.error("failed", exc_info=True)` to attach the traceback.
"""


# ======================================================================================
# Scenario 4 - Duplicate log lines from adding handlers repeatedly.
# ======================================================================================

def _make_logger_bad(buf: io.StringIO) -> logging.Logger:
    lg = logging.getLogger("s4.bad")
    h = logging.StreamHandler(buf)               # a NEW handler every call
    lg.addHandler(h)
    lg.setLevel(logging.INFO)
    lg.propagate = False
    return lg


def _make_logger_good(buf: io.StringIO) -> logging.Logger:
    lg = logging.getLogger("s4.good")
    if not lg.handlers:                          # configure once
        lg.addHandler(logging.StreamHandler(buf))
        lg.setLevel(logging.INFO)
        lg.propagate = False
    return lg


def s4_build() -> int:
    logging.getLogger("s4.good").handlers.clear()
    buf = io.StringIO()
    for _ in range(3):
        _make_logger_good(buf).info("once")
    return buf.getvalue().count("once")  # 3 lines for 3 calls


def s4_break() -> int:
    logging.getLogger("s4.bad").handlers.clear()
    buf = io.StringIO()
    for _ in range(3):
        _make_logger_bad(buf).info("hi")
    # call 1 -> 1 handler -> 1 line; call 2 -> 2 handlers -> 2 lines; call 3 -> 3.
    return buf.getvalue().count("hi")  # 6, not 3


def s4_fix() -> int:
    logging.getLogger("s4.good").handlers.clear()
    buf = io.StringIO()
    for _ in range(3):
        _make_logger_good(buf).info("hi")
    return buf.getvalue().count("hi")  # 3


S4_WHY = """
`logger.addHandler(h)` appends - it does not replace - so calling it every time a
function runs (or on every request) stacks up handlers, and each one emits every
message: N handlers -> N copies of each line. Configure handlers ONCE, at
application startup (or guard with `if not logger.handlers:`), and let library
modules just call `logging.getLogger(__name__)` with no handler at all.
"""


SCENARIOS = [
    Scenario("basicConfig after logging started", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("f-string in a log call", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Exception without a traceback", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Duplicate lines from re-adding handlers", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

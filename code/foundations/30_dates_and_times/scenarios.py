"""Dates & times - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/30_dates_and_times/scenarios.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

UTC = timezone.utc
NY = ZoneInfo("America/New_York")


# ======================================================================================
# Scenario 1 - Subtracting a naive and an aware datetime.
# ======================================================================================

def s1_build() -> float:
    a = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    b = datetime(2024, 6, 1, 10, 0, tzinfo=UTC)
    return (a - b).total_seconds() / 3600  # 2.0


def s1_break() -> str:
    aware = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    naive = datetime(2024, 6, 1, 10, 0)          # no tzinfo
    try:
        return str((aware - naive).total_seconds())
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> float:
    aware = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    naive = datetime(2024, 6, 1, 10, 0)
    # If you know the naive value is UTC, attach it explicitly.
    fixed = naive.replace(tzinfo=UTC)
    return (aware - fixed).total_seconds() / 3600  # 2.0


S1_WHY = """
A naive datetime is wall-clock digits with no zone; an aware one is a real
instant. Python refuses to subtract/compare across the two kinds -
`TypeError: can't subtract offset-naive and offset-aware datetimes` - because the
answer would depend on an assumption it won't make for you. Decide what zone the
naive value is in and attach it (`.replace(tzinfo=...)`), or parse it as aware
from the start.
"""


# ======================================================================================
# Scenario 2 - datetime.utcnow() returns a NAIVE value.
# ======================================================================================

def s2_build() -> bool:
    now = datetime.now(UTC)                       # aware
    return now.tzinfo is UTC and abs(now.timestamp() - _real_epoch(now)) < 1


def _real_epoch(dt: datetime) -> float:
    return dt.replace(tzinfo=UTC).timestamp() if dt.tzinfo is None else dt.timestamp()


def s2_break() -> bool:
    # utcnow() gives the UTC wall clock but with tzinfo=None (deprecated in 3.12).
    fake_utcnow = datetime(2024, 6, 1, 12, 0)     # stand-in for datetime.utcnow()
    aware_utc = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    # .timestamp() on a NAIVE datetime assumes LOCAL time, not UTC -> wrong epoch
    # unless the machine happens to be on UTC.
    naive_epoch = fake_utcnow.replace(tzinfo=NY).timestamp()  # simulate "local != UTC"
    return naive_epoch != aware_utc.timestamp()   # they disagree


def s2_fix() -> bool:
    now = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)  # always aware
    return now.timestamp() == datetime(2024, 6, 1, 12, 0, tzinfo=UTC).timestamp()


S2_WHY = """
`datetime.utcnow()` returns the current UTC time but as a NAIVE datetime (no
tzinfo) - a long-standing footgun, deprecated since 3.12. Downstream code that
calls `.timestamp()` or compares it treats a naive value as LOCAL time, so on any
machine not set to UTC the result is off by the local offset. Use
`datetime.now(timezone.utc)`, which is aware.
"""


# ======================================================================================
# Scenario 3 - Subtracting two aware datetimes that share one tzinfo across DST.
# ======================================================================================

# 2024-03-10 in New York: clocks jump 02:00 EST -> 03:00 EDT (spring forward).
_BEFORE = datetime(2024, 3, 10, 1, 30, tzinfo=NY)   # 06:30 UTC
_AFTER = datetime(2024, 3, 10, 3, 30, tzinfo=NY)    # 07:30 UTC  -> 1 real hour later


def s3_build() -> float:
    # Convert both to UTC first -> real elapsed time.
    return (_AFTER.astimezone(UTC) - _BEFORE.astimezone(UTC)).total_seconds() / 3600


def s3_break() -> float:
    # Both operands carry the SAME ZoneInfo object, so datetime subtraction does
    # naive wall-clock arithmetic and ignores the skipped hour.
    hours = (_AFTER - _BEFORE).total_seconds() / 3600
    assert hours == 2.0, "wall-clock difference, not real elapsed"
    return hours


def s3_fix() -> float:
    return (_AFTER.astimezone(UTC) - _BEFORE.astimezone(UTC)).total_seconds() / 3600


S3_WHY = """
When both datetimes are aware AND have the *same* tzinfo object, Python's
subtraction ignores the offset and just compares the wall-clock fields - so
across a DST transition you get the difference in displayed time (2h), not the
real elapsed time (1h, because 02:00-03:00 never happened). Normalise to UTC
(`.astimezone(timezone.utc)`) before doing duration arithmetic.
"""


# ======================================================================================
# Scenario 4 - Parsing a timestamp string without a timezone.
# ======================================================================================

def s4_build() -> bool:
    # ISO string with an offset parses straight to an aware datetime.
    dt = datetime.fromisoformat("2024-06-01T12:00:00+00:00")
    return dt.tzinfo is not None


def s4_break() -> str:
    dt = datetime.strptime("2024-06-01 12:00", "%Y-%m-%d %H:%M")  # no %z -> naive
    try:
        return str(dt < datetime.now(UTC))       # naive vs aware comparison
    except TypeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s4_fix() -> bool:
    dt = datetime.strptime("2024-06-01 12:00", "%Y-%m-%d %H:%M")
    dt = dt.replace(tzinfo=UTC)                   # you know the source is UTC
    return dt < datetime.now(UTC)


S4_WHY = """
A format string without `%z` (or an ISO string without an offset) produces a
NAIVE datetime - `strptime` has no zone information to attach. Comparing it to an
aware `now()` then raises. Include the offset in the data and parse it
(`%z`, or `fromisoformat` for real ISO-8601), or attach the zone you know the
source uses right after parsing.
"""


SCENARIOS = [
    Scenario("Subtracting naive and aware", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("utcnow() is naive", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("timedelta across DST", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Parsing without a timezone", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

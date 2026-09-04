"""Dates & times: aware vs naive, zoneinfo - the practice snippet.

Run it:  python code/foundations/30_dates_and_times/demo.py

Mental model:
- A NAIVE datetime has no `tzinfo`. It is just wall-clock numbers - it does not
  identify a moment in time. `datetime.now()` is naive local.
- An AWARE datetime has a `tzinfo` and denotes a real instant.
  `datetime.now(timezone.utc)` is aware.
- Never mix them: comparing / subtracting a naive and an aware datetime raises.
- Rule of thumb: work in aware UTC internally; convert to a local zone
  (`zoneinfo.ZoneInfo("Area/City")`) only at the edges (display, user input).
- `timedelta` is an absolute duration; adding one crosses DST transitions in
  real time, so the wall clock can shift.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo


def naive_vs_aware() -> None:
    naive = datetime(2024, 6, 1, 12, 0)
    aware = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)
    print("naive.tzinfo:", naive.tzinfo, "| aware.tzinfo:", aware.tzinfo)
    print("aware as epoch:", aware.timestamp())
    try:
        _ = aware - naive
    except TypeError as exc:
        print("aware - naive ->", exc)


def timezones_and_dst() -> None:
    ny = ZoneInfo("America/New_York")
    # 2024-03-10: New York springs forward, 02:00 EST -> 03:00 EDT.
    before = datetime(2024, 3, 10, 1, 30, tzinfo=ny)
    after = datetime(2024, 3, 10, 3, 30, tzinfo=ny)
    print("before offset:", before.utcoffset(), "| after offset:", after.utcoffset())
    # Same tzinfo object -> subtraction uses wall-clock fields (2h)...
    print("naive subtraction:", (after - before).total_seconds() / 3600, "h")
    # ...convert to UTC for the true elapsed time (1h - an hour was skipped).
    print("via UTC:", (after.astimezone(UTC)
                       - before.astimezone(UTC)).total_seconds() / 3600, "h")


def timedelta_math() -> None:
    start = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
    print("start + 90 min:", (start + timedelta(minutes=90)).isoformat())
    print("days until 2024-12-25:", (date(2024, 12, 25) - date(2024, 1, 1)).days)


def iso_round_trip() -> None:
    t = datetime(2024, 6, 1, 15, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    s = t.isoformat()
    print("isoformat:", s)
    print("parsed back equal:", datetime.fromisoformat(s) == t)


def main() -> None:
    naive_vs_aware()
    print()
    timezones_and_dst()
    print()
    timedelta_math()
    print()
    iso_round_trip()


if __name__ == "__main__":
    main()

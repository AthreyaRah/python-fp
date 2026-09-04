"""Regular expressions - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/32_regex/scenarios.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

# ======================================================================================
# Scenario 1 - re.match only anchors at the start.
# ======================================================================================

def s1_build() -> str:
    return re.search(r"\d+", "order abc123def").group()  # '123'


def s1_break() -> str | None:
    m = re.match(r"\d+", "order abc123def")   # tries only at position 0
    return m  # None


def s1_fix() -> str:
    return re.search(r"\d+", "order abc123def").group()


S1_WHY = """
`re.match(pattern, s)` anchors the match at the START of the string - it is
`re.search(r"^" + pattern, s)` in spirit. `"order abc123def"` doesn't begin with a
digit, so it returns `None`. Use `re.search` to find a match anywhere, or add
explicit anchors (`^`, `$`, `\\b`) when you mean them.
"""


# ======================================================================================
# Scenario 2 - Catastrophic backtracking.
# ======================================================================================

_EVIL = re.compile(r"(a+)+$")          # nested quantifier over the same text
_SAFE = re.compile(r"a+$")             # no nesting - linear


def _bad_input(n: int) -> str:
    return "a" * n + "!"               # never matches (trailing '!'): forces full search


def s2_build() -> float:
    start = time.perf_counter()
    _SAFE.match(_bad_input(40))
    return time.perf_counter() - start  # ~microseconds


def s2_break() -> bool:
    n = 22   # each +1 roughly doubles the runtime of the evil pattern
    t0 = time.perf_counter()
    _EVIL.match(_bad_input(n))
    evil_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    _SAFE.match(_bad_input(n))
    safe_ms = (time.perf_counter() - t0) * 1000

    return evil_ms > safe_ms * 50     # exponential vs linear: a huge gap


def s2_fix() -> float:
    start = time.perf_counter()
    _SAFE.match(_bad_input(1000))     # 1000 chars, still instant
    return time.perf_counter() - start


S2_WHY = """
`(a+)+$` can split a run of N `a`s between the inner and outer `+` in
exponentially many ways. On input that ends up NOT matching (a trailing `!`), the
engine must try them all before giving up - so time doubles with each extra
character. `a+$` matches the same strings with no nesting and runs in linear time.
Fixes: remove nested quantifiers, use a more specific pattern, possessive
quantifiers / atomic groups (`(?>...)`, Python 3.11+), or a non-backtracking
engine (`re2`).
"""


# ======================================================================================
# Scenario 3 - Not using a raw string.
# ======================================================================================

def s3_build() -> list[str]:
    return re.findall(r"\bcat\b", "the cat sat, a category, cats")  # raw string


def s3_break() -> list[str]:
    # "\bcat\b" - the \b here is the BACKSPACE character (\x08), not a word boundary.
    pattern = "\bcat\b"
    return re.findall(pattern, "the cat sat, a category, cats")  # [] - never matches


def s3_fix() -> list[str]:
    return re.findall(r"\bcat\b", "the cat sat, a category, cats")


S3_WHY = """
In a normal string literal, `\\b` is an escape for the backspace control
character (0x08); `\\d`, `\\w` etc. are invalid escapes kept literally (with a
SyntaxWarning in modern Python). So `"\\bcat\\b"` is a pattern for
`<backspace>cat<backspace>`, which never matches your text. Raw strings (`r"..."`)
pass the backslashes through untouched, which is what the regex engine needs.
"""


# ======================================================================================
# Scenario 4 - A greedy quantifier grabs too much.
# ======================================================================================

def s4_build() -> list[str]:
    return re.findall(r'"[^"]*"', '"alpha" and "beta"')  # ['"alpha"', '"beta"']


def s4_break() -> list[str]:
    return re.findall(r'".*"', '"alpha" and "beta"')  # ['"alpha" and "beta"'] - one match


def s4_fix() -> list[str]:
    return re.findall(r'"[^"]*"', '"alpha" and "beta"')  # or  r'".*?"'


S4_WHY = """
`.*` is greedy: it consumes as much as it can, then backtracks only enough to let
the rest of the pattern match. `".*"` therefore matches from the first `"` to the
LAST `"`, swallowing the text between the two quoted parts. Use a lazy `.*?`
(stops at the first closing `"`) or, better, a negated character class `[^"]*`
(can't cross a `"` at all - and no backtracking).
"""


SCENARIOS = [
    Scenario("re.match anchors at the start", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Catastrophic backtracking", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Forgetting the raw string", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Greedy quantifier grabs too much", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

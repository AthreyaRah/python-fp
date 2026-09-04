"""Strings, bytes & Unicode - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/06_strings_bytes_unicode/scenarios.py
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness.scenario import Scenario, run_all  # noqa: E402

TEXT = "café ☕ π"  # mix of ASCII, accented, symbol, Greek


# ======================================================================================
# Scenario 1 - Encode with one codec, decode with another.
# ======================================================================================

def s1_build() -> str:
    raw = TEXT.encode("utf-8")
    return raw.decode("utf-8")  # matching codec -> exact round trip


def s1_break() -> str:
    raw = TEXT.encode("utf-8")  # multi-byte sequences for é, coffee cup, pi
    try:
        return raw.decode("ascii")  # wrong codec: ascii is 7-bit only
    except UnicodeDecodeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s1_fix() -> str:
    raw = TEXT.encode("utf-8")
    # In real code: agree on the codec out of band, or prepend a BOM, or sniff.
    return raw.decode("utf-8")


S1_WHY = """
`bytes` carry no record of how they were produced. `decode` just applies the
rule you name. UTF-8 encodes 'é' as two bytes both >= 0x80; ASCII only defines
0x00-0x7F, so it raises on the first such byte. Latin-1 would *not* raise - it
would silently produce mojibake. The encoding is a contract both sides must know.
"""


# ======================================================================================
# Scenario 2 - Truncating UTF-8 bytes to limit "length".
# ======================================================================================

def s2_build() -> str:
    # Limit to 6 CHARACTERS: slice the str, then encode.
    limited = TEXT[:6]
    return limited.encode("utf-8").decode("utf-8")


def s2_break() -> str:
    raw = TEXT.encode("utf-8")
    clipped = raw[:4]  # 4 BYTES - lands in the middle of 'é' (2 bytes)
    try:
        return clipped.decode("utf-8")
    except UnicodeDecodeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> str:
    raw = TEXT.encode("utf-8")
    clipped = raw[:4]
    # Option A: drop the incomplete tail.
    return clipped.decode("utf-8", errors="ignore")


S2_WHY = """
In UTF-8 a code point is 1-4 bytes. Slicing the byte string at an arbitrary
offset can cut a multi-byte character in half; `decode` then finds a lead byte
with no continuation and raises. Slice the `str` (by code points) and encode
after, or decode with an incremental decoder / `errors=` policy.
"""


# ======================================================================================
# Scenario 3 - Comparing strings that look identical but are normalized differently.
# ======================================================================================

def _from_form(name: str) -> str:
    return unicodedata.normalize(name, "café")


def s3_build() -> bool:
    a = _from_form("NFC")
    b = _from_form("NFD")
    return unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)  # True


def s3_break() -> bool:
    a = _from_form("NFC")  # 'é' = U+00E9
    b = _from_form("NFD")  # 'e' + U+0301
    assert a != b, "same on screen, different code points"
    # A membership check against a set built the other way misses.
    allowed = {a}
    return b in allowed  # False


def s3_fix() -> bool:
    norm = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731
    allowed = {norm(_from_form("NFC"))}
    return norm(_from_form("NFD")) in allowed


S3_WHY = """
Unicode lets the same visible text be encoded as different code point sequences
(precomposed 'é' vs 'e' + combining accent). They are unequal to `==`, hash
differently, and have different `len`. Normalise to a canonical form (NFC is the
usual choice) at input, then compare / store / index.
"""


# ======================================================================================
# Scenario 4 - Mixing str and bytes.
# ======================================================================================

def s4_build() -> str:
    payload = b"\x48\x69"  # from a socket
    text = payload.decode("ascii")  # decode at the boundary
    return f"received: {text}"


def s4_break() -> str:
    payload = b"Hi"
    # Forgetting to decode: str() of bytes gives the REPR, not the text.
    line = "received: " + str(payload)
    assert line == "received: b'Hi'", "the literal b'...' leaked into the string"
    return line


def s4_fix() -> str:
    payload = b"Hi"
    return "received: " + payload.decode("ascii")


S4_WHY = """
Python 3 never implicitly converts between `str` and `bytes`: `b"a" + "b"` is a
TypeError, and `str(b"Hi")` returns the string `"b'Hi'"` (its repr) plus a
BytesWarning under `-b`. Always `.decode()` bytes to text (and `.encode()` text
to bytes) explicitly, at the edge of your program.
"""


SCENARIOS = [
    Scenario("Encode utf-8, decode ascii", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Truncating UTF-8 bytes", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Normalization and equality", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Mixing str and bytes", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

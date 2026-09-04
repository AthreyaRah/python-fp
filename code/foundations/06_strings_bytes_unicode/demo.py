"""Strings, bytes & Unicode - the practice snippet.

Run it:  python code/foundations/06_strings_bytes_unicode/demo.py

Mental model:
- `str`   is a sequence of Unicode *code points* (abstract characters).
- `bytes` is a sequence of integers 0..255. Raw octets. No text meaning on
          their own.
- An *encoding* (utf-8, latin-1, utf-16, ...) is the rule that maps between the
  two: `str.encode(codec) -> bytes`, `bytes.decode(codec) -> str`.
- Files and sockets carry bytes. You choose the encoding at that boundary.
"""

from __future__ import annotations

import unicodedata

CAFE = "café"          # 'cafe' + e-acute as one code point (U+00E9)
PI_APPROX = "π ≈ 3.14"  # 'GREEK SMALL LETTER PI', 'ALMOST EQUAL TO'


def code_points_vs_bytes() -> None:
    print("s =", CAFE, "| len(s) =", len(CAFE), "code points")
    for codec in ("utf-8", "latin-1", "utf-16"):
        raw = CAFE.encode(codec)
        print(f"  encode {codec:8} -> {raw!r}  ({len(raw)} bytes)")


def round_trip_needs_matching_codec() -> None:
    raw = PI_APPROX.encode("utf-8")
    print("bytes on the wire:", raw)
    print("decode utf-8 ->", raw.decode("utf-8"))
    try:
        raw.decode("ascii")
    except UnicodeDecodeError as exc:
        print("decode ascii ->", type(exc).__name__, "-", exc)


def characters_have_names_and_numbers() -> None:
    print("ord('A') =", ord("A"), "| chr(97) =", chr(97))
    snowman = "\N{SNOWMAN}"
    print(r"'\N{SNOWMAN}' =", snowman, "| U+%04X" % ord(snowman),
          "|", unicodedata.name(snowman))


def bytes_index_to_int() -> None:
    b = b"ABC"
    print("b[0] =", b[0], "(an int)  | b[:1] =", b[:1], "(bytes)")


def fstring_format_specs() -> None:
    n, x = 1234567, 3.14159
    print(f"{n:_}            <- thousands separator")
    print(f"{x:>10.2f}       <- width 10, 2 decimals, right aligned")
    print(f"{CAFE!r}          <- !r applies repr()")
    print(f"{n=}             <- self-documenting expression")


def normalization() -> None:
    nfc = unicodedata.normalize("NFC", CAFE)
    nfd = unicodedata.normalize("NFD", CAFE)  # 'cafe' + U+0301 combining acute
    print("NFC code points:", [f"U+{ord(c):04X}" for c in nfc])
    print("NFD code points:", [f"U+{ord(c):04X}" for c in nfd])
    print("len:", len(nfc), "vs", len(nfd),
          "| they render identically | nfc == nfd ->", nfc == nfd)
    print("after normalizing both to NFC, equal? ->",
          unicodedata.normalize("NFC", nfc) == unicodedata.normalize("NFC", nfd))


def main() -> None:
    code_points_vs_bytes()
    print()
    round_trip_needs_matching_codec()
    print()
    characters_have_names_and_numbers()
    print()
    bytes_index_to_int()
    print()
    fstring_format_specs()
    print()
    normalization()


if __name__ == "__main__":
    main()

"""Floating point, random & reproducibility - the practice snippet.

Run it:  python code/foundations/31_floating_point_and_random/demo.py

Mental model:
- A `float` is an IEEE-754 64-bit binary fraction: 52 bits of mantissa, ~15-17
  significant decimal digits. Most decimal fractions are not representable, and
  errors ACCUMULATE across operations.
- `round()` uses banker's rounding (round half to EVEN): round(2.5) == 2.
- `random` is a pseudo-random generator (Mersenne Twister). Given the same seed
  it produces the same sequence - that is what makes results reproducible. It is
  NOT cryptographically secure; use `secrets` for tokens/passwords.
"""

from __future__ import annotations

import math
import random
import secrets


def representation_error() -> None:
    print("0.1 + 0.2            =", 0.1 + 0.2)
    print("stored value of 0.1  =", f"{0.1:.20f}")
    print("0.1 + 0.2 == 0.3?    =", 0.1 + 0.2 == 0.3)
    print("math.isclose(...)    =", math.isclose(0.1 + 0.2, 0.3))


def accumulation_error() -> None:
    vals = [1e16, 1.0, -1e16, 1.0, 1.0]     # true sum is 3.0
    total = 0.0
    for v in vals:
        total += v                          # plain += loses a term near 1e16
    print("manual += loop       =", total, "  (a 1.0 was swallowed by 1e16)")
    print("math.fsum            =", math.fsum(vals), "  (compensated - correct)")
    print("built-in sum         =", sum(vals), "  (also compensated since 3.12)")


def rounding() -> None:
    print("round(0.5), round(1.5), round(2.5):", round(0.5), round(1.5), round(2.5))
    print("  ^ round half to EVEN (banker's rounding)")


def reproducible_random() -> None:
    rng = random.Random(42)                       # a dedicated generator
    print("Random(42) first 3:", [rng.randint(1, 100) for _ in range(3)])
    rng2 = random.Random(42)
    print("Random(42) again  :", [rng2.randint(1, 100) for _ in range(3)])


def secure_random() -> None:
    print("secrets.token_hex(8):", f"<{len(secrets.token_hex(8))} hex chars>")
    print("  use `secrets`, never `random`, for anything security-sensitive")


def main() -> None:
    representation_error()
    print()
    accumulation_error()
    print()
    rounding()
    print()
    reproducible_random()
    print()
    secure_random()


if __name__ == "__main__":
    main()

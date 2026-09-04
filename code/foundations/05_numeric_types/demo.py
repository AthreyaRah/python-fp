"""Numeric types: int, float, Decimal, Fraction — the practice snippet.

Run it:  python code/foundations/05_numeric_types/demo.py

Mental model:
- int  : arbitrary precision. Never overflows. Exact.
- float: an IEEE-754 64-bit binary fraction. Fast, fixed size, and CANNOT
         represent most decimal fractions exactly (0.1, 0.2, 0.3, ...).
- Decimal: exact base-10 arithmetic with configurable precision. Use for money.
- Fraction: exact rational numbers (numerator/denominator).
- bool : a subclass of int. True == 1, False == 0.
"""

from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction


def int_never_overflows() -> None:
    big = 2 ** 1000
    print("2**1000 has", len(str(big)), "digits; type is", type(big).__name__)
    print("factorial-ish:", math.prod(range(1, 21)))  # 20! exactly


def float_is_binary() -> None:
    print("0.1 + 0.2      =", 0.1 + 0.2)
    print("0.1 + 0.2 == 0.3 ->", 0.1 + 0.2 == 0.3)
    print("what 0.1 really is:", Decimal(0.1))
    print("math.isclose(0.1+0.2, 0.3) ->", math.isclose(0.1 + 0.2, 0.3))


def decimal_and_fraction_are_exact() -> None:
    print("Decimal('0.1')*3        =", Decimal("0.1") * 3)
    print("Decimal('0.1')*3 == 0.3 ->", Decimal("0.1") * 3 == Decimal("0.3"))
    print("Fraction(1,3)+Fraction(1,6) =", Fraction(1, 3) + Fraction(1, 6))


def floor_division_and_modulo() -> None:
    for a, b in [(7, 2), (-7, 2), (7, -2)]:
        print(f"{a:>3} // {b} = {a // b:>3}   {a:>3} % {b} = {a % b:>3}   "
              f"divmod = {divmod(a, b)}")
    print("note: the sign of a % b follows the divisor b")


def bool_is_an_int() -> None:
    print("isinstance(True, int) ->", isinstance(True, int))
    print("True + True + False   ->", True + True + False)
    print("sum([True, False, True, True]) ->", sum([True, False, True, True]))


def float_specials() -> None:
    nan = float("nan")
    inf = float("inf")
    print("nan == nan ->", nan == nan, " | math.isnan(nan) ->", math.isnan(nan))
    print("inf > 1e308 ->", inf > 1e308, " | 1/inf ->", 1 / inf)


def main() -> None:
    int_never_overflows()
    print()
    float_is_binary()
    print()
    decimal_and_fraction_are_exact()
    print()
    floor_division_and_modulo()
    print()
    bool_is_an_int()
    print()
    float_specials()


if __name__ == "__main__":
    main()

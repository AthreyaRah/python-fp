"""Regular expressions & catastrophic backtracking - the practice snippet.

Run it:  python code/foundations/32_regex/demo.py

Mental model:
- A regex is compiled to a matching engine. Python's `re` uses a BACKTRACKING
  engine: on a mismatch it rewinds and tries other ways to match.
- `re.match` is anchored at the START of the string; `re.search` scans anywhere;
  `re.fullmatch` must consume the whole string.
- `*` `+` `?` are GREEDY (match as much as possible); add `?` to make them LAZY
  (`*?` `+?`).
- Nested quantifiers over the same text (`(a+)+`, `(.*)*`) can make the engine
  explore exponentially many paths on input that ultimately fails - "catastrophic
  backtracking".
- Always write patterns as RAW strings (`r"..."`).
"""

from __future__ import annotations

import re


def match_vs_search_vs_fullmatch() -> None:
    s = "id=123 status=ok"
    print("match(r'\\d+', ...):   ", re.match(r"\d+", s))            # None (not at start)
    print("search(r'\\d+', ...):  ", re.search(r"\d+", s).group())   # '123'
    print("fullmatch(r'\\w+', 'ab'):", re.fullmatch(r"\w+", "ab"))    # matches


def groups() -> None:
    m = re.search(r"(?P<key>\w+)=(?P<value>\w+)", "status=ok")
    print("groupdict:", m.groupdict(), "| group(1):", m.group(1))


def greedy_vs_lazy() -> None:
    text = "<a><b>"
    print("greedy <.*> :", re.findall(r"<.*>", text))     # ['<a><b>']
    print("lazy   <.*?>:", re.findall(r"<.*?>", text))    # ['<a>', '<b>']


def sub_with_callable() -> None:
    text = "prices: 10, 20, 30"
    doubled = re.sub(r"\d+", lambda m: str(int(m.group()) * 2), text)
    print("sub with a function:", doubled)


def verbose_pattern() -> None:
    pattern = re.compile(
        r"""
        (\d{4}) - (\d{2}) - (\d{2})   # year - month - day
        """,
        re.VERBOSE,
    )
    print("re.VERBOSE:", pattern.match("2024-05-01").groups())


def main() -> None:
    match_vs_search_vs_fullmatch()
    print()
    groups()
    print()
    greedy_vs_lazy()
    print()
    sub_with_callable()
    print()
    verbose_pattern()


if __name__ == "__main__":
    main()

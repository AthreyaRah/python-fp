"""The collections module - the practice snippet.

Run it:  python code/foundations/08_the_collections_module/demo.py

`collections` gives you specialised containers built on dict/list so you stop
hand-rolling the same patterns:
- defaultdict : dict that auto-creates a default value for a missing key
- Counter     : dict subclass for tallying, with most_common / arithmetic
- deque       : double-ended queue, O(1) at both ends, optional maxlen
- namedtuple  : a tuple with named fields - a lightweight immutable record
- ChainMap    : a stack of dicts searched in order (layered config)
"""

from __future__ import annotations

from collections import ChainMap, Counter, defaultdict, deque, namedtuple


def grouping_with_defaultdict() -> None:
    people = [("eng", "Ada"), ("data", "Bo"), ("eng", "Cy"), ("data", "Di")]
    groups: dict[str, list[str]] = defaultdict(list)
    for team, name in people:
        groups[team].append(name)   # no "if team not in groups" needed
    print("defaultdict(list):", dict(groups))


def tallying_with_counter() -> None:
    text = "the cache retries the write then the cache flushes the write"
    counts = Counter(text.split())
    print("Counter:", counts)
    print("most_common(2):", counts.most_common(2))
    print("arithmetic:", Counter(a=3, b=1) + Counter(a=1, c=2))


def sliding_window_with_deque() -> None:
    window: deque[int] = deque(maxlen=3)
    seen = []
    for x in range(6):
        window.append(x)
        seen.append(list(window))
    print("deque(maxlen=3) as it fills:", seen)


def records_with_namedtuple() -> None:
    Point = namedtuple("Point", ["x", "y"])
    p = Point(3, 4)
    print("namedtuple:", p, "| p.x =", p.x, "| unpacks:", (lambda a, b: a + b)(*p))
    print("_replace returns a new one:", p._replace(y=10), "| original:", p)


def layered_config_with_chainmap() -> None:
    defaults = {"timeout": 30, "retries": 3, "debug": False}
    env = {"retries": 5}
    cli = {"debug": True}
    cfg = ChainMap(cli, env, defaults)   # searched left -> right
    print("ChainMap resolves:", dict(cfg))
    print("  cfg['retries'] =", cfg["retries"], "(from env)  cfg['timeout'] =",
          cfg["timeout"], "(from defaults)")


def main() -> None:
    grouping_with_defaultdict()
    print()
    tallying_with_counter()
    print()
    sliding_window_with_deque()
    print()
    records_with_namedtuple()
    print()
    layered_config_with_chainmap()


if __name__ == "__main__":
    main()

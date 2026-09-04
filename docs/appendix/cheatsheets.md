<!-- status: authored -->
# Cheat sheets

Fast reference for the patterns you reach for daily. Each links to the topic that
explains *why*.

## Comparison & truthiness

```python
x is None          # singletons only: None, True, False
x == y             # everything else — value equality
if items:          # not  if len(items) > 0
if x is not None:  # not  if x != None
```

`2 == True` is `False` — never `if flag == True:`.
[Names & references](../foundations/02-names-objects-references.md) ·
[Idioms](../foundations/43-idioms-and-anti-patterns.md)

## Mutable default argument

```python
def f(items=None):
    items = [] if items is None else items
```

Dataclass field: `tags: list[str] = field(default_factory=list)`.
[Mutability](../foundations/03-mutability-and-the-default-arg-trap.md)

## Copy

```python
b = a                 # alias — same object
b = a.copy() / a[:]   # shallow — new outer, shared nested
b = copy.deepcopy(a)  # deep — independent all the way down
```

[copy: shallow vs deep](../foundations/41-copy-shallow-vs-deep.md)

## Containers by job

| Need | Use |
|---|---|
| membership test in a loop | `set` / `dict`, not `list` |
| queue (both ends) | `collections.deque` |
| tally | `collections.Counter` |
| group-by | `collections.defaultdict(list)` |
| dedup keeping order | `list(dict.fromkeys(seq))` |
| dict key from several values | `tuple` |
| immutable set member | `frozenset` |

[Containers & complexity](../foundations/07-builtin-containers-and-complexity.md) ·
[collections](../foundations/08-the-collections-module.md)

## Iteration

```python
for x in items                     # not  for i in range(len(items))
for i, x in enumerate(items, 1)    # need the index
for a, b in zip(xs, ys, strict=True)   # two sequences
[f(x) for x in xs if p(x)]         # not  list(map(lambda..., filter(lambda...)))
```

`map` / `filter` / `zip` / generator expressions are one-pass.
[Iterators](../foundations/10-iterators-and-the-iterator-protocol.md) ·
[itertools](../foundations/15-itertools.md)

## Generator expression vs list comp

```python
any(check(x) for x in items)     # lazy: stops at the first hit
sum(x*x for x in big)            # no intermediate list
[x*x for x in xs]                # when you need it more than once
```

[Comprehensions](../foundations/09-comprehensions.md)

## Files

```python
with open(path, encoding="utf-8") as f:   # text: always pass encoding
    for line in f:                        # lazy — one line at a time
        ...
data = Path(path).read_bytes()            # binary
HERE = Path(__file__).resolve().parent    # script-relative, not cwd
path.parent.mkdir(parents=True, exist_ok=True)   # before writing
tmp.write_text(new); os.replace(tmp, target)     # atomic write
```

[File I/O & pathlib](../foundations/28-file-io-and-pathlib.md)

## Exceptions

```python
try:
    ...
except (KeyError, ValueError) as e:   # narrow, never bare `except:`
    raise DomainError("...") from e   # chain the cause
finally:
    ...                              # cleanup only — never `return` here
```

[Exceptions](../foundations/17-exceptions.md)

## Floats & money

```python
math.isclose(a, b)                   # never  a == b
math.isnan(x)                        # never  x == float("nan")
total_cents = 1099                   # money as int minor units
Decimal("19.99")                     # or Decimal, from a string
```

[Numeric types](../foundations/05-numeric-types.md) ·
[Floating point](../foundations/31-floating-point-and-random.md)

## Dates

```python
from datetime import datetime, timezone
now = datetime.now(timezone.utc)              # aware; never datetime.utcnow()
local = now.astimezone(ZoneInfo("Asia/Kolkata"))
datetime.fromisoformat(s)                     # round-trip
```

Work in aware UTC internally; convert at the edges.
[Dates & times](../foundations/30-dates-and-times.md)

## Regex

```python
re.compile(r"...")            # raw string, compile once
re.search(pattern, s)         # not re.match unless you want start-anchoring
r'"[^"]*"'                    # negated class beats  r'".*?"'  beats  r'".*"'
```

Avoid nested quantifiers `(a+)+`.
[Regular expressions](../foundations/32-regex.md)

## Threading a shared counter

```python
from threading import Lock
lock = Lock()
with lock:
    counter += 1              # the whole read-modify-write inside the lock
```

Threads for I/O; `ProcessPoolExecutor` for CPU.
[The GIL](../foundations/33-gil-threads-races.md) ·
[multiprocessing](../foundations/34-multiprocessing-and-futures.md)

## asyncio

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        for u in urls:
            tg.create_task(fetch(u))     # concurrent — not  await fetch(u) in a loop

asyncio.run(main())
await loop.run_in_executor(None, blocking_fn, arg)   # offload blocking calls
```

[asyncio](../foundations/35-asyncio.md)

## Decorators

```python
import functools

def deco(func):
    @functools.wraps(func)               # always
    def wrapper(*args, **kwargs):
        ...
        return func(*args, **kwargs)
    return wrapper                        # always return a callable
```

[Decorators](../foundations/13-decorators.md)

## Classes

```python
@dataclass(frozen=True, slots=True)      # hashable, memory-lean value object
class Point:
    x: int
    y: int

super().__init__(...)                    # in every overridden __init__
self.CONST  /  ClassName.CONST           # class attrs from a method, not bare
```

[Classes & OOP](../foundations/19-classes-and-oop.md) ·
[dataclasses & __slots__](../foundations/21-dataclasses-and-slots.md)

## match

```python
match value:
    case 200 | 201:            ...
    case [cmd, *args]:          ...      # a list — split strings first
    case {"type": t, **rest}:   ...
    case Point(x=0, y=y):       ...      # keyword sub-patterns always work
    case _:                     ...      # catch-all LAST
```

Bare name = capture, not comparison — use literals / dotted names.
[The match statement](../foundations/42-match-statement.md)

## Serialization

```python
json.dumps(obj, default=str)             # for datetimes / Decimals / sets
json.loads(text)                         # keys come back as strings
csv.DictReader(f)                        # every value is a str — convert
# pickle: trusted data only
```

[Serialization](../foundations/29-serialization-stdlib.md)

## subprocess

```python
subprocess.run(["prog", arg1, arg2], capture_output=True, text=True, check=True)
# never shell=True with interpolated input; never skip check=True
```

[stdlib toolkit](../foundations/40-stdlib-toolkit.md)

## Logging

```python
log = logging.getLogger(__name__)        # in every module; no handler
log.info("user %s did %s", uid, action)  # args, not f-strings
log.exception("failed")                  # inside except — attaches the traceback
logging.basicConfig(level=..., force=True)   # once, at startup
```

[Logging](../foundations/39-logging.md)

## Profiling

```python
python -m cProfile -s tottime script.py
timeit.repeat("f(data)", setup="data = build()", number=1000, repeat=5)  # min()
time.perf_counter()                      # never time.time() for timing
```

Fix the algorithm (O(n²)→O(n)) before micro-optimising.
[Profiling](../foundations/37-profiling-and-dis.md)

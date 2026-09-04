<!-- status: authored -->
# "Check yourself" — answers

Answers to the questions at the end of each Foundations topic. Try them first;
each topic's page has the full reasoning.

## 01 · The execution & import model

1. The first `import` runs the module body and caches the module object in
   `sys.modules`. Every later `import` finds it there and never re-reads the
   file. Restart the process to pick up edits (or `importlib.reload`).
2. `__name__` is `"__main__"` in the file you launched; it's the module's dotted
   name in an imported file. The `if __name__ == "__main__":` guard keys off
   this.
3. The connection is opened at module top level, so it fires on first import.
   Move it behind a function (optionally cached) so only code that needs it pays.
4. Whether there's a `json.py` (or a `json/` package) shadowing the stdlib on
   `sys.path` — the script directory / cwd comes first.
5. `-X importtime` shows how long each import took *at startup*, before your
   program's own timeline begins — a runtime profiler can't see import cost that
   already happened.

## 02 · Names, objects & references

1. `a` is still `(1, 2)`. `tuple` has no `__iadd__`, so `b += (3,)` is
   `b = b + (3,)` — a new tuple rebound to `b` only. A `list` *does* mutate in
   place.
2. `[] is []` builds two separate list objects. `a = b = []` binds both names to
   the *same* one object.
3. The third call returns `{0: 1, 1: 1, 2: 1}`. The default `{}` is created once
   at `def` time and stored on `f.__defaults__`; every call without `cache`
   mutates that one dict.
4. Caller side: pass a copy — `f(items[:])` / `f(list(items))`. Callee side:
   don't mutate the argument — build and return a new list.
5. Only for singletons: `x is None`, `x is True`, `x is False`. Everything else
   uses `==`.

## 03 · Mutability & the mutable-default trap

1. Both end at `([1, 1],)`. `a[0].append(1)` mutates the list, no rebinding.
   `a[0] += [1]` runs `list.__iadd__` (extends the list) **then** tries
   `STORE_SUBSCR` into the tuple, which raises `TypeError` — after the mutation
   already happened.
2. A `set` is mutable, so it has no stable `__hash__` and can't be a member of
   another set (or a dict key). `frozenset` is immutable and hashable.
3. The default `{}` is shared across all calls that omit `counts`, so counts
   accumulate globally. Fix: `def tally(word, counts=None): counts = {} if counts
   is None else counts`.
4. `ValueError: mutable default <class 'list'> ... is not allowed`. Use
   `tags: list[str] = field(default_factory=list)`.
5. For immutable constants and defaults shared intentionally across instances
   (`MAX_RETRIES = 3`). Never for per-object mutable state.

## 04 · The data model & dunder methods

1. Python sets `__hash__ = None` on any class that defines `__eq__` but not
   `__hash__`, to preserve `a == b ⇒ hash(a) == hash(b)`. `__lt__` has no such
   invariant, so it's left alone.
2. `__radd__` (or `__add__` handling `other == 0`). `sum` starts at `0`, so it
   needs `0 + obj` to work; `__radd__` should return `self` for `0` and add for
   another `Obj`.
3. Containers, loggers, and the REPL call `repr()` on elements. Defining only
   `__str__` leaves `__repr__` as the default `<Obj object at 0x…>`. `str` falls
   back to `repr`, never the reverse.
4. Its `__hash__` depends on a field you mutated after inserting it — the new
   hash lands in a different bucket, so the lookup misses.
5. `NotImplemented` tells Python "try the other operand's reflected method, then
   raise `TypeError`". `None` is just a value — `a + b` would silently become
   `None`.

## 05 · Numeric types

1. `0.1` and `0.2` have no exact binary representation, so their float sum is
   `0.30000000000000004`. `Decimal` does exact base-10 arithmetic.
2. `-5 // 2 == -3` (floor, toward −∞), `-5 % 2 == 1` (sign follows the divisor).
   The invariant: `a == (a // b) * b + (a % b)`.
3. `x != float("nan")` is `True` for *everything* (NaN compares unequal to all
   values, itself included). Use `math.isnan(x)` or `x != x`.
4. `Decimal(price)` copies the float's *already-inexact* value exactly. Build
   from a string (`Decimal("19.99")`) or keep money as integer cents.
5. When the value is inherently approximate (measurements, scientific data,
   coordinates, ML weights) and you need speed and a fixed size.

## 06 · Strings, bytes & Unicode

1. On whether `é` is one code point (NFC) or `e` + combining accent (NFD).
   Normalise on input: `unicodedata.normalize("NFC", s)`.
2. `str(chunk)` returns the *repr* of the bytes (`"b'...'"`), not the decoded
   text. Do `chunk.decode("utf-8")`.
3. A UTF-8 code point is 1–4 bytes; a byte-offset cut can split one, leaving a
   lead byte with no continuation. Slice the `str`, then encode.
4. One string is NFC and the other NFD — different code point sequences that
   render identically. Normalise both before comparing.
5. `"\xe9"` is a 1-char `str` (code point U+00E9, "é"). `b"\xe9"` is a 1-byte
   `bytes`. `"é"` is the same 1-char `str` as the first (if NFC).

## 07 · list, tuple, dict, set: internals & complexity

1. `x in some_list` (or `list.index`, `del`/`remove` in a loop) — O(n) per call,
   O(n²) over the loop. Swap the list for a `set`/`dict`.
2. Removing from a list you're iterating shifts later elements past the
   iterator's index, so items get skipped. Fix: comprehension/`filter`, or
   iterate `items[:]`.
3. A `tuple` is immutable, so its `__hash__` is stable. A `list` is mutable and
   unhashable by design.
4. `list.pop(0)` is O(n) — every element shifts. `collections.deque` has O(1)
   `append`/`popleft`.
5. No — set iteration order reflects hash values, not insertion. For order-
   preserving dedup use `list(dict.fromkeys(seq))`.

## 08 · The collections module

1. `sessions[u]` on a `defaultdict` runs the factory *and inserts the key* for
   every missing `u`. Use `sessions.get(u)` or `u in sessions` for reads.
2. The `-` operator: it returns a new `Counter` keeping only counts > 0.
   `.subtract()` mutates in place and keeps zeros and negatives.
3. Right when dropping the oldest items is the intended behaviour ("last N",
   ring buffer, sliding window). A data-loss bug when you picked `maxlen` as a
   guessed capacity.
4. `point._replace(x=5)` — returns a new namedtuple.
5. When the layers change often (no dict rebuild) or you need to know *which*
   layer a value came from.

## 09 · Comprehensions & generator expressions

1. The genexp yields one value at a time (constant memory); the list comp builds
   all 10⁷ squares first.
2. Every lambda closes over the one variable `name`; called later, they all read
   its final value. Fix: `lambda name=name:` or `functools.partial`.
3. `[x for cols in table for x in cols]` — the clause defining `cols` must come
   before the one using it.
4. The list comp runs every `check(x)` *before* `any` is called. Drop the
   brackets: `any(check(x) for x in items)` lets `any` stop at the first hit.
5. No, `n` is not accessible — comprehensions have their own scope. After a
   `for` loop, `n` *is* bound (to the last value, or undefined if the iterable
   was empty).

## 10 · Iterators & the iterator protocol

1. `zip` returns a one-pass iterator; the first loop exhausts it. `list(zip(a,
   b))` if you need to reuse it.
2. `x` is an iterator (its `__iter__` returns `self`), not just an iterable —
   it's already being consumed.
3. `__iter__` returned `self` (with shared state) instead of a fresh iterator,
   so nested loops share one cursor.
4. A bare `next(it)` that hits the end inside a generator body — the leaked
   `StopIteration` becomes `RuntimeError` (PEP 479). Use `next(it, default)` or
   `try/except StopIteration: return`.
5. Consume it once and prepend it back: `it = itertools.chain([peeked], it)`.

## 11 · Generators & yield from

1. Calling a generator function returns a paused generator object; the body
   (including the `print`) doesn't run until the first `next()`.
2. In a wrapper. Validation in the generator function itself is deferred to the
   first `next()`, surfacing far from the call.
3. On `gen.close()`, when the generator is fully consumed, or at garbage
   collection — *not* when the caller `break`s. Use
   `contextlib.closing(gen)`.
4. `last` is the last *yielded* value, not the `return` value. Get the return
   with `yield from`, or catch `StopIteration` and read `.value`.
5. `yield from source`.

## 12 · Functions: args/kwargs, closures, nonlocal

1. All three lambdas close over one `i`, read at call time (== 2). Fixes:
   `lambda i=i: i`, or `functools.partial(lambda i: i, i)`.
2. `UnboundLocalError` — `n += 1` makes `n` local for the whole function, and the
   read happens before any assignment. Add `nonlocal n`.
3. When the argument is a boolean or one of several same-typed values a caller
   could pass in the wrong order — `*` forces `name=...` at the call site.
4. `levl` goes into `fields` as `{"levl": "warn"}`; the real `level` isn't set.
   `**kwargs` accepts any keyword with no checking.
5. `5` — the value the closure captured when `make_adder(5)` was called.

## 13 · Decorators

1. `def view(): ...` then `view = app.route("/x")(view)`.
2. Add `@functools.wraps(func)` above the `def wrapper`.
3. `@timed` is a plain decorator: `f = timed(f)`. `@timed()` calls it first,
   expecting it to *return* a decorator. `timed` here is the plain kind.
4. `@require_auth` *above* `@log` keeps unauthorized attempts out of the log
   (auth runs first, rejects before logging). `@log` on top logs them.
5. The decorator runs at `def`/import time, once — not per call.

## 14 · functools

1. The cache holds strong references forever, growing without bound (and pinning
   every `path` string). Set `maxsize=N` or clear it periodically.
2. It computed and stored the value in `instance.__dict__` on first access,
   shadowing the descriptor. Use a plain `@property`, or invalidate with
   `del obj.attr`.
3. An empty iterable with no initializer → `TypeError`. Pass the identity
   element: `reduce(operator.add, items, 0)` (or use `sum`).
4. `partial` prepends positional args, so `partial(json.loads, my_fn)` passes
   `my_fn` as the JSON *string*. Bind by keyword: `partial(json.loads,
   parse_constant=my_fn)`.
5. `__name__`, `__doc__`, `__module__`, `__qualname__`, `__dict__`,
   `__wrapped__`. It goes on the `wrapper` function (as `@functools.wraps(func)`).

## 15 · itertools

1. To sort the data by the same key before `groupby` — it only groups
   *consecutive* equal keys.
2. `list(groupby(...))` walks to the last group marker, dragging the shared
   source iterator past every earlier group. Materialise each group inside the
   same loop: `[(k, list(g)) for k, g in groupby(...)]`.
3. `chain.from_iterable(rows)` (lazy) or `chain(*rows)` (unpacks). `chain(rows)`
   treats `rows` as one iterable to yield.
4. `zip(headers, row, strict=True)` (3.10+) raises on a length mismatch;
   `itertools.zip_longest` fills the gaps.
5. `list(itertools.islice(itertools.count(), 10))`.

## 16 · Scope & namespaces (LEGB)

1. `UnboundLocalError` — the assignment `x = 1` makes `x` local for the whole
   function, so the earlier `print(x)` reads an unassigned local.
2. `return self.TIMEOUT` or `return ClassName.TIMEOUT`. The class body is not an
   enclosing scope for methods.
3. Without `global`: when you only *mutate* the object (`d[k] = v`,
   `d.update(...)`). With `global`: when you *rebind* the name (`d = {}`).
4. `v` is not defined (comprehension scope). After a `for` loop it is bound.
5. It shadows the built-in *for the rest of that scope*, so a later `id(x)` /
   `list(x)` call raises `TypeError: 'int'/'list' object is not callable`.

## 17 · Exceptions: EAFP, chaining, groups

1. It catches your `NameError`/`TypeError`/`AttributeError` too — real bugs get
   swallowed and the program continues with a wrong value.
2. The `return` replaces the in-flight exception, which is silently discarded.
   (Modern Python warns about `return` in `finally`.)
3. `raise B()` shows "During handling of the above exception, another occurred"
   (implicit `__context__`). `raise B() from a` shows "The above exception was
   the direct cause" and sets `__cause__`.
4. One account is debited, the other not — inconsistent. Validate first, compute
   new values without committing, apply last; or wrap the whole operation so a
   failure rolls back (transaction / context manager).
5. EAFP for local "try the fast path, handle the miss" and to avoid check-then-
   act races. LBYL when the check is cheap, has no side effects, and makes the
   code clearer.

## 18 · Context managers & with

1. `with open(p) as f: data = f.read()`. In the original, if `.read()` raises,
   `f.close()` is never reached and the descriptor leaks until GC.
2. When the `with` body raises, the exception is *thrown into* the generator at
   the `yield`; only a `finally` runs the teardown before it propagates.
3. It returned a truthy value, which means "I handled the exception, suppress
   it". Return `False`/`None`.
4. `contextlib.ExitStack` with `stack.enter_context(...)` per file.
5. It wraps a generator, and a generator runs once — a second `__enter__` raises
   `RuntimeError`/`AttributeError`. Call the factory again per `with`.

## 19 · Classes & OOP

1. `seen = set()` is one object on the class; `self.seen.add(x)` *mutates* it, no
   assignment, so every instance shares it. `self.count += 1` *reassigns* — the
   write creates a per-instance `count` shadowing the class one, so the class
   counter never moves.
2. The `self` parameter — `obj.render()` passes `obj` as the first argument.
3. `property` is a data descriptor (`__get__` + `__set__`); its `__set__` with no
   setter raises. Add `@name.setter`, or leave it read-only deliberately.
4. `__new__` creates the instance; `__init__` initialises it in place (and must
   return `None`). Construction that returns something computed → a
   `@classmethod` factory.
5. `@classmethod` for alternative constructors / class-level operations;
   `@staticmethod` rarely (a plain function is usually clearer); a module
   function when it needs neither the class nor an instance.

## 20 · Inheritance, MRO & super()

1. `C` — the next class after `B` in `D`'s MRO (`D, B, C, A, object`). `super()`
   follows the MRO of `type(self)`, not the static base.
2. `super().__init__(...)` in the subclass's `__init__`.
3. The intermediate classes called the base `__init__` directly instead of
   `super().__init__()`, so it ran once per branch.
4. `D` and `E` order two common bases inconsistently (one says X-before-Y, the
   other Y-before-X); C3 can't linearize both.
5. `self.render()` dispatches to the most-derived override immediately — before
   the subclass's `__init__` has set up the state that override depends on.

## 21 · dataclasses & __slots__

1. `ValueError: mutable default ... is not allowed`. Use
   `field(default_factory=list)`.
2. `frozen=True` (makes it immutable and hashable). "Change" one with
   `dataclasses.replace(money, cents=...)`.
3. Generated `__eq__` without `frozen` sets `__hash__ = None`. Fix:
   `frozen=True`.
4. Buys: less memory (no per-instance `__dict__`) and typo-catching (undeclared
   attributes raise). Costs: no ad-hoc attributes, `cached_property` needs the
   name in `__slots__`, multiple-inheritance is fiddly.
5. In `__post_init__(self)`, which runs right after the generated `__init__`.

## 22 · ABCs, Protocols & duck typing

1. Nothing at all (duck typing) — just call `.read()`. Add a `Protocol` if you
   want a static checker to verify callers; an ABC only if you own the
   implementations and want shared behaviour.
2. Implement every `@abstractmethod`. The error is raised at instantiation
   (`MyHandler()`), not at definition.
3. `@runtime_checkable`. It only checks that the method *names* exist — not
   their signatures or types.
4. `list`'s C methods (`__init__`, `extend`, `+=`, slice-assign) write to
   internal storage directly, bypassing your Python `append`. Subclass
   `collections.UserList` / `collections.abc.MutableSequence`.
5. Shared mixin methods, an enforced "you must implement this" at instantiation,
   and `register()` for virtual subclasses.

## 23 · Type hints, typing & mypy

1. Annotations are metadata — the interpreter never checks them. Validate/coerce
   at the trust boundary (`x = float(x)`), or use pydantic.
2. mypy flags `Incompatible default` (a `list[str]` can't be `None`). At runtime
   `items` really is `None`, so `items.append(...)` raises `AttributeError`.
3. `typing.get_type_hints(func)` — it evaluates the string annotations in the
   right namespace.
4. `Optional[str]` means "the *value* is `str` or `None`", not "the argument may
   be omitted". Add `= None`.
5. It statically analyses types and reports mismatches before you run the code;
   `python` never checks annotations.

## 24 · Descriptors

1. A function is a non-data descriptor: `obj.method` calls
   `func.__get__(obj, type)`, which returns a bound method.
2. It stores state on `self` (the one shared descriptor object). Store it in
   `instance.__dict__[self.name]` (name from `__set_name__`) or a
   `WeakKeyDictionary`.
3. A non-data descriptor (`__get__` only) — an instance attribute of the same
   name shadows it. Add `__set__` to make it a data descriptor.
4. `__set_name__(self, owner, name)` tells the descriptor which attribute it is.
   Without it, two descriptors of the same class use one hardcoded storage key
   and clobber each other.
5. When you need the same managed-attribute behaviour (validation, unit
   conversion, lazy loading, ORM fields) across *many* attributes or *many*
   classes.

## 25 · Metaclasses & __init_subclass__

1. `__init_subclass__` — it needs no metaclass, so it composes with `ABC`.
2. `__init_subclass__` must declare `path` (or accept `**kwargs`) and forward
   with `super().__init_subclass__(**kwargs)`.
3. `__init_subclass__` fires for every subclass at every depth, including
   abstract intermediates. Guard with an opt-in class keyword (`register=True`).
4. `class C(Meta)` makes `Meta` a *base class* (so `C` becomes a class factory).
   `class C(metaclass=Meta)` applies `Meta` as the metaclass.
5. `abc.ABCMeta` and `enum.EnumMeta` (also many ORM / serialization frameworks).

## 26 · Modules, packages & circular imports

1. `A` imports a *name* from `B` while `B` imports a name from `A` mid-load.
   Fixes: import the *module* (`import a.b`) and use `a.b.name`; defer the import
   into a function; move the shared code to a third module.
2. Run directly, `__package__` is empty, so `from . import x` has nothing to
   resolve against. `python -m` runs it with a package context.
3. `import *` without `__all__` copies every public name — including `json` that
   the package imported for its own use. Define `__all__`.
4. `import os.path` binds `os`. Call it as `os.path.join(...)`.
5. In the package's `__init__.py` (keep it light).

## 27 · venv, pip, pyproject.toml & wheels

1. `sys.prefix != sys.base_prefix`.
2. You're not in the venv you installed into (wrong `python` on `PATH`), or a
   local file/dir shadows the package on `sys.path`.
3. `tomllib` needs binary mode: `open("pyproject.toml", "rb")`.
4. `tomllib` is a read-only parser (no `dump`). Use `tomli-w` / `tomlkit`, or
   template the string for simple cases.
5. `Pillow`. `importlib.metadata.packages_distributions()["PIL"]` maps the
   import name to its distribution.

## 28 · File I/O & pathlib

1. `data/input.csv` is relative to the cwd, not the script. Build the path from
   `Path(__file__).resolve().parent`.
2. Binary: `path.read_bytes()` / `open(path, "rb")`.
3. Write to a temp file, then `os.replace(tmp, target)` — an atomic rename.
4. `path.parent.mkdir(parents=True, exist_ok=True)` — opening a file for writing
   creates the file, not its directories.
5. `Path("logs").rglob("*.log")` or `glob("**/*.log")` — `glob` is one level
   only.

## 29 · Serialization: json, pickle, csv, struct

1. `json.dumps(obj, default=list)` (or `str`), or convert the set to a list
   before dumping.
2. JSON object keys are always strings, so `2021` round-trips as `"2021"`.
   `{int(k): v for k, v in loaded.items()}` on the way in.
3. Never `pickle.load` untrusted data — the byte stream can name any callable
   for the unpickler to run. Use JSON.
4. `row["amount"]` is a `str`; `sum` of strings concatenates (or `+ 0` raises).
   Convert: `int(row["amount"])`.
5. Byte order isn't portable — `>` (big-endian) or `<` (little-endian) makes the
   file readable on any machine; `@` (native) doesn't.

## 30 · Dates & times

1. One is aware (`datetime.now(timezone.utc)`), one is naive (a parsed or
   `utcnow()` value). Attach a zone to the naive one (`.replace(tzinfo=...)`) or
   parse it as aware.
2. It returns the UTC time but with `tzinfo=None`, so downstream `.timestamp()` /
   comparisons treat it as *local*. Use `datetime.now(timezone.utc)`.
3. Both datetimes share one `ZoneInfo` object, so subtraction uses wall-clock
   fields and ignores the skipped hour. Convert both to UTC first.
4. Naive. `dt.replace(tzinfo=timezone.utc)` (if you know it's UTC) makes it
   aware; parse with `%z` to get an aware result directly.
5. Only if you mean "168 hours of elapsed time". For "the same wall-clock time"
   across a DST change, adjust the date fields or use `dateutil.relativedelta`.

## 31 · Floating point, random & reproducibility

1. Float arithmetic rarely equals a decimal literal. Use
   `assert compute() == pytest.approx(0.3)` (or `math.isclose`).
2. `1e16 + 1` rounds back to `1e16`, so a manual `+=` loop loses the small
   addends; `math.fsum` keeps an exact running correction. (The built-in `sum`
   also compensates since 3.12.)
3. Something else in the process calls `random.*` (shifting the shared
   generator), or you rely on set/dict iteration order across processes
   (string hashing is randomised).
4. `users` has fewer than 5 elements — `sample` is without replacement. Use
   `random.choices(users, k=5)` if repeats are OK, or clamp `k`.
5. Feature — Python rounds half to even (banker's rounding). For "round half up":
   `Decimal("2.5").quantize(Decimal("1"), rounding=ROUND_HALF_UP)`.

## 32 · Regular expressions

1. `re.match` anchors at the start; `"code ABC"` doesn't start with `[A-Z]{3}`.
   Use `re.search`.
2. Nested quantifiers over overlapping text — `(a+)+`, `(\w+)*`, `(.*)*` —
   catastrophic backtracking on non-matching input.
3. `\d` isn't a valid string escape (kept literally, with a warning); worse,
   `\t` *is* the tab character before `re` sees it. Use raw strings: `r"\d"`.
4. `.+` is greedy — it matched from the first `<` to the last `>`. Use `<(.+?)>`
   (lazy) or `<([^>]+)>` (negated class).
5. For parsing structured formats (HTML, JSON, CSV) — use a real parser. And for
   fixed strings — `str` methods are clearer and faster.

## 33 · The GIL, threads & race conditions

1. `counter += 1` is load / add / store — several bytecodes with switch points
   between them. `list.append` is a single bytecode whose C code doesn't release
   the GIL.
2. Check-then-act: two threads both see `"key" not in cache`, both run the init.
   The GIL serialises *bytecodes*, not your *statement*.
3. A single `threading.Lock` around every read-modify-write of the dict (or use a
   structure built for it). A read-often/write-rarely dict still needs the lock
   on writes and any compound read.
4. Deadlock from acquiring the two locks in different orders on different
   threads. Fix: a global lock ordering (always acquire the lower `id()` first).
5. When the work is CPU-bound and splits into independent chunks — separate
   processes each have their own GIL. New cost: pickling args/results and process
   startup.

## 34 · multiprocessing & concurrent.futures

1. CPU-bound Python threads take turns under the GIL. Use `ProcessPoolExecutor`.
2. `lambda` isn't picklable. Use a module-level function, or
   `functools.partial` of one.
3. Each process has its own copy of module globals. Return values from `map` and
   combine in the parent, or use `multiprocessing.Value`/`Manager`/`Queue`.
4. It never called `.result()` (or iterated `as_completed`) on the futures, so
   worker exceptions stayed trapped inside them.
5. `spawn` (Windows/macOS default) re-imports the module in each worker;
   unguarded top-level pool creation then recursively spawns. Linux often uses
   `fork`, which copies the parent instead.

## 35 · asyncio

1. A coroutine is called but never `await`ed / scheduled — the body never runs.
2. A blocking synchronous call (`time.sleep`, `requests.get`, heavy CPU) that
   never yields to the loop, so the tasks run serially.
3. `await asyncio.gather(*(download(u) for u in urls))` — or an
   `asyncio.TaskGroup`.
4. `asyncio.run` stops the loop when `main` returns and cancels leftover tasks.
   Fix: `await` the task, or use `asyncio.TaskGroup`.
5. For CPU-bound work (use processes) or a handful of blocking calls (a
   `ThreadPoolExecutor` is simpler).

## 36 · The memory model & weakref

1. It's in a reference cycle (freed only by `gc.collect()`), or another
   reference still holds it. Confirm with `gc.get_referrers(obj)` /
   `tracemalloc`.
2. Their reference counts never reach zero (they hold each other). Make the
   back-reference a `weakref` so only the downward link is strong.
3. `build_thing()` has no strong reference, so it's freed the instant the
   expression finishes. Bind it to a name first.
4. The dict is a strong reference keyed by user objects, pinning every session
   forever. Use `weakref.WeakKeyDictionary`, or a bounded/TTL cache.
5. `__del__` runs at collection time, not scope exit — deferred in a cycle,
   skipped on hard exit. Use a context manager / explicit `close()`.

## 37 · Profiling: timeit, cProfile, dis

1. The `load_file()` call — `timeit` runs the whole statement `number` times.
   Move it into `setup=`.
2. `globals=locals()` / `globals=globals()`, or
   `setup="from mymodule import my_helper"`.
3. `timeit` disables the cyclic GC during measurement, so allocation-heavy code
   looks faster than in production.
4. They should have profiled (`cProfile`, sort by `tottime`) to find the actual
   hot loop — usually an O(n²) scan — and fixed its complexity, not the
   constants.
5. `tottime` — time spent *in* the function itself, excluding sub-calls.

## 38 · Testing with pytest & hypothesis

1. Shared state — an earlier test mutated a module-level object that `test_b`
   assumes is pristine. Use a fixture.
2. `assert compute() == pytest.approx(0.75)`.
3. It uses `return` instead of `yield`, so there's no teardown — code after the
   `return` is unreachable.
4. Only "the function didn't raise" — nothing about the result being correct.
5. When the correct behaviour is a *property* that must hold for all inputs
   (round-trips, idempotence, invariants), especially for parsers and data
   structures.

## 39 · Logging

1. Something already logged (auto-installing a handler), so `basicConfig` is now
   a no-op. Configure it first thing at startup, or pass `force=True`.
2. The f-string (and `build_payload()`) runs *before* `log.debug` is called.
   Pass args (`log.debug("payload=%s", payload)`) or guard with
   `if log.isEnabledFor(logging.DEBUG):`.
3. `log.exception("save failed")` (or `log.error(..., exc_info=True)`) — attaches
   the traceback.
4. `logger.addHandler(...)` — three times (e.g. on every request / in a function
   that runs repeatedly). Configure handlers once at startup.
5. It steals the application's control over where logs go, and stacks up
   duplicate handlers. A library just does `logging.getLogger(__name__)`.

## 40 · stdlib toolkit: argparse, enum, subprocess

1. `shell=True` runs the string through `/bin/sh`; a filename with `;`/`$()`
   injects commands. Pass a list: `subprocess.run(["convert", infile, outfile])`.
2. `check=True` — `subprocess.run` doesn't raise on a non-zero exit by default.
3. `status` is an `Enum` member, not `"active"`. Compare members (`status is
   Status.ACTIVE`) or use `StrEnum` so `==` a string works.
4. `type=int` on `add_argument("--port", ...)` — argparse values are strings.
5. When the member must *be* its value in JSON, a DB, argparse `choices`, or
   comparisons — otherwise a plain `Enum`.

## 41 · copy: shallow vs deep

1. Yes — `dict.copy()` is shallow, so `new["tags"]` *is* `old["tags"]`.
2. Implement `__deepcopy__(self, memo)` to share (or re-open) the socket and deep-
   copy only the data; or keep the socket out of the object you copy.
3. `deepcopy`'s `memo` (which preserves shared references) lives for one call
   only — two separate calls duplicate the shared `Settings`. Deep-copy the
   whole graph in one call.
4. `copy.copy` on a plain object shallow-copies its `__dict__`, so `b.cache` *is*
   `a.cache`. Use `copy.deepcopy`, or implement `__copy__`.
5. When immutable data (`tuple`, `frozenset`, `frozen` dataclass), a fresh
   rebuild, or copying just the one layer you mutate would be cheaper and
   clearer.

## 42 · The match statement

1. A bare name in a `case` is a *capture* — it always matches and rebinds the
   name. Use a literal (`case 200:`) or a dotted name (`case Status.OK.value:`).
2. An irrefutable pattern (`case _:` / a bare capture) must be **last** — any
   `case` after it is unreachable, which is a `SyntaxError`.
3. `user_input` is a `str`, and sequence patterns exclude `str`/`bytes`. Match
   `user_input.split()`.
4. `Response` needs `__match_args__` for positional sub-patterns (dataclasses /
   NamedTuples have it). Always-safe alternative: keyword patterns —
   `case Response(status=200, body=body):`.
5. When it's one value against a few constants — a plain `if`/`elif` chain or a
   `{value: handler}` dict is clearer.

## 43 · Idioms & anti-patterns

1. `for i, row in enumerate(rows): process(row, i)`.
2. `if user_id is None:` — `not user_id` is also true for `0`.
3. `isinstance(response, dict)` — matches subclasses too.
4. `filter` returns a one-pass iterator; `sum` consumes it, so `list(evens)` is
   `[]`. Use a list comprehension.
5. Default arguments: never a mutable (`[]`, `{}`) — use `None`. `except`: never
   bare (`except:`) — catch a specific type. Iteration: never mutate a list
   while looping it — build a new one.

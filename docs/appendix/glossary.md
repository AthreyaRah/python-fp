<!-- status: authored -->
# Glossary

First-principles definitions of the terms that come up most across the track.
Each links to the topic that develops it.

**Aware / naive datetime** — an *aware* `datetime` has a `tzinfo` and denotes a
real instant; a *naive* one is wall-clock numbers with no zone. Never mix them.
See [Dates & times](../foundations/30-dates-and-times.md).

**Bytecode** — the flat list of stack-machine instructions your source compiles
to, cached as a `.pyc`. The interpreter is the loop that executes it. See
[The execution & import model](../foundations/01-execution-and-import-model.md).

**Capture pattern** — in a `match` `case`, a bare name that always matches and
binds the subject to it. Not a comparison. See
[The match statement](../foundations/42-match-statement.md).

**Catastrophic backtracking** — exponential regex runtime from nested
quantifiers over overlapping text (`(a+)+`) on input that fails to match. See
[Regular expressions](../foundations/32-regex.md).

**Closure** — a nested function together with the enclosing variables it uses.
It captures the *variable* (a cell), not a snapshot. See
[Functions](../foundations/12-functions-args-closures.md).

**Context manager** — an object with `__enter__` / `__exit__`, driven by `with`;
`__exit__` is guaranteed to run. See
[Context managers](../foundations/18-context-managers.md).

**Coroutine** — a function defined with `async def`; calling it returns a paused
coroutine object that the event loop drives at `await` points. See
[asyncio](../foundations/35-asyncio.md).

**Data descriptor** — a class attribute defining `__set__` (or `__delete__`); it
takes priority over the instance `__dict__`. `property` is one. See
[Descriptors](../foundations/24-descriptors.md).

**Deep vs shallow copy** — a shallow copy is a new outer object sharing the
nested ones; a deep copy recursively copies everything. See
[copy: shallow vs deep](../foundations/41-copy-shallow-vs-deep.md).

**Descriptor** — an object customising attribute access via `__get__` /
`__set__` / `__delete__`, living as a class attribute. Methods, `property`,
`classmethod` are all descriptors. See
[Descriptors](../foundations/24-descriptors.md).

**Duck typing** — relying on an object's behaviour (does it have `.read()`?)
rather than its declared type. See
[ABCs, Protocols & duck typing](../foundations/22-abcs-protocols-duck-typing.md).

**Dunder method** — a method with `__name__` underscores that the data model
dispatches to: `__len__`, `__eq__`, `__iter__`, `__enter__`, … See
[The data model & dunder methods](../foundations/04-the-data-model-and-dunders.md).

**EAFP / LBYL** — "easier to ask forgiveness than permission" (try it, catch the
failure) vs "look before you leap" (pre-check). Python favours EAFP. See
[Exceptions](../foundations/17-exceptions.md).

**Event loop** — the single-threaded scheduler that runs `asyncio` coroutines,
switching between them only at `await`. See [asyncio](../foundations/35-asyncio.md).

**Exception chaining** — `raise New() from original` records `original` as
`__cause__`, keeping the root cause in the traceback. See
[Exceptions](../foundations/17-exceptions.md).

**Fixture** — in pytest, a function that supplies test inputs and (if it
`yield`s) runs teardown afterwards. See
[Testing with pytest](../foundations/38-testing-with-pytest.md).

**Garbage collector (cyclic)** — the `gc` module's collector that frees
reference cycles that reference counting can't. See
[The memory model & weakref](../foundations/36-memory-model-and-weakref.md).

**Generator** — a function containing `yield`; calling it returns a paused
iterator. Single-pass. See
[Generators & yield from](../foundations/11-generators-and-yield-from.md).

**GIL (Global Interpreter Lock)** — the CPython lock that lets one thread
execute bytecode at a time; released periodically. Doesn't make code
thread-safe. See [The GIL, threads & race conditions](../foundations/33-gil-threads-races.md).

**Hashable** — an object with a `hash()` that never changes for its lifetime and
that compares equal only to objects with the same hash. Required for dict keys
and set members; implies (effective) immutability. See
[Mutability](../foundations/03-mutability-and-the-default-arg-trap.md).

**Identity (`is`)** — whether two names point at the *same* object (`id()`
equal), as opposed to equal values (`==`). See
[Names, objects & references](../foundations/02-names-objects-references.md).

**Immortal / interned objects** — small ints (−5…256) and some strings that
CPython caches and reuses; an implementation detail, never rely on it with `is`.
See [Names, objects & references](../foundations/02-names-objects-references.md).

**Iterable / iterator** — an *iterable* has `__iter__` returning a fresh
iterator; an *iterator* has `__next__` and holds the position. Iterators are
one-pass. See
[Iterators & the iterator protocol](../foundations/10-iterators-and-the-iterator-protocol.md).

**LEGB** — the name-lookup order: Local, Enclosing, Global, Built-in. See
[Scope & namespaces](../foundations/16-scope-legb.md).

**Metaclass** — the type of a class (default `type`); customises class creation.
Rarely needed — `__init_subclass__` or a class decorator usually suffices. See
[Metaclasses](../foundations/25-metaclasses.md).

**MRO (method resolution order)** — the single linear list of classes (from C3
linearization) that attribute lookup walks. `Cls.__mro__`. See
[Inheritance, MRO & super()](../foundations/20-inheritance-and-mro.md).

**Mutable / immutable** — whether an object's state can change after creation.
`list`, `dict`, `set` mutable; `int`, `str`, `tuple`, `frozenset` immutable. See
[Mutability](../foundations/03-mutability-and-the-default-arg-trap.md).

**`NotImplemented`** — the singleton an arithmetic dunder returns to say "not my
job — try the reflected operation, then raise". Not the same as `NotImplementedError`.
See [The data model & dunder methods](../foundations/04-the-data-model-and-dunders.md).

**Pattern (structural)** — the right-hand side of a `match` `case`: literal,
capture, sequence, mapping, class, or-, guard. See
[The match statement](../foundations/42-match-statement.md).

**Pickle** — Python-specific binary serialization that can execute arbitrary
code on load. Trusted data only. See
[Serialization](../foundations/29-serialization-stdlib.md).

**Race condition** — a bug whose outcome depends on the interleaving of
concurrent operations. See
[The GIL, threads & race conditions](../foundations/33-gil-threads-races.md).

**Reference** — a name bound to an object. Assignment binds a name; it never
copies the object. See
[Names, objects & references](../foundations/02-names-objects-references.md).

**Reference counting** — CPython frees an object the moment its count of
references hits zero. See
[The memory model & weakref](../foundations/36-memory-model-and-weakref.md).

**Sentinel** — a unique marker value (usually `None`, or `object()`) meaning
"not supplied", used instead of a mutable default argument. See
[Mutability](../foundations/03-mutability-and-the-default-arg-trap.md).

**`__slots__`** — a class declaration of the allowed attribute names; removes the
per-instance `__dict__` (less memory) and rejects typos. See
[dataclasses & __slots__](../foundations/21-dataclasses-and-slots.md).

**Type annotation** — metadata (`x: int`) the interpreter stores and ignores; a
static checker (`mypy`) reads it. See
[Type hints, typing & mypy](../foundations/23-type-hints-and-typing.md).

**`weakref`** — a reference that doesn't increase an object's count, so it
doesn't keep the object alive. See
[The memory model & weakref](../foundations/36-memory-model-and-weakref.md).

**WSGI / ASGI** — synchronous / asynchronous web-server-to-application
interfaces. (Beyond this track — the concurrency model behind them is
[asyncio](../foundations/35-asyncio.md) and
[the GIL](../foundations/33-gil-threads-races.md).)

<!-- status: authored -->
# Idioms & anti-patterns

## First principles

"Pythonic" is not a style preference — it means **working with the language's
grain**: truthiness, the iteration protocols, EAFP, unpacking, comprehensions,
and the standard library, instead of translating loops and type checks from C or
Java. Idiomatic code is usually shorter, faster, and less buggy, because the
constructs you're leaning on are the well-tested ones.

This is the capstone: a checklist of the small stuff, each with the failure it
prevents.

| Anti-pattern | Idiom | Why |
|---|---|---|
| `for i in range(len(a)): a[i]` | `for x in a` / `enumerate` / `zip` | no index bookkeeping, no `IndexError` |
| `if len(x) > 0:` / `if x != None:` | `if x:` / `if x is None:` | truthiness; `None` is a singleton |
| `if flag == True:` | `if flag:` | `2 == True` is `False` |
| `type(x) == list` | `isinstance(x, list)` | respects subclasses |
| `s = ""; s += p` in a loop | `"".join(parts)` | clearer; not accidentally O(n²) |
| `d[k] = d.get(k, 0) + 1` | `Counter` / `defaultdict` | intent, not plumbing |
| `list(map(lambda …, filter(lambda …)))` | `[f(x) for x in xs if p(x)]` | readable; and `map`/`filter` are one-pass |
| bare `except:` | `except SpecificError:` | don't swallow bugs / `KeyboardInterrupt` |
| `open()` … `close()` | `with open() as f:` | closes on exception |
| mutate a list while iterating it | build a new list | the iterator's index desyncs |
| `path = dir + "/" + name` | `Path(dir) / name` | cross-platform, real API |

## Practice

```bash
python code/foundations/43_idioms_and_anti_patterns/demo.py
```

```python title="code/foundations/43_idioms_and_anti_patterns/demo.py"
--8<-- "code/foundations/43_idioms_and_anti_patterns/demo.py"
```

## Scenarios

```bash
python code/foundations/43_idioms_and_anti_patterns/scenarios.py
```

### 1 — `range(len(...))` vs `zip`

!!! example "🔨 Build"
    `[f"{k}={v}" for k, v in zip(keys, values, strict=True)]`.

!!! failure "💥 Break"
    `for i in range(len(keys)): keys[i], values[i]` — `values` is one short →
    `IndexError`.

!!! success "🔧 Fix"
    `zip` (stops at the shorter) or `zip(..., strict=True)` (raises on mismatch);
    `enumerate` when you truly need the index.

!!! quote "🧠 Why it behaved that way"
    Indexing re-derives what iteration hands you, and assumes equal lengths.

### 2 — `not value` vs `is None`

!!! example "🔨 Build"
    `price if discount is None else price * (1 - discount)`.

!!! failure "💥 Break"
    `if not discount:` — also true for `0.0`. A caller's explicit "0% discount"
    is treated as "no discount given". The bug hides because non-zero discounts
    still work.

!!! success "🔧 Fix"
    Test `is None` for "argument omitted".

!!! quote "🧠 Why it behaved that way"
    `0`, `0.0`, `""`, `[]`, `False` are all falsy — indistinguishable from
    `None` under `not`.

### 3 — `type() ==` vs `isinstance`

!!! example "🔨 Build"
    `isinstance(v, list)` — matches `list` and its subclasses.

!!! failure "💥 Break"
    `type(v) == list` — a `list` subclass (`Rows`, `UserList`) fails the check
    and isn't handled.

!!! success "🔧 Fix"
    `isinstance` (tuple of types if needed).

!!! quote "🧠 Why it behaved that way"
    `type()` is the exact class; `isinstance` respects the inheritance chain.

### 4 — `map`/`filter` are one-pass

!!! example "🔨 Build"
    `squares = [x*x for x in nums if x % 2 == 0]` — a reusable list;
    `sum` and `max` both work.

!!! failure "💥 Break"
    `squares = map(..., filter(..., nums))`. `sum(squares)` consumes it;
    `list(squares)` is then `[]`.

!!! success "🔧 Fix"
    A comprehension — clearer and reusable.

!!! quote "🧠 Why it behaved that way"
    `map`/`filter` return lazy iterators, exhausted after one pass
    ([Iterators](10-iterators-and-the-iterator-protocol.md)).

## The wider checklist

- **Iterate directly.** `for item in items`. Need the index? `enumerate(items,
  start=1)`. Two sequences? `zip`. Reversed? `reversed`.
- **Truthiness.** `if items:` not `if len(items) != 0:`. `x is None` /
  `x is not None`. Never `== None`, never `== True`.
- **EAFP over LBYL.** `try: … except (KeyError, ValueError):` beats pre-checking —
  and it's race-free ([Exceptions](17-exceptions.md)).
- **Unpacking.** `a, b = b, a`; `first, *rest = seq`; `for k, v in d.items()`;
  `x, y = point`.
- **Comprehensions** for build-a-collection; a **generator expression** when
  feeding one consumer; a real loop when there are side effects or >2 clauses.
- **`str.join`** to assemble strings; **f-strings** to format them.
- **`pathlib`** for paths; **`with`** for every resource;
  **`dataclass`/`NamedTuple`** for records.
- **`collections`** (`Counter`, `defaultdict`, `deque`) and **`itertools`**
  before hand-rolling.
- **`_`** for a value you must bind but won't use.
- **Don't** mutate a collection while iterating it, shadow built-ins, use a
  mutable default argument, catch bare `except`, or compare floats with `==`.
- **Names**: `snake_case` functions/variables, `PascalCase` classes,
  `UPPER_SNAKE` constants, `_private` by convention. Read
  [PEP 8](https://peps.python.org/pep-0008/); run a formatter (`black`/`ruff
  format`) and a linter (`ruff`).

## See also

Every Foundations topic, really — but especially:

- [Names, objects & references](02-names-objects-references.md) · [Mutability](03-mutability-and-the-default-arg-trap.md)
- [Comprehensions](09-comprehensions.md) · [Iterators](10-iterators-and-the-iterator-protocol.md)
- [Exceptions](17-exceptions.md) · [Context managers](18-context-managers.md)
- [list, tuple, dict, set: internals & complexity](07-builtin-containers-and-complexity.md) · [The collections module](08-the-collections-module.md)
- [Type hints, typing & mypy](23-type-hints-and-typing.md) · [Testing with pytest & hypothesis](38-testing-with-pytest.md)

## Check yourself

1. Rewrite `for i in range(len(rows)): process(rows[i], i)` idiomatically.
2. `if not user_id:` rejects a valid `user_id` of `0`. Fix it.
3. `type(response) == dict` fails for a subclass your framework returns. What
   should it be?
4. `evens = filter(...); print(sum(evens)); print(list(evens))` prints a number
   then `[]`. Why?
5. Name three things you should *never* do: with default arguments, with `except`,
   and while iterating a list.

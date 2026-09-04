"""Deterministic synthetic datasets shared across topic demos.

Import the piece you need:

    from _harness.dummydata import people_rows, write_people_csv

Every function is seeded and side-effect-free unless it takes a `path`.
Standard library only - no third-party dependencies anywhere in this package.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import random
import sqlite3
from pathlib import Path

FIRST_NAMES = [
    "Ada",
    "Grace",
    "Alan",
    "Linus",
    "Katherine",
    "Dennis",
    "Barbara",
    "Guido",
    "Radia",
    "Ken",
    "Margaret",
    "Tim",
    "Shafi",
    "Bjarne",
    "Frances",
    "Edsger",
]
LAST_NAMES = [
    "Lovelace",
    "Hopper",
    "Turing",
    "Torvalds",
    "Johnson",
    "Ritchie",
    "Liskov",
    "van Rossum",
    "Perlman",
    "Thompson",
    "Hamilton",
    "Berners-Lee",
    "Goldwasser",
]
CITIES = ["London", "Lagos", "Chennai", "Berlin", "Toronto", "Nairobi", "Osaka", "Lima"]
DEPARTMENTS = ["Engineering", "Data", "Design", "Sales", "Support", "Ops"]


# --------------------------------------------------------------------------------------
# People: the canonical small tabular dataset (CSV / list-of-dict).
# --------------------------------------------------------------------------------------


def people_rows(n: int = 20, seed: int = 0) -> list[dict[str, object]]:
    """A list of dict rows: id, name, age, city, department, salary, hired_on."""
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    for i in range(1, n + 1):
        hired = dt.date(2018, 1, 1) + dt.timedelta(days=rng.randint(0, 2500))
        rows.append(
            {
                "id": i,
                "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "age": rng.randint(21, 63),
                "city": rng.choice(CITIES),
                "department": rng.choice(DEPARTMENTS),
                "salary": rng.randrange(45_000, 180_000, 500),
                "hired_on": hired.isoformat(),
            }
        )
    return rows


def write_people_csv(
    path: str | Path,
    n: int = 20,
    seed: int = 0,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8",
    include_header: bool = True,
) -> Path:
    """Write the people dataset to a CSV file and return its Path."""
    path = Path(path)
    rows = people_rows(n, seed)
    with path.open("w", newline="", encoding=encoding) as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=delimiter)
        if include_header:
            writer.writeheader()
        writer.writerows(rows)
    return path


# --------------------------------------------------------------------------------------
# Events: append-only JSON Lines, for streaming / log / ETL demos.
# --------------------------------------------------------------------------------------


def event_rows(n: int = 100, seed: int = 0) -> list[dict[str, object]]:
    rng = random.Random(seed)
    kinds = ["view", "click", "add_to_cart", "purchase", "logout"]
    start = dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)
    out = []
    for i in range(n):
        ts = start + dt.timedelta(seconds=rng.randint(0, 86_400 * 7))
        out.append(
            {
                "event_id": i,
                "user_id": rng.randint(1, 25),
                "kind": rng.choices(kinds, weights=[50, 30, 10, 5, 5])[0],
                "ts": ts.isoformat(),
                "amount": round(rng.uniform(5, 250), 2) if rng.random() < 0.1 else None,
            }
        )
    return sorted(out, key=lambda r: str(r["ts"]))


def write_events_jsonl(path: str | Path, n: int = 100, seed: int = 0) -> Path:
    path = Path(path)
    with path.open("w", encoding="utf-8") as fh:
        for row in event_rows(n, seed):
            fh.write(json.dumps(row) + "\n")
    return path


# --------------------------------------------------------------------------------------
# A tiny relational shop, for SQL / DB-API / ORM demos.
# --------------------------------------------------------------------------------------


def build_shop_db(path: str | Path = ":memory:", seed: int = 0) -> sqlite3.Connection:
    """Create and populate customers / products / orders. Returns an open connection."""
    rng = random.Random(seed)
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
        CREATE TABLE products  (id INTEGER PRIMARY KEY, title TEXT, price_cents INTEGER);
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            product_id  INTEGER REFERENCES products(id),
            qty INTEGER,
            ordered_on TEXT
        );
        """
    )
    customers = [
        (i, f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}", rng.choice(CITIES))
        for i in range(1, 13)
    ]
    products = [(i, f"Widget {chr(64 + i)}", rng.randrange(500, 9900, 100)) for i in range(1, 9)]
    conn.executemany("INSERT INTO customers VALUES (?,?,?)", customers)
    conn.executemany("INSERT INTO products VALUES (?,?,?)", products)
    orders = []
    for oid in range(1, 61):
        day = dt.date(2024, 1, 1) + dt.timedelta(days=rng.randint(0, 300))
        orders.append(
            (oid, rng.randint(1, 12), rng.randint(1, 8), rng.randint(1, 5), day.isoformat())
        )
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)
    conn.commit()
    return conn


# --------------------------------------------------------------------------------------
# Text corpus, for regex / NLP / embeddings / RAG demos.
# --------------------------------------------------------------------------------------


def text_documents(n: int = 12, seed: int = 0) -> list[str]:
    rng = random.Random(seed)
    subjects = [
        "The cache",
        "A retry",
        "The event loop",
        "This index",
        "The parser",
        "Our pipeline",
        "The GIL",
        "A dataclass",
        "The scheduler",
        "This buffer",
    ]
    verbs = [
        "drops",
        "retries",
        "flushes",
        "blocks",
        "serializes",
        "batches",
        "deduplicates",
        "rehashes",
        "streams",
        "partitions",
    ]
    objects = [
        "the request",
        "stale rows",
        "every message",
        "the connection",
        "the payload",
        "pending work",
        "the write",
        "each record",
    ]
    tails = [
        "under load.",
        "after a timeout.",
        "on shutdown.",
        "once per second.",
        "when the queue is full.",
        "without a lock.",
    ]
    return [
        " ".join(rng.choice(part) for part in (subjects, verbs, objects, tails)) for _ in range(n)
    ]


# --------------------------------------------------------------------------------------
# A simple numeric series, for statistics / random / floating-point demos.
# --------------------------------------------------------------------------------------


def noisy_series(n: int = 200, slope: float = 0.5, noise: float = 3.0, seed: int = 0):
    """(xs, ys) lists: ys = slope*x + intercept + gaussian noise. Standard library only."""
    rng = random.Random(seed)
    xs = list(range(n))
    ys = [slope * x + 10 + rng.gauss(0, noise) for x in xs]
    return xs, ys

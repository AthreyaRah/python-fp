"""File I/O & pathlib - the practice snippet.

Run it:  python code/foundations/28_file_io_and_pathlib/demo.py

Mental model:
- `open(path, mode, encoding=...)` returns a file object. TEXT mode ('r'/'w')
  yields `str`, decoding bytes with `encoding` and translating newlines. BINARY
  mode ('rb'/'wb') yields `bytes`, untouched.
- Iterating a file yields lines lazily - one at a time, not the whole file.
- A relative path is resolved against the current working directory, NOT the
  script's location. Anchor to `Path(__file__).parent` for files next to code.
- `pathlib.Path` is the modern API: `/` to join, `.read_text()`, `.glob()`,
  `.stem`, `.suffix`, `.parent`, `.with_suffix()`, `.resolve()`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402


def path_parts() -> None:
    p = Path("reports/2024/summary.csv")
    print("name:", p.name, "| stem:", p.stem, "| suffix:", p.suffix)
    print("parent:", p.parent, "| parts:", p.parts)
    print("with_suffix('.parquet'):", p.with_suffix(".parquet"))
    print("join with /:", Path("data") / "raw" / p.name)


def read_write_text() -> None:
    d = generated_dir("fileio_demo")
    f = d / "note.txt"
    f.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")
    print("read_text ->", repr(f.read_text(encoding="utf-8")))
    with f.open(encoding="utf-8") as fh:
        print("line by line:", [line.rstrip("\n") for line in fh])  # lazy iteration


def script_relative_paths() -> None:
    here = Path(__file__).resolve().parent
    print("this script's dir:", here.name)
    print("sibling file would be:", (here / "demo.py").exists())


def globbing() -> None:
    d = generated_dir("fileio_glob")
    (d / "sub").mkdir(exist_ok=True)
    for rel in ("a.txt", "b.log", "sub/c.txt", "sub/d.txt"):
        (d / rel).write_text("x", encoding="utf-8")
    print("glob('*.txt')      :", sorted(p.name for p in d.glob("*.txt")))
    print("rglob('*.txt')     :", sorted(p.name for p in d.rglob("*.txt")))


def text_vs_binary() -> None:
    d = generated_dir("fileio_demo")
    raw = b"col1\tcol2\r\n\x00\x01\x02payload"
    (d / "blob.bin").write_bytes(raw)
    back = (d / "blob.bin").read_bytes()
    print("binary round-trips exactly:", back == raw)


def main() -> None:
    path_parts()
    print()
    read_write_text()
    print()
    script_relative_paths()
    print()
    globbing()
    print()
    text_vs_binary()


if __name__ == "__main__":
    main()

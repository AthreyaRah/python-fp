"""File I/O & pathlib - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/28_file_io_and_pathlib/scenarios.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

OUT = generated_dir("fileio_scenarios")
HERE = Path(__file__).resolve().parent


# ======================================================================================
# Scenario 1 - Relative path resolved against the cwd, not the script.
# ======================================================================================

def _make_sibling() -> None:
    # A data file that lives next to this scenarios.py (in the scratch dir here).
    (OUT / "config.ini").write_text("[app]\nname = demo\n", encoding="utf-8")


def s1_build() -> str:
    _make_sibling()
    path = OUT / "config.ini"          # absolute, anchored - works from anywhere
    return path.read_text(encoding="utf-8").splitlines()[0]


def s1_break() -> str:
    _make_sibling()
    old = os.getcwd()
    os.chdir(HERE)                      # simulate "run from a different directory"
    try:
        return open("config.ini").read()   # relative -> looked for in the new cwd
    except FileNotFoundError as exc:
        return f"{type(exc).__name__}: {Path(exc.filename).name}"
    finally:
        os.chdir(old)


def s1_fix() -> str:
    _make_sibling()
    base = OUT                          # anchor to a known location, not the cwd
    return (base / "config.ini").read_text(encoding="utf-8").splitlines()[0]


S1_WHY = """
`open("config.ini")` asks the OS for `config.ini` relative to the process's
CURRENT WORKING DIRECTORY - which is wherever the user launched Python, not where
your script lives. Run the program from another folder and the file isn't found.
Build paths from a fixed anchor: `Path(__file__).resolve().parent / "config.ini"`
for files shipped with the code, or an explicit configured directory for data.
"""


# ======================================================================================
# Scenario 2 - Opening a binary file in text mode.
# ======================================================================================

def _make_blob() -> Path:
    p = OUT / "image.bin"
    p.write_bytes(bytes(range(256)) + b"\r\n" + b"\xff\xfe\x00")
    return p


def s2_build() -> bool:
    p = _make_blob()
    data = p.read_bytes()              # binary mode -> exact bytes
    return data == bytes(range(256)) + b"\r\n" + b"\xff\xfe\x00"


def s2_break() -> str:
    p = _make_blob()
    try:
        return p.read_text(encoding="utf-8")   # text mode on binary data
    except UnicodeDecodeError as exc:
        return f"{type(exc).__name__}: {exc}"


def s2_fix() -> bool:
    p = _make_blob()
    return len(p.read_bytes()) == 256 + 2 + 3


S2_WHY = """
Text mode decodes bytes with an encoding and translates newlines
(`\\r\\n` <-> `\\n`). Arbitrary binary content contains byte sequences that are
not valid UTF-8 (`0x80`+), so `read_text` raises `UnicodeDecodeError`; and even
when it doesn't, newline translation silently corrupts the data. Read/write
binary files in binary mode ('rb'/'wb', or `read_bytes`/`write_bytes`).
"""


# ======================================================================================
# Scenario 3 - A non-atomic write leaves a truncated file on failure.
# ======================================================================================

def _serialize(rows: list[str], fail_after: int | None = None) -> str:
    text = ""
    for i, row in enumerate(rows):
        if fail_after is not None and i == fail_after:
            raise RuntimeError("crash mid-serialize")
        text += row + "\n"
    return text


def s3_build() -> str:
    target = OUT / "atomic.txt"
    target.write_text("old contents\n", encoding="utf-8")
    tmp = target.with_suffix(".tmp")
    try:
        tmp.write_text(_serialize(["a", "b"], fail_after=1), encoding="utf-8")
        os.replace(tmp, target)                 # atomic swap - never runs on failure
    except RuntimeError:
        tmp.unlink(missing_ok=True)
    return target.read_text(encoding="utf-8")   # 'old contents\n' - intact


def s3_break() -> str:
    target = OUT / "direct.txt"
    target.write_text("old contents\n", encoding="utf-8")
    try:
        with target.open("w", encoding="utf-8") as fh:   # TRUNCATES immediately
            fh.write("new line a\n")
            raise RuntimeError("crash mid-write")
            fh.write("new line b\n")
    except RuntimeError:
        pass
    # The old contents are gone and the new data is incomplete.
    return target.read_text(encoding="utf-8")  # 'new line a\n'


def s3_fix() -> str:
    target = OUT / "atomic2.txt"
    target.write_text("old contents\n", encoding="utf-8")
    tmp = target.with_suffix(".tmp")
    try:
        tmp.write_text(_serialize(["x", "y", "z"]), encoding="utf-8")
        os.replace(tmp, target)
    except RuntimeError:
        tmp.unlink(missing_ok=True)
    return target.read_text(encoding="utf-8")  # 'x\ny\nz\n'


S3_WHY = """
`open(path, "w")` truncates the file to zero length the moment it opens - before
you've written anything. Crash between the truncate and the last write and you're
left with a partial file and no original. The atomic pattern: write the full new
content to a temporary file in the same directory, then `os.replace(tmp, target)`,
which swaps the name in one indivisible operation. Readers see either the old file
or the complete new one, never a half.
"""


# ======================================================================================
# Scenario 4 - Writing into a directory that doesn't exist.
# ======================================================================================

def s4_build() -> bool:
    path = OUT / "nested" / "deep" / "out.txt"
    path.parent.mkdir(parents=True, exist_ok=True)   # ensure the tree exists
    path.write_text("ok", encoding="utf-8")
    return path.exists()


def s4_break() -> str:
    path = OUT / "missing_dir" / "out.txt"
    # (make sure it really is missing)
    if path.parent.exists():
        for f in path.parent.iterdir():
            f.unlink()
        path.parent.rmdir()
    try:
        path.write_text("ok", encoding="utf-8")
    except FileNotFoundError as exc:
        return f"{type(exc).__name__}: {exc.strerror}"
    return "no error (unexpected)"


def s4_fix() -> bool:
    path = OUT / "made_dir" / "out.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("ok", encoding="utf-8")
    return path.read_text(encoding="utf-8") == "ok"


S4_WHY = """
`open(path, "w")` / `write_text` create the FILE but not any missing parent
directories - the OS returns `FileNotFoundError: No such file or directory` for
the containing folder. Create the tree first with
`path.parent.mkdir(parents=True, exist_ok=True)` (`parents` makes intermediate
dirs, `exist_ok` makes it idempotent).
"""


SCENARIOS = [
    Scenario("Relative path vs the cwd", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("Binary file in text mode", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Non-atomic write", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("Parent directory missing", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

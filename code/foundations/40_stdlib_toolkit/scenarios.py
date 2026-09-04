"""stdlib toolkit - four Build -> Break -> Fix -> Understand scenarios.

Run it:  python code/foundations/40_stdlib_toolkit/scenarios.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from enum import Enum, StrEnum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _harness import generated_dir  # noqa: E402
from _harness.scenario import Scenario, run_all  # noqa: E402

OUT = generated_dir("toolkit_scenarios")


# ======================================================================================
# Scenario 1 - subprocess with shell=True and interpolated input.
# ======================================================================================

def _target_file() -> Path:
    p = OUT / "data.txt"
    p.write_text("real contents\n", encoding="utf-8")
    return p


def s1_build() -> str:
    path = _target_file()
    hostile_name = str(path)                     # even a weird name is safe as one arg
    out = subprocess.run(
        [sys.executable, "-c", "import sys; print(open(sys.argv[1]).read().strip())",
         hostile_name],
        capture_output=True, text=True,
    )
    return out.stdout.strip()  # "real contents"


def s1_break() -> str:
    _target_file()
    marker = OUT / "PWNED"
    marker.unlink(missing_ok=True)
    # A user-supplied "name" carrying a shell command. With shell=True, sh runs it.
    tainted = f'; {sys.executable} -c "open(r\'{marker}\', \'w\').close()"'
    subprocess.run(
        f"echo processing {tainted}",
        shell=True, capture_output=True, text=True,
    )
    return "injected command executed" if marker.exists() else "no injection"


def s1_fix() -> str:
    path = _target_file()
    out = subprocess.run(
        [sys.executable, "-c", "import sys; print(open(sys.argv[1]).read().strip())",
         str(path)],
        capture_output=True, text=True,
    )
    return out.stdout.strip()


S1_WHY = """
`shell=True` hands your string to `/bin/sh`, which interprets `;`, `&&`, `|`,
`$()`, globs and quotes. Interpolating any external value (a filename, a user
input) into that string is a command-injection vulnerability. Pass a LIST of
arguments and no shell: `subprocess.run([prog, arg1, arg2])` - each element is a
literal argument, never parsed.
"""


# ======================================================================================
# Scenario 2 - subprocess.run without check=True.
# ======================================================================================

def s2_build() -> str:
    r = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stderr.write('nope'); sys.exit(1)"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout


def s2_break() -> str:
    r = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stderr.write('nope'); sys.exit(1)"],
        capture_output=True, text=True,
    )
    # No exception. The caller happily proceeds with empty stdout.
    return f"returncode={r.returncode}, stdout={r.stdout!r}, code continued"


def s2_fix() -> str:
    try:
        subprocess.run(
            [sys.executable, "-c", "import sys; sys.exit(1)"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as exc:
        return f"CalledProcessError: exit {exc.returncode}"
    return "unexpectedly succeeded"


S2_WHY = """
`subprocess.run` does NOT raise on a non-zero exit by default - it returns a
`CompletedProcess` and your code sails on with whatever (often empty) output the
failed command produced. Pass `check=True` to get a `CalledProcessError` (which
carries `returncode`, `stdout`, `stderr`), or inspect `result.returncode`
yourself.
"""


# ======================================================================================
# Scenario 3 - Enum members are not equal to their values.
# ======================================================================================

class RolePlain(Enum):
    ADMIN = "admin"
    USER = "user"


class RoleStr(StrEnum):        # 3.11+: members ARE strings
    ADMIN = "admin"
    USER = "user"


def _is_admin_by_value(role) -> bool:
    return role == "admin"


def s3_build() -> bool:
    return _is_admin_by_value(RoleStr.ADMIN) and (RolePlain.ADMIN is RolePlain.ADMIN)


def s3_break() -> bool:
    role = RolePlain.ADMIN
    # A stringly-typed check against a plain Enum member: always False.
    return _is_admin_by_value(role) is False and role.value == "admin"


def s3_fix() -> bool:
    role = RolePlain.ADMIN
    by_identity = role is RolePlain.ADMIN
    by_value = role.value == "admin"
    str_enum_ok = _is_admin_by_value(RoleStr.ADMIN)
    return by_identity and by_value and str_enum_ok


S3_WHY = """
A plain `Enum` member is its own object - `RolePlain.ADMIN == "admin"` is False
and `RolePlain.ADMIN == 1` is False. Compare members to members (`role is
RolePlain.ADMIN`), compare `role.value` if you need the raw value, or subclass
`StrEnum` / `IntEnum` so the members ARE strings / ints and value comparisons
work (with the caveat that `IntEnum` members from different enums collide when
the ints match).
"""


# ======================================================================================
# Scenario 4 - argparse values are strings unless you pass type=.
# ======================================================================================

def _parser(with_type: bool) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    if with_type:
        p.add_argument("--count", type=int, default=1)
    else:
        p.add_argument("--count", default=1)
    return p


def s4_build() -> int:
    args = _parser(with_type=True).parse_args(["--count", "5"])
    return args.count * 2  # 10


def s4_break() -> str:
    args = _parser(with_type=False).parse_args(["--count", "5"])
    # args.count is the string "5"; "5" * 2 is "55".
    return args.count * 2


def s4_fix() -> int:
    args = _parser(with_type=True).parse_args(["--count", "5"])
    return args.count * 2


S4_WHY = """
Everything argparse reads from the command line is a string. Without `type=int`
(or `type=float`, `type=Path`, a custom callable), `args.count` is `"5"` and
`"5" * 2` is `"55"`. Note `default=1` is used as-is (not passed through `type`)
when the flag is absent - so pass a default of the right type too.
"""


SCENARIOS = [
    Scenario("shell=True command injection", s1_build, s1_break, s1_fix, S1_WHY),
    Scenario("subprocess.run without check=True", s2_build, s2_break, s2_fix, S2_WHY),
    Scenario("Enum member != its value", s3_build, s3_break, s3_fix, S3_WHY),
    Scenario("argparse values are strings", s4_build, s4_break, s4_fix, S4_WHY),
]


def main() -> None:
    run_all(SCENARIOS)


if __name__ == "__main__":
    main()

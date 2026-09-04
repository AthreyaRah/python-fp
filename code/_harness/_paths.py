"""Where demos put the throwaway files they generate."""

from __future__ import annotations

import tempfile
from pathlib import Path


def generated_dir(name: str) -> Path:
    """Return a writable scratch directory for a demo to drop files into.

    Uses ``<repo>/_generated/<name>`` when the repo is writable (handy: you can
    open the files and look at them), otherwise a temp dir. The location is
    git-ignored.
    """
    repo_root = Path(__file__).resolve().parents[2]
    candidate = repo_root / "_generated" / name
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        probe = candidate / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return candidate
    except OSError:
        tmp = Path(tempfile.gettempdir()) / "python-fp" / name
        tmp.mkdir(parents=True, exist_ok=True)
        return tmp

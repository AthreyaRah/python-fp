"""Shared, deterministic dummy-data synthesizers for every topic demo.

Nothing here reaches the network or reads real data. Every generator takes a
`seed` and is reproducible. Heavy third-party imports (pandas, numpy) live
*inside* the functions that need them so the stdlib-only Foundations track can
import this package freely.
"""

from ._paths import generated_dir

__all__ = ["generated_dir"]

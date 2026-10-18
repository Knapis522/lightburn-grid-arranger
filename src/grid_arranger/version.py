"""Jediný zdroj čísla verze aplikace (spec. kap. 30.3).

Verze aplikace je nezávislá na verzi specifikace. Hodnota je PEP 440
kompatibilní (``0.1.0a1``); pro GUI, název ZIPu, Git tag a release notes se
použije SemVer z `display_version()` (``0.1.0-alpha.1``).
"""

from __future__ import annotations

import re

__version__ = "0.1.0a4"

_PRE = {"a": "alpha", "b": "beta", "rc": "rc"}


def display_version(version: str = __version__) -> str:
    """PEP 440 → SemVer: ``0.1.0a1`` → ``0.1.0-alpha.1``, ``0.1.0.dev0`` → ``0.1.0-dev``."""
    m = re.fullmatch(r"(\d+\.\d+\.\d+)(?:(a|b|rc)(\d+))?(\.dev\d*)?", version)
    if not m:
        raise ValueError(f"unsupported version {version!r}")
    base, pre, num, dev = m.groups()
    out = base + (f"-{_PRE[pre]}.{num}" if pre else "")
    return out + ("-dev" if dev and not pre else ".dev" if dev else "")

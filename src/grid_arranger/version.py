"""Jediný zdroj čísla verze aplikace (spec. kap. 30.3).

Verze aplikace je nezávislá na verzi specifikace. Hodnota je PEP 440
kompatibilní; pro zobrazení uživateli se použije `display_version()`.
"""

__version__ = "0.1.0.dev0"


def display_version() -> str:
    """Verze ve tvaru SemVer pro GUI a release notes (např. ``0.1.0-dev``)."""
    base, _, suffix = __version__.partition(".dev")
    return f"{base}-dev" if _ else base

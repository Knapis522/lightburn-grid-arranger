"""Kontrola překladových katalogů ``.ts`` (T-I18N-14, 15; spec. kap. 36.3, 36.5).

Bez závislosti na Qt — použitelné v testech i v sestavení.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

_PLACEHOLDER = re.compile(r"\{[a-z_]+\}|%n|%\d")


def placeholders(text: str) -> set[str]:
    return set(_PLACEHOLDER.findall(text or ""))


def check_catalog(path: Path, require_complete: bool) -> list[str]:
    """Vrátí seznam problémů: chybějící překlad (je-li povinný), nesoulad zástupných symbolů."""
    problems: list[str] = []
    root = ET.parse(path).getroot()
    for ctx in root.findall("context"):
        cname = ctx.findtext("name")
        for m in ctx.findall("message"):
            src = m.findtext("source") or ""
            tr = m.find("translation")
            if tr is None or tr.get("type") == "obsolete" or tr.get("type") == "vanished":
                continue
            unfinished = tr.get("type") == "unfinished"
            if m.get("numerus") == "yes":
                forms = [f.text or "" for f in tr.findall("numerusform")]
                if not forms or any(not f for f in forms):
                    problems.append(f"[{cname}] chybí tvary množného čísla: {src!r}")
                    continue
                texts = forms
            else:
                if unfinished or not (tr.text or "").strip():
                    if require_complete:
                        problems.append(f"[{cname}] chybí překlad: {src!r}")
                    continue
                texts = [tr.text]
            want = placeholders(src)
            for t in texts:
                if placeholders(t) != want:
                    problems.append(f"[{cname}] nesouhlasí zástupné symboly {sorted(want)} v {t!r}")
    return problems

"""Regresní testy na reálných projektech uložených MIMO Git (spec. kap. 30.2).

Spustí se jen s proměnnou prostředí ``GRID_ARRANGER_REAL_DATA`` = složka se soubory,
např. ``..\\lightburn-grid-arranger-data``. Bez ní se přeskočí (CI, cizí počítač).
Originály se nikdy nemění; výstupy jdou do dočasné složky.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, run

DATA = os.environ.get("GRID_ARRANGER_REAL_DATA")
pytestmark = pytest.mark.skipif(not DATA, reason="GRID_ARRANGER_REAL_DATA není nastaveno")

V001_SHA = "d83c49cd535960af12dffd767ac3bb3b42ba10374aea8fe87ecbb2529780b951"
V001_WIDTHS = sorted([187.5, 187.5, 213.533, 196.798, 187.5, 200.21, 200.21, 187.5, 187.5])


def _sources() -> list[Path]:
    return sorted(p for p in Path(DATA).glob("*.lbrn2") if "__grid_" not in p.name)


def _by_sha(sha: str) -> list[Path]:
    return [p for p in _sources() if hashlib.sha256(p.read_bytes()).hexdigest() == sha]


def test_every_real_project_loads_or_fails_cleanly():
    for p in _sources():
        proj = load_project(p)  # GridError by test shodil s čitelným kódem
        assert proj.items, p.name


def test_v001_nine_cards_supported():
    files = _by_sha(V001_SHA)
    if not files:
        pytest.skip("vzorek V-001 není ve složce")
    proj = load_project(files[0])
    assert proj.info.orientation.origin == "top_right"
    assert all(it.supported for it in proj.items) and len(proj.items) == 9
    widths = sorted(round(it.file_bbox[2] - it.file_bbox[0], 3) for it in proj.items)
    assert widths == V001_WIDTHS


def test_v001_arrange_roundtrip(tmp_path):
    files = _by_sha(V001_SHA)
    if not files:
        pytest.skip("vzorek V-001 není ve složce")
    before = hashlib.sha256(files[0].read_bytes()).hexdigest()
    res = run(files[0], ArrangeParams(columns=3, gap_x=5, gap_y=5, material=MaterialInput(0, -500, 1300, 1000, 5, 5, 5, 5)), out_dir=tmp_path)
    assert res.problems == []
    diff = [1 for x, y in zip(files[0].read_bytes().split(b"\r\n"), res.output.read_bytes().split(b"\r\n")) if x != y]
    assert len(diff) == 18  # 9 skupin + 9 BackupPath
    assert hashlib.sha256(files[0].read_bytes()).hexdigest() == before

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
        assert proj.items or "__kal" in p.name, p.name  # kalibrace převedené na křivky nemají skupiny


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
    res = run(files[0], ArrangeParams(columns=3, gap_x=5, gap_y=5, material=MaterialInput(700, 500)), out_dir=tmp_path)
    assert res.problems == []
    diff = [1 for x, y in zip(files[0].read_bytes().split(b"\r\n"), res.output.read_bytes().split(b"\r\n")) if x != y]
    assert len(diff) == 18  # 9 skupin + 9 BackupPath
    assert hashlib.sha256(files[0].read_bytes()).hexdigest() == before


# --- C: nativní tvary LightBurnu (Test_tvary_A / L_A / _posun, Test_klicenky) ----------------------

TVARY_A_SHA = "ca790133486ccfb43cddc9395878e86959fbf87bd9e7638f54d1ff26ada2486b"
TVARY_A_POSUN_SHA = "13e27f9701694b1aa1588762c4d2f3f0e35e4b2d9127deab6ffc44f8e17d205a"
TVARY_L_A_SHA = "c554e44abcd99733296019f57d233b44edf44cd9a6a36b3631198fdc1838642b"
KLICENKY_SHA = "9476cc8cd660a90dd387d8bfd7fd033db2c68fddf2ab3fcae72c89d1ebf53ddd"


def _one(sha: str) -> Path:
    files = _by_sha(sha)
    if not files:
        pytest.skip("testovací soubor C není ve složce")
    return files[0]


@pytest.mark.parametrize("sha", [TVARY_A_SHA, TVARY_L_A_SHA, KLICENKY_SHA])
def test_native_shapes_all_items_supported(sha):
    proj = load_project(_one(sha))
    assert len(proj.items) == 8 and all(it.supported for it in proj.items), [(it.id, it.reasons) for it in proj.items]


def test_translation_write_matches_lightburn_move():
    """LightBurn posunul K1 o (50, 30): náš zápis změní tytéž dva řádky na tytéž hodnoty."""
    from grid_arranger.adapters.lightburn.write import apply_patches, plan_patches

    src, ref = _one(TVARY_A_SHA), _one(TVARY_A_POSUN_SHA)
    p = load_project(src)
    ours = apply_patches(p.data, plan_patches(p, {"G1": (50.000076, 30.000229)})).split(b"\r\n")
    theirs = ref.read_bytes().split(b"\r\n")
    orig = src.read_bytes().split(b"\r\n")
    assert len(ours) == len(theirs) == len(orig)
    diff = [i for i, (a, b) in enumerate(zip(ours, theirs)) if a != b and not a.lstrip().startswith(b"<Thumbnail")]
    for i in diff:  # jen zaokrouhlení v posledním řádu (LightBurn počítá v jednoduché přesnosti)
        va = [float(v) for v in ours[i].split(b">")[1].split(b"<")[0].split()]
        vb = [float(v) for v in theirs[i].split(b">")[1].split(b"<")[0].split()]
        assert va == pytest.approx(vb, abs=1e-4)
    changed = [i for i, (a, b) in enumerate(zip(ours, orig)) if a != b]
    assert len(changed) == 2  # XForm skupiny + BackupPath textu


def test_klicenky_rotation_saves_material(tmp_path):
    src = _one(KLICENKY_SHA)
    p = dict(columns=4, gap_x=3, gap_y=3, material=MaterialInput(600, 400))
    plain = run(src, ArrangeParams(**p), out_dir=tmp_path)
    turned = run(src, ArrangeParams(**p, rotation="any"), out_dir=tmp_path)
    assert plain.problems == [] and turned.problems == []
    area = lambda r: r.plan.layout.grid_bounds.width * r.plan.layout.grid_bounds.height  # noqa: E731
    assert area(turned) < 0.9 * area(plain)
    assert all(it.supported for it in load_project(turned.output).items)

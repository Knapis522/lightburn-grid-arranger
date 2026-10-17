"""Natočení v plánu, zápisu a nezávislé kontrole (spec. v1.13) — syntetické projekty."""

from __future__ import annotations

import math

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, make_plan, run

from .lbrn2_builder import Group, Path, Text, card, project


def tilted(cx, cy, w=120, h=30, deg=30.0, text="Klíčenka"):
    r = math.radians(deg)
    pts = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((round(cx + x * math.cos(r) - y * math.sin(r), 6), round(cy + x * math.sin(r) + y * math.cos(r), 6)))
    return Group([Path(pts), Text(text, (cx - 15, cy - 4, 30, 8))])


def write(tmp_path, data, name="k.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def params(**kw):
    base = dict(columns=2, gap_x=5, gap_y=5, material=MaterialInput(700, 500), rotation="any")
    base.update(kw)
    return ArrangeParams(**base)


@pytest.mark.parametrize("mirror_x", [True, False])
def test_any_rotation_straightens_and_writes_verified_output(tmp_path, mirror_x):
    src = write(tmp_path, project([tilted(0, 0), tilted(300, 0), tilted(0, 300)], mirror_x=mirror_x))
    before = src.read_bytes()
    p = load_project(src)
    plan = make_plan(p, params())
    assert set(plan.rotations) == {"G1", "G2", "G3"}
    for pl in plan.layout.placements:
        w, h = pl.target_bounds.width, pl.target_bounds.height
        assert max(w, h) == pytest.approx(120, abs=0.01) and min(w, h) == pytest.approx(30, abs=0.01)
    assert plan.report.can_save
    res = run(src, params(), out_dir=tmp_path)
    assert res.problems == [] and res.output.exists()  # nezávislá kontrola + kontrola po znovunačtení
    assert src.read_bytes() == before
    q = load_project(res.output)
    assert all(it.supported for it in q.items)  # BackupPath textu natočený se skupinou


def test_rotation_none_is_unchanged_translation(tmp_path):
    src = write(tmp_path, project([tilted(0, 0), tilted(300, 0)]))
    plan = make_plan(load_project(src), params(rotation="none"))
    assert plan.rotations == {} and all(len(m) == 2 for m in plan.moves_file.values())


def test_cards_are_not_rotated_in_any_mode(tmp_path):
    src = write(tmp_path, project([card(0, 0), card(200, 0), card(0, 200), card(200, 200)]))
    plan = make_plan(load_project(src), params(columns=2))
    assert plan.rotations == {}  # obdélník už je nejmenší a jiná orientace nic neušetří


def test_no_rotate_exception(tmp_path):
    src = write(tmp_path, project([tilted(0, 0), tilted(300, 0)]))
    plan = make_plan(load_project(src), params(no_rotate=frozenset({"G2"})))
    assert "G1" in plan.rotations and "G2" not in plan.rotations


def test_90_mode_turns_portrait_items_when_grid_gets_smaller(tmp_path):
    items = [card(i * 70, 0, w=40, h=100) for i in range(3)] + [card(0, 300, w=100, h=40)]
    src = write(tmp_path, project(items))
    p = load_project(src)
    plan = make_plan(p, params(rotation="90", columns=4))
    angles = plan.rotations
    assert all(abs(a) in (90.0, 270.0) or a == 90.0 for a in angles.values())
    assert set(angles) == {"G1", "G2", "G3"}  # na šířku — mřížka 4 × 1 je nižší
    res = run(src, params(rotation="90", columns=4), out_dir=tmp_path)
    assert res.problems == []
    assert "e-" not in res.output.read_text(encoding="utf-8")  # přesné 0/±1, žádné 6e-17


def test_cli_rotate_and_protocol(tmp_path, capsys):
    import json

    from grid_arranger.cli import main

    src = write(tmp_path, project([tilted(0, 0), tilted(300, 0)]))
    assert main(["arrange", str(src), "--columns", "2", "--board", "700", "500", "--rotate", "any", "--out-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "rotate" in out
    proto = json.loads(next(tmp_path.glob("*__grid_001.json")).read_text(encoding="utf-8"))
    assert proto["parameters"]["rotation_mode"] == "any"
    assert all(p["rotation_deg_screen_clockwise"] != 0 and len(p["transform_lightburn"]) == 6 for p in proto["placements"])

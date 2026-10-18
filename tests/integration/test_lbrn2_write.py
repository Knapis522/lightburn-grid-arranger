"""Zápis a kontrola: T-MVP-19…24, T-FMT-04, 07; LB-01…03, 05, 11 (spec. kap. 9, 14, 26.1)."""

from __future__ import annotations

import hashlib
import json
import os

import pytest

from grid_arranger.adapters.lightburn import write as wr
from grid_arranger.adapters.lightburn.geometry import fmt_num
from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, execute, make_plan, run
from grid_arranger.domain import GridError
from grid_arranger.safety.verify import verify_output

from .lbrn2_builder import Group, card, project, rect

BOARD = MaterialInput(4000, 4000, -2000, -2000)


def four_cards():
    return project([card(10, 20, text="A"), card(300, 400, text="B"), card(-50, 700, 80, 50, text="C"), card(900, -100, text="D")])


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def changed_lines(a: bytes, b: bytes) -> list[tuple[bytes, bytes]]:
    la, lb = a.split(b"\r\n"), b.split(b"\r\n")
    assert len(la) == len(lb)
    return [(x, y) for x, y in zip(la, lb) if x != y]


# --- formát čísel ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "v, s",
    [(1362.0, "1362"), (1000.99646, "1000.9965"), (-611.83984, "-611.83984"), (0.0, "0"), (-0.0, "0"),
     (1e-5, "0.00001"), (-2.5e-7, "-0.00000025"), (123456.789, "123456.79")],
)
def test_fmt_num_matches_lightburn_style(v, s):
    assert fmt_num(v) == s


# --- LB-01/02/03, T-MVP-19: přesné změny ---------------------------------------------------


def test_t_mvp19_only_group_and_backup_xforms_change(write_project):
    src = write_project(four_cards())
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    a, b = src.read_bytes(), res.output.read_bytes()
    diff = changed_lines(a, b)
    assert len(diff) == 8  # 4 skupiny + 4 BackupPath textů
    assert all(x.strip().startswith(b"<XForm>") and y.strip().startswith(b"<XForm>") for x, y in diff)
    assert a.count(b"<Shape") == b.count(b"<Shape")
    assert b.count(b"\r\n") == a.count(b"\r\n") and b"\n" not in b.replace(b"\r\n", b"")  # CRLF zachováno


def test_lb01_new_positions_match_plan_after_reload(write_project):
    src = write_project(four_cards())
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    out = load_project(res.output)
    for pl in res.plan.layout.placements:
        got = out.item(pl.item_id).screen_bounds
        assert got.left == pytest.approx(pl.target_bounds.left, abs=1e-3)
        assert got.top == pytest.approx(pl.target_bounds.top, abs=1e-3)
        assert got.width == pytest.approx(pl.old_bounds.width, abs=1e-6)  # rozměr beze změny


def test_lb02_texts_move_with_group_and_text_content_unchanged(write_project):
    src = write_project(four_cards())
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    out = load_project(res.output)
    assert [i.label for i in out.items] == ["A", "B", "C", "D"]
    assert all(i.supported for i in out.items)  # BackupPath stále odpovídá skupině


def test_lb05_unselected_group_bytes_unchanged(write_project):
    src = write_project(four_cards())
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, order=("G1", "G4")))
    before, after = load_project(src), load_project(res.output)
    for gid in ("G2", "G3"):
        n0, n1 = before.item(gid).node, after.item(gid).node
        assert src.read_bytes()[n0.start : n0.content_end] == res.output.read_bytes()[n1.start : n1.content_end]


def test_t_fmt04_original_unchanged_and_protocol_written(write_project):
    src = write_project(four_cards())
    h = sha(src)
    res = run(src, ArrangeParams(columns=4, gap_x=3, gap_y=3, material=BOARD))
    assert sha(src) == h
    assert res.output.name == "test__grid_001.lbrn2"
    proto = json.loads(res.protocol.read_text(encoding="utf-8"))
    assert proto["verification"]["passed"] is True
    assert proto["source"]["sha256"] == h
    assert len(proto["placements"]) == 4


def test_t_fmt07_deterministic_output(write_project, tmp_path):
    src = write_project(four_cards())
    p = ArrangeParams(columns=3, gap_x=2.5, gap_y=1.25, material=BOARD)
    o1 = run(src, p).output.read_bytes()
    o2 = run(src, p).output
    assert o2.name == "test__grid_002.lbrn2"  # T-MVP-23: další číslo, nikdy přepis
    assert o2.read_bytes() == o1


# --- umístění a orientace (spec. v1.10) ------------------------------------------------------


def machine_bboxes(res):
    out = load_project(res.output)
    return {it.id: it.file_bbox for it in out.items}


@pytest.mark.parametrize("mx, my", [(True, True), (False, True), (False, False), (True, False)])
def test_manual_start_is_grid_corner_at_origin_in_lightburn_coordinates(write_project, mx, my):
    src = write_project(project([card(10, 20), card(300, 400)], mirror_x=mx, mirror_y=my))
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, anchor="manual", start=(500, 10)))
    b = machine_bboxes(res)
    # pro všechny rohy počátku: roh u počátku = nejmenší X a Y stroje; G1 (plnění od počátku) leží v tomto rohu
    assert b["G1"][0] == pytest.approx(500) and b["G1"][1] == pytest.approx(10)
    assert b["G2"][0] == pytest.approx(603) and b["G2"][1] == pytest.approx(10)


@pytest.mark.parametrize("mx, my", [(True, True), (False, True), (False, False), (True, False)])
def test_origin_anchor_puts_grid_into_board_corner_at_origin(write_project, mx, my):
    src = write_project(project([card(310, 20, text="A"), card(-300, 400, text="B"), card(50, 50, text="C")], mirror_x=mx, mirror_y=my))
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=MaterialInput(700, 500)))
    b = machine_bboxes(res)
    assert b["G1"][:2] == pytest.approx((5, 5))  # deska u počátku + okraj 5 mm
    assert b["G2"][:2] == pytest.approx((108, 5))  # další sloupec dál od počátku
    assert b["G3"][:2] == pytest.approx((5, 68))  # druhý řádek začíná opět u počátku


@pytest.mark.parametrize("mx", [True, False])
def test_reading_fill_starts_top_left_on_screen(write_project, mx):
    src = write_project(project([card(0, 0), card(500, 0)], mirror_x=mx))
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=MaterialInput(700, 500), fill="reading"))
    b = machine_bboxes(res)
    if mx:  # počátek vpravo → vlevo na obrazovce = větší X stroje
        assert b["G1"][0] > b["G2"][0]
    else:
        assert b["G1"][0] < b["G2"][0]


def test_center_anchor_centers_grid_on_board(write_project):
    src = write_project(project([card(0, 0), card(500, 0)]))
    res = run(src, ArrangeParams(columns=2, gap_x=4, gap_y=3, material=MaterialInput(700, 500)), write=True, out_dir=None)
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=4, gap_y=3, material=MaterialInput(700, 500), anchor="center"))
    g = plan.layout.grid_bounds
    assert (g.left + g.right) / 2 == pytest.approx(-350)  # počátek vpravo: deska X 0..700 → obrazovka −700..0
    assert (g.top + g.bottom) / 2 == pytest.approx(250)
    assert res.output is not None


def test_selection_anchor_keeps_grid_at_original_place(write_project):
    src = write_project(project([card(10, 20), card(300, 400)], mirror_x=False))
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, anchor="selection", fill="reading"))
    assert (plan.layout.grid_bounds.left, plan.layout.grid_bounds.top) == pytest.approx((10, 20))


@pytest.mark.parametrize(
    "params, code",
    [
        (ArrangeParams(columns=2, gap_x=3, gap_y=3, material=None), "material_missing"),
        (ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, anchor="nowhere"), "invalid_anchor"),
        (ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, anchor="manual"), "invalid_start"),
        (ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, fill="diagonal"), "invalid_fill_corner"),
        (ArrangeParams(columns=2, gap_x=3, gap_y=3, material=MaterialInput(700, 500, margin_left=400, margin_right=400)), "margins_exceed_material"),
    ],
)
def test_invalid_placement_parameters(write_project, params, code):
    src = write_project(project([card(0, 0)]))
    with pytest.raises(GridError) as e:
        make_plan(load_project(src), params)
    assert e.value.code == code


# --- T-MVP-20/21: vadný writer musí kontrola zachytit ---------------------------------------


def _good(write_project):
    src = write_project(four_cards())
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    ops = wr.plan_patches(plan.project, plan.moves_file)
    out = wr.apply_patches(plan.project.data, ops)
    tops = {it.id: it.source_order for it in plan.project.items}
    moves = {tops[k]: v for k, v in plan.moves_file.items()}
    return plan.project.data, out, moves


def test_verify_accepts_correct_output(write_project):
    a, b, moves = _good(write_project)
    assert verify_output(a, b, moves) == []


def test_t_mvp20_changed_cut_setting_is_detected(write_project):
    a, b, moves = _good(write_project)
    bad = b.replace(b'<maxPower Value="40"/>', b'<maxPower Value="45"/>')
    assert verify_output(a, bad, moves)


def test_t_mvp21_changed_text_is_detected(write_project):
    a, b, moves = _good(write_project)
    bad = b.replace(b'Str="B"', b'Str="X"')
    assert "structure_changed" in verify_output(a, bad, moves)


def test_moved_unselected_group_is_detected(write_project):
    a, b, moves = _good(write_project)
    del moves[2]  # tvrdíme, že G2 se přesouvat neměl
    assert any(p.startswith("unexpected_xform_change") for p in verify_output(a, b, moves))


def test_wrong_translation_is_detected(write_project):
    a, b, moves = _good(write_project)
    moves[1] = (moves[1][0] + 0.01, moves[1][1])
    assert any(p.startswith("wrong_translation") for p in verify_output(a, b, moves))


def test_changed_linear_part_is_detected(write_project):
    src = write_project(project([card(10, 20)]))
    a = src.read_bytes()
    b = a.replace(b"<XForm>1 0 0 1 10 20</XForm>", b"<XForm>1 0 0 1.0001 10 20</XForm>", 1)
    problems = verify_output(a, b, {1: (0.0, 0.0)})
    assert any(p.startswith("linear_part_changed") for p in problems)


def test_unreadable_output_is_detected(write_project):
    a, b, moves = _good(write_project)
    assert verify_output(a, b[: len(b) // 2], moves)[0].startswith("output_unreadable")


# --- T-MVP-22/23/24: bezpečné ukládání ------------------------------------------------------


def test_t_mvp22_failed_publish_leaves_nothing(write_project, monkeypatch):
    src = write_project(four_cards())
    h = sha(src)

    def boom(tmp, final):
        raise OSError("disk full (simulace)")

    monkeypatch.setattr(wr, "_publish_no_overwrite", boom)
    with pytest.raises(GridError) as e:
        run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    assert e.value.code == "write_failed"
    assert sorted(p.name for p in src.parent.iterdir()) == ["test.lbrn2"]  # žádný výstup ani .tmp
    assert sha(src) == h


@pytest.mark.skipif(os.name == "nt", reason="POSIX cesta přes hard link")
def test_cleanup_failure_after_publish_is_not_an_error(tmp_path, monkeypatch):
    real_unlink = os.unlink

    def no_delete(p, *a, **kw):
        if ".tmp-" in str(p):
            raise PermissionError("Operation not permitted (simulace složky bez práva mazat)")
        return real_unlink(p, *a, **kw)

    monkeypatch.setattr(os, "unlink", no_delete)
    monkeypatch.setattr(type(tmp_path), "unlink", lambda self, *a, **k: no_delete(self))
    out = wr.write_new_file(tmp_path / "x__grid_001.lbrn2", b"data")
    assert out.read_bytes() == b"data"


def test_t_mvp23_never_overwrites_existing_file(tmp_path):
    target = tmp_path / "x__grid_001.lbrn2"
    target.write_bytes(b"old")
    with pytest.raises(GridError) as e:
        wr.write_new_file(target, b"new")
    assert e.value.code == "output_exists" and target.read_bytes() == b"old"
    assert wr.next_output_path(tmp_path / "x.lbrn2").name == "x__grid_002.lbrn2"


def test_write_refuses_source_path(tmp_path):
    src = tmp_path / "a.lbrn2"
    with pytest.raises(GridError) as e:
        wr.write_new_file(src, b"x", forbidden=src)
    assert e.value.code == "would_overwrite_source"


def test_t_mvp24_source_changed_after_loading_blocks(write_project):
    src = write_project(four_cards())
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    src.write_bytes(src.read_bytes() + b"\r\n")  # uživatel mezitím soubor uložil znovu
    with pytest.raises(GridError) as e:
        execute(plan)
    assert e.value.code == "source_changed"
    assert not any(p.name.endswith("__grid_001.lbrn2") for p in src.parent.iterdir())


# --- validace blokuje zápis -----------------------------------------------------------------


def test_invalid_layout_is_never_written(write_project):
    src = write_project(four_cards())
    small = MaterialInput(150, 100)
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=small))
    assert "outside_material" in plan.report.codes()
    with pytest.raises(GridError) as e:
        execute(plan)
    assert e.value.code == "validation_failed"
    assert sorted(p.name for p in src.parent.iterdir()) == ["test.lbrn2"]


def test_loose_object_in_grid_area_blocks(write_project):
    src = write_project(project([card(10, 20), card(300, 400), rect(0, 0, 500, 500, cut=1)]))
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, anchor="manual", start=(10, 10)))
    assert "obstacle_overlap" in plan.report.codes()
    assert not plan.report.can_save


def test_selecting_blocked_item_is_refused(write_project):
    bad = Group([rect(0, 0, 100, 60, prims="L0 1L1 2L2 3")])
    src = write_project(project([card(10, 20), bad]))
    with pytest.raises(GridError) as e:
        make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, order=("G1", "G2")))
    assert e.value.code == "item_not_supported"


def test_no_temp_files_left_after_success(write_project):
    src = write_project(four_cards())
    run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD))
    assert not [p for p in os.listdir(src.parent) if ".tmp-" in p]


def test_check_output_path_rules(tmp_path):
    from grid_arranger.application.arrange_job import check_output_path
    from grid_arranger.domain import GridError

    src = tmp_path / "a.lbrn2"
    src.write_bytes(b"x")
    assert check_output_path(tmp_path / "b", src) == tmp_path / "b.lbrn2"
    assert check_output_path(tmp_path / "b.LBRN2", src) == tmp_path / "b.LBRN2"
    for bad, code in ((src, "would_overwrite_source"), (tmp_path / "missing" / "c.lbrn2", "write_failed")):
        with pytest.raises(GridError) as e:
            check_output_path(bad, src)
        assert e.value.code == code
    (tmp_path / "d.json").write_text("{}")
    with pytest.raises(GridError) as e:
        check_output_path(tmp_path / "d.lbrn2", src)  # existující protokol by se přepsal
    assert e.value.code == "output_exists"


def test_protocol_none_ignores_existing_json(tmp_path):
    from grid_arranger.application.arrange_job import check_output_path

    src = tmp_path / "a.lbrn2"
    src.write_bytes(b"x")
    (tmp_path / "d.json").write_text("{}")
    assert check_output_path(tmp_path / "d.lbrn2", src, "none") == tmp_path / "d.lbrn2"


def test_next_output_path_continues_series_of_saved_output(tmp_path):
    # z uloženého výstupu (pokračování v uloženém souboru) se číslo nepřidává podruhé
    (tmp_path / "x__grid_001.lbrn2").write_bytes(b"data")
    assert wr.next_output_path(tmp_path / "x__grid_001.lbrn2").name == "x__grid_002.lbrn2"
    assert wr.next_output_path(tmp_path / "__grid_001.lbrn2").name == "__grid_001__grid_001.lbrn2"


@pytest.mark.parametrize("mx", [True, False])
def test_bottom_origin_fills_rows_upward_from_origin_on_screen(write_project, mx):
    # počátek dole: 1. řádek u počátku = dole na obrazovce, další řádek nad ním (v souboru větší Y)
    src = write_project(project([card(0, 0), card(500, 0), card(0, 300)], mirror_x=mx, mirror_y=False))
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=MaterialInput(700, 500)))
    t = {p.item_id: p.target_bounds for p in plan.layout.placements}
    g = plan.layout.grid_bounds
    assert t["G1"].bottom == pytest.approx(g.bottom) and t["G3"].bottom < t["G1"].top  # G3 o řádek výš
    assert (t["G1"].right == pytest.approx(g.right)) if mx else (t["G1"].left == pytest.approx(g.left))
    assert plan.origin_corner_lightburn == pytest.approx((5, 5))
    res = execute(plan, output=src.with_name("out.lbrn2"))  # nezávislá kontrola výstupu i poloh po načtení
    assert res.output.exists() and not res.problems
    b = machine_bboxes(res)
    assert b["G1"][:2] == pytest.approx((5, 5)) and b["G3"][:2] == pytest.approx((5, 68))  # další řádek dál od počátku


@pytest.mark.parametrize("mx", [True, False])
def test_bottom_origin_rotation_keeps_item_inside_board(write_project, mx):
    # natočení se v souboru zapíše jako S ∘ T ∘ S i pro osu Y nahoru; výsledek po načtení leží na desce
    src = write_project(project([card(0, 0, w=100, h=30), card(200, 0, w=100, h=30)], mirror_x=mx, mirror_y=False))
    params = ArrangeParams(columns=1, gap_x=3, gap_y=3, material=MaterialInput(700, 500), angles={"G1": 30.0})
    res = run(src, params, write=True, out_dir=None)
    out = load_project(res.output)
    for it in out.items:
        x0, y0, x1, y1 = it.file_bbox
        assert -1e-6 <= x0 and x1 <= 700 + 1e-6 and -1e-6 <= y0 and y1 <= 500 + 1e-6

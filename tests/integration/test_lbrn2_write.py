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

BOARD = MaterialInput(-2000, -2000, 4000, 4000, 5, 5, 5, 5)


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


# --- start a orientace ----------------------------------------------------------------------


@pytest.mark.parametrize("mx", [True, False])
def test_start_is_in_lightburn_coordinates(write_project, mx):
    src = write_project(project([card(10, 20), card(300, 400)], mirror_x=mx))
    res = run(src, ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, start=(500, 10)))
    out = load_project(res.output)
    b1, b2 = out.items[0].file_bbox, out.items[1].file_bbox
    assert b1[1] == pytest.approx(10) and b2[1] == pytest.approx(10)  # horní hrana = Y 10
    if mx:  # počátek vpravo: první sloupec vpravo, X roste doleva
        assert b1[2] == pytest.approx(500) and b2[2] == pytest.approx(500 - 103)
    else:
        assert b1[0] == pytest.approx(500) and b2[0] == pytest.approx(603)


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
    small = MaterialInput(0, 0, 150, 100)
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=small))
    assert "outside_material" in plan.report.codes()
    with pytest.raises(GridError) as e:
        execute(plan)
    assert e.value.code == "validation_failed"
    assert sorted(p.name for p in src.parent.iterdir()) == ["test.lbrn2"]


def test_loose_object_in_grid_area_blocks(write_project):
    src = write_project(project([card(10, 20), card(300, 400), rect(0, 0, 500, 500, cut=1)]))
    plan = make_plan(load_project(src), ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, start=(400, 100)))
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

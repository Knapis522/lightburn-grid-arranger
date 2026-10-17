"""Kopie výrobků (spec. v1.16): plán, zápis nových skupin a nezávislá kontrola."""

from __future__ import annotations

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.write import apply_with_copies, plan_patches
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, make_plan, run
from grid_arranger.safety.verify import verify_output

from .lbrn2_builder import Group, Text, card, keyring, project, rect
from .test_rotation_plan import tilted


def write(tmp_path, data, name="c.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def params(order, copies, **kw):
    base = dict(columns=3, gap_x=5, gap_y=5, material=MaterialInput(700, 500), order=order, copies=copies)
    base.update(kw)
    return ArrangeParams(**base)


@pytest.mark.parametrize("mirror_x", [True, False])
def test_copies_are_written_as_new_groups_and_verified(tmp_path, mirror_x):
    src = write(tmp_path, project([card(0, 0, text="A"), keyring(300, 100, text="K")], mirror_x=mirror_x))
    before = src.read_bytes()
    copies = {"G1+1": "G1", "G2+1": "G2", "G2+2": "G2"}
    res = run(src, params(("G1", "G2", *copies), copies), out_dir=tmp_path)
    assert res.problems == [] and src.read_bytes() == before
    q = load_project(res.output)
    assert len(q.items) == 5 and all(it.supported for it in q.items)
    assert [it.label for it in q.items] == ["A", "K", "A", "K", "K"]
    sizes = [(round(it.file_bbox[2] - it.file_bbox[0], 3), round(it.file_bbox[3] - it.file_bbox[1], 3)) for it in q.items]
    assert sizes[2] == sizes[0] and sizes[3] == sizes[4] == sizes[1]


def test_copy_of_unselected_item_leaves_source_as_obstacle(tmp_path):
    src = write(tmp_path, project([card(0, 0), card(0, 300)]))
    p = load_project(src)
    plan = make_plan(p, params(("G1", "G2+1"), {"G2+1": "G2"}))
    assert "G2" not in plan.moves_file and plan.copies == {"G2+1": "G2"}
    res = run(src, params(("G1", "G2+1"), {"G2+1": "G2"}), out_dir=tmp_path)
    assert res.problems == []
    q = load_project(res.output)
    assert q.item("G2").file_bbox == p.item("G2").file_bbox  # originál zůstal na místě


def test_rotated_copies_with_manual_and_automatic_angles(tmp_path):
    src = write(tmp_path, project([tilted(0, 0), tilted(300, 0)]))
    copies = {"G1+1": "G1", "G1+2": "G1"}
    p = params(("G1", "G2", *copies), copies, rotation="any", angles={"G1+2": 90.0})
    plan = make_plan(load_project(src), p)
    assert plan.rotations["G1+1"] == pytest.approx(plan.rotations["G1"]) and plan.rotations["G1+2"] == 90.0
    res = run(src, p, out_dir=tmp_path)
    assert res.problems == []


def test_copies_not_in_order_are_ignored(tmp_path):
    src = write(tmp_path, project([card(0, 0)]))
    plan = make_plan(load_project(src), params(("G1",), {"G1+1": "G1"}))
    assert plan.copies == {} and len(plan.layout.placements) == 1


def test_shared_vertex_lists_are_referenced_not_repeated(tmp_path):
    src = write(tmp_path, project([Group([rect(0, 0, 100, 60), Text("S", (5, 5, 20, 10))])]))
    p = load_project(src)
    out = apply_with_copies(p, plan_patches(p, {}), [("G1", (200.0, 0.0))])
    assert out.count(b"<VertList>") == p.data.count(b"<VertList>") + 1  # jen BackupPath textu; cesta odkazuje na VertID
    assert verify_output(p.data, out, {}, [(1, (200.0, 0.0))]) == []
    q = load_project(write(tmp_path, out, "o.lbrn2"))
    assert q.items[1].supported and q.items[1].file_bbox == pytest.approx((200, 0, 300, 60))


def test_verifier_rejects_tampered_copy(tmp_path):
    src = write(tmp_path, project([card(0, 0, text="A")]))
    p = load_project(src)
    out = apply_with_copies(p, plan_patches(p, {}), [("G1", (150.0, 0.0))])
    assert verify_output(p.data, out, {}, [(1, (150.0, 0.0))]) == []
    assert verify_output(p.data, out, {}, [(1, (151.0, 0.0))])  # jiný posun
    tampered = out[: len(out) // 2] + out[len(out) // 2 :].replace(b'Str="A"', b'Str="B"', 1)
    assert any("copy" in x for x in verify_output(p.data, tampered, {}, [(1, (150.0, 0.0))]))
    assert verify_output(p.data, out, {}, []) != []  # nehlášená kopie

"""Vynechané objekty (spec. v1.27): do výstupu se nezapíší, mřížka s nimi nepočítá, sdílená geometrie se přesune."""

from __future__ import annotations

import json

import pytest

from grid_arranger.adapters.lightburn.coords import Orientation
from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.write import apply_with_copies, omit_shapes, plan_patches
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, TargetLaser, make_plan, run
from grid_arranger.domain.errors import GridError
from grid_arranger.safety.verify import verify_output

from .lbrn2_builder import Group, Text, card, project, rect


def write(tmp_path, data, name="o.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def params(order, **kw):
    base = dict(columns=2, gap_x=5, gap_y=5, material=MaterialInput(700, 500), order=order)
    base.update(kw)
    return ArrangeParams(**base)


def test_omitted_item_and_loose_shape_are_not_in_output(tmp_path):
    src = write(tmp_path, project([card(0, 0, text="A"), card(300, 300, text="B"), rect(500, 400, 20, 20), card(0, 200, text="C")]))
    before = src.read_bytes()
    res = run(src, params(("G1", "G4"), omit=frozenset({"G2", "S3"})), out_dir=tmp_path)
    assert res.problems == [] and src.read_bytes() == before
    q = load_project(res.output)
    assert [it.label for it in q.items] == ["A", "C"] and q.loose == []
    assert res.plan.omitted == {"G2", "S3"}


def test_omitted_object_is_not_an_obstacle(tmp_path):
    # mřížka v místě výběru: A zůstane, kde je, a B ho překrývá
    data = project([card(10, 300, text="A"), card(50, 320, text="B")], mirror_x=False)
    src = write(tmp_path, data)
    p = load_project(src)
    kept = make_plan(p, params(("G1",), anchor="selection"))
    assert not kept.report.can_save  # ponechaný objekt = překážka
    omitted = make_plan(p, params(("G1",), anchor="selection", omit=frozenset({"G2"})))
    assert omitted.report.can_save


def test_omitting_selected_item_is_rejected(tmp_path):
    p = load_project(write(tmp_path, project([card(0, 0), card(0, 300)])))
    with pytest.raises(GridError) as e:
        make_plan(p, params(("G1", "G2"), omit=frozenset({"G2"})))
    assert e.value.code == "omitted_selected"
    with pytest.raises(GridError) as e:
        make_plan(p, params(("G1", "G2+1"), copies={"G2+1": "G2"}, omit=frozenset({"G2"})))
    assert e.value.code == "omitted_selected"
    with pytest.raises(GridError) as e:
        make_plan(p, params(("G1",), omit=frozenset({"G9"})))
    assert e.value.code == "unknown_item"


def shared_project():
    outline = rect(0, 0, 100, 60)
    a = Group([outline, Text("A", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 0, 0))
    b = Group([rect(0, 0, 100, 60, share_from=outline), Text("B", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 0, 200))
    c = Group([rect(0, 0, 100, 60, share_from=outline), Text("C", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 0, 400))
    return project([a, b, c])


def test_shared_geometry_moves_to_first_kept_reference(tmp_path):
    src = write(tmp_path, shared_project())
    p = load_project(src)
    assert p.data.count(b"<VertList>") == 1 + 3  # obrys A + BackupPath tří textů
    res = run(src, params(("G2", "G3"), omit=frozenset({"G1"})), out_dir=tmp_path)
    assert res.problems == []
    out = res.output.read_bytes()
    assert out.count(b"<VertList>") == 1 + 2 and out.count(b"<PrimList>LineClosed</PrimList>") == 1 + 2
    q = load_project(res.output)
    assert [it.label for it in q.items] == ["B", "C"] and all(it.supported for it in q.items)
    for it in q.items:
        assert it.file_bbox[2] - it.file_bbox[0] == pytest.approx(100) and it.file_bbox[3] - it.file_bbox[1] == pytest.approx(60)
    # definice je v první ponechané skupině (B), ne v C
    b_start, c_start = out.index(b'Str="B"'), out.index(b'Str="C"')
    first_path_list = out.index(b"<VertList>V0 0c0x1c1x1")
    assert first_path_list < b_start < c_start or first_path_list < c_start


def test_shared_geometry_with_copies_of_kept_item(tmp_path):
    src = write(tmp_path, shared_project())
    copies = {"G3+1": "G3", "G3+2": "G3"}
    res = run(src, params(("G3", *copies), copies=copies, omit=frozenset({"G1", "G2"})), out_dir=tmp_path)
    assert res.problems == []
    q = load_project(res.output)
    assert [it.label for it in q.items] == ["C", "C", "C"] and all(it.supported for it in q.items)


def test_protocol_lists_omitted(tmp_path):
    src = write(tmp_path, project([card(0, 0, text="A"), card(0, 300, text="B")]))
    plan = make_plan(load_project(src), params(("G1",), omit=frozenset({"G2"})))
    from grid_arranger.application.arrange_job import execute

    res = execute(plan, out_dir=tmp_path)
    proto = json.loads(res.protocol.read_text(encoding="utf-8"))
    assert proto["omitted"] == [{"id": "G2", "label": "B"}]


def test_convert_to_other_laser_with_rest_omitted(tmp_path):
    src = write(tmp_path, project([card(0, 0, text="A"), card(0, 300, text="B")], mirror_x=True))
    target = TargetLaser("Levý laser", Orientation(False, True))
    with pytest.raises(GridError):
        make_plan(load_project(src), params(("G1",), target=target))
    res = run(src, params(("G1",), target=target, omit=frozenset({"G2"})), out_dir=tmp_path)
    assert res.problems == []
    q = load_project(res.output)
    assert q.info.device_name == "Levý laser" and len(q.items) == 1


# --- nezávislá kontrola ---------------------------------------------------------------------


def _out(p, omitted, moves=None):
    return omit_shapes(apply_with_copies(p, plan_patches(p, moves or {}), []), omitted)


def test_verifier_accepts_plain_omission_and_relocation(tmp_path):
    p = load_project(write(tmp_path, shared_project()))
    assert verify_output(p.data, _out(p, {1}), {}, omitted={1}) == []
    assert verify_output(p.data, _out(p, {2}, {"G1": (10.0, 0.0)}), {1: (10.0, 0.0)}, omitted={2}) == []


def test_verifier_rejects_wrong_omission(tmp_path):
    p = load_project(write(tmp_path, shared_project()))
    good = _out(p, {1})
    # vynechán jiný tvar, než se tvrdí
    assert verify_output(p.data, _out(p, {3}), {}, omitted={2})
    # tvrdí se vynechání, ale výstup je beze změny
    assert verify_output(p.data, p.data, {}, omitted={1})
    # vynechán navíc ještě další tvar
    assert verify_output(p.data, _out(p, {1, 3}), {}, omitted={1})
    # přesunutá definice pozměněna
    assert verify_output(p.data, good.replace(b"<VertList>V0 0c0x1c1x1V100 0", b"<VertList>V0 0c0x1c1x1V101 0", 1), {}, omitted={1})
    # přesunutá definice ve špatném tvaru (C místo B)
    bad = _out(p, {1})
    i_b = bad.index(b"<VertList>V0 0c0x1c1x1")
    line_s = bad.rfind(b"\n", 0, i_b) + 1
    line_e = bad.index(b"\n", i_b) + 1
    vline = bad[line_s:line_e]
    pl_s = line_e
    pl_e = bad.index(b"\n", pl_s) + 1
    pline = bad[pl_s:pl_e]
    moved = bad[:line_s] + bad[pl_e:]
    xc = moved.index(b"<XForm>1 0 0 1 0 400</XForm>")
    xc_end = moved.index(b"\n", xc) + 1
    moved = moved[:xc_end] + moved[xc_end:]  # skupina C — vložit do její cesty
    path_c = moved.index(b'<Shape Type="Path"', xc)
    pxe = moved.index(b"\n", moved.index(b"<XForm>", path_c)) + 1
    moved = moved[:pxe] + vline + pline + moved[pxe:]
    assert verify_output(p.data, moved, {}, omitted={1})


def test_omit_shapes_refuses_to_remove_everything(tmp_path):
    p = load_project(write(tmp_path, project([card(0, 0)])))
    with pytest.raises(GridError) as e:
        omit_shapes(p.data, {1})
    assert e.value.code == "nothing_left"


def test_cli_omit_and_unselected(tmp_path, capsys):
    from grid_arranger.cli import main

    src = write(tmp_path, project([card(0, 0, text="A"), card(0, 300, text="B"), rect(600, 450, 10, 10), card(300, 300, text="C")]))
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    out_a.mkdir()
    out_b.mkdir()
    assert main(["arrange", str(src), "--columns", "2", "--board", "700", "500", "--order", "G1,G4", "--omit", "G2",
                 "--out-dir", str(out_a)]) == 0
    q = load_project(next(out_a.glob("*.lbrn2")))
    assert [it.label for it in q.items] == ["A", "C"] and len(q.loose) == 1
    assert "Omitted:   G2" in capsys.readouterr().out
    assert main(["arrange", str(src), "--columns", "2", "--board", "700", "500", "--order", "G4",
                 "--unselected", "omit", "--out-dir", str(out_b)]) == 0
    q = load_project(next(out_b.glob("*.lbrn2")))
    assert [it.label for it in q.items] == ["C"] and q.loose == []

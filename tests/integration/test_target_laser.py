"""Příprava projektu pro jiný laser (spec. v1.23): hlavička cílového laseru a zrcadlení výrobků."""

from __future__ import annotations

import pytest

from grid_arranger.adapters.lightburn.coords import Orientation
from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.render import ProjectRenderer, stroke_points
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, TargetLaser, execute, make_plan
from grid_arranger.domain import GridError
from grid_arranger.safety.verify import verify_output

from .lbrn2_builder import Group, Text, card, project, rect

ORIENTATIONS = [Orientation(True, True), Orientation(False, True), Orientation(False, False), Orientation(True, False)]
BOARD = MaterialInput(700, 500)


def tag(x, y, label):
    """Asymetrický výrobek: text jen v levé horní části (na obrazovce zdroje) — zrcadlení by bylo vidět."""
    return Group([rect(0, 0, 100, 60), Text(label, (5, 5, 30, 10))], xform=(1, 0, 0, 1, x, y))


def shapes(proj, item_id):
    """Křivky výrobku na obrazovce, posunuté do (0, 0) — „jak výrobek vypadá“."""
    pts = stroke_points(ProjectRenderer(proj).strokes(item_id))
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    return sorted((round(x - x0, 3), round(y - y0, 3)) for x, y in pts)


@pytest.mark.parametrize("src", ORIENTATIONS, ids=lambda o: o.origin)
@pytest.mark.parametrize("dst", ORIENTATIONS, ids=lambda o: o.origin)
def test_converted_items_look_the_same_on_target_laser(write_project, tmp_path, src, dst):
    path = write_project(project([tag(10, 20, "A"), tag(300, 100, "B"), tag(150, 300, "C")],
                                 mirror_x=src.mirror_x, mirror_y=src.mirror_y))
    source = load_project(path)
    params = ArrangeParams(columns=2, gap_x=3, gap_y=3, material=BOARD, rotation="none",
                           angles={"G2": 30.0}, target=TargetLaser("Modrý laser", dst))
    plan = make_plan(source, params)
    res = execute(plan, output=tmp_path / "out.lbrn2")  # nezávislá kontrola + poloha po načtení
    out = load_project(res.output)
    assert out.info.orientation == dst and out.info.device_name == "Modrý laser"
    assert out.items[0].file_bbox[:2] == pytest.approx((5, 5))  # 1. výrobek v rohu u počátku cílového laseru
    for iid in ("G1", "G3"):  # stejný vzhled (žádné zrcadlení), jen jinde
        assert shapes(out, iid) == shapes(source, iid)


def test_same_orientation_only_changes_device_name(write_project, tmp_path):
    path = write_project(project([card(10, 20), card(300, 100)]))
    source = load_project(path)
    plan = make_plan(source, ArrangeParams(2, 3, 3, BOARD, target=TargetLaser("Jiný Ruida", source.info.orientation)))
    assert all(len(m) == 2 for m in plan.moves_file.values())  # čistý posun, žádné zrcadlení
    res = execute(plan, output=tmp_path / "o.lbrn2")
    b = res.output.read_bytes()
    assert 'DeviceName="Jiný Ruida"'.encode() in b and b.count(b"MirrorX") == 1


def test_target_equal_to_project_laser_is_ignored(write_project):
    source = load_project(write_project(project([card(10, 20)])))
    t = TargetLaser(source.info.device_name, source.info.orientation)
    assert make_plan(source, ArrangeParams(1, 3, 3, BOARD, target=t)).target is None


def test_mirrored_conversion_needs_whole_project(write_project):
    source = load_project(write_project(project([card(10, 20), card(300, 100)])))
    params = ArrangeParams(1, 3, 3, BOARD, order=("G1",), target=TargetLaser("L", Orientation(False, True)))
    with pytest.raises(GridError) as e:
        make_plan(source, params)
    assert e.value.code == "convert_needs_whole_project" and e.value.params["objects"] == ["G2"]


def test_copies_are_converted_too(write_project, tmp_path):
    source = load_project(write_project(project([tag(10, 20, "A")])))
    params = ArrangeParams(3, 3, 3, BOARD, order=("G1", "G1+1", "G1+2"), copies={"G1+1": "G1", "G1+2": "G1"},
                           target=TargetLaser("L", Orientation(False, False)))
    res = execute(make_plan(source, params), output=tmp_path / "c.lbrn2")
    out = load_project(res.output)
    assert len(out.items) == 3 and all(shapes(out, it.id) == shapes(source, "G1") for it in out.items)


def test_verifier_rejects_other_header_changes(write_project, tmp_path):
    path = write_project(project([card(10, 20)]))
    source = load_project(path)
    plan = make_plan(source, ArrangeParams(1, 3, 3, BOARD, target=TargetLaser("L", Orientation(False, True))))
    res = execute(plan, output=tmp_path / "v.lbrn2")
    out = res.output.read_bytes()
    moves = {1: plan.moves_file["G1"]}
    header = {"DeviceName": "L", "MirrorX": "False", "MirrorY": "True"}
    assert verify_output(path.read_bytes(), out, moves, header=header) == []
    assert "header_mismatch" in verify_output(path.read_bytes(), out, moves, header={**header, "DeviceName": "X"})
    bad = out.replace(b'FormatVersion="1"', b'FormatVersion="2"')
    assert verify_output(path.read_bytes(), bad, moves, header=header)
    assert verify_output(path.read_bytes(), out, moves)  # bez povolení změny hlavičky = chyba

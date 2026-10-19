"""Více desek (spec. v1.29 kap. 23.1): plánování, stránky LightBurnu, samostatné soubory, vstup se stránkami."""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from grid_arranger.adapters.lightburn.coords import Orientation
from grid_arranger.adapters.lightburn.pages import page_groups
from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.xmltree import parse
from grid_arranger.application.arrange_job import (
    AUTO_COLUMNS, ArrangeParams, MaterialInput, TargetLaser, execute_job, make_job,
)
from grid_arranger.domain.errors import GridError

from .lbrn2_builder import I, Group, Text, card, project, rect


def write(tmp_path, data, name="b.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


@dataclass
class PageG:
    name: str
    shapes: list

    def lines(self, ind: str, world=I) -> list[str]:
        out = [f'{ind}<Shape Type="Group" SubType="Page" Name="{self.name}">', f"{ind}    <XForm>1 0 0 1 0 0</XForm>"]
        if not self.shapes:
            return out + [f"{ind}    <Children/>", f"{ind}</Shape>"]
        out.append(f"{ind}    <Children>")
        for s in self.shapes:
            out += s.lines(ind + "        ", I)
        return out + [f"{ind}    </Children>", f"{ind}</Shape>"]


# deska 230 × 150, okraje 5 → plocha 220 × 140: kartičky 100 × 60 s mezerou 5 → 2 × 2 = 4 na desku
BOARD = MaterialInput(230, 150)


def params(order=None, **kw):
    base = dict(columns=AUTO_COLUMNS, gap_x=5, gap_y=5, material=BOARD, order=order, boards="sequential",
                board_name="{page} – deska {n}")
    base.update(kw)
    return ArrangeParams(**base)


def cards(n, **kw):
    return project([card(0, 400 + 70 * i, text=f"K{i + 1}") for i in range(n)], mirror_x=False, **kw)


def counts(job):
    return [len(b.layout.placements) for b in job.boards]


def test_single_board_when_everything_fits(tmp_path):
    job = make_job(load_project(write(tmp_path, cards(3))), params())
    assert counts(job) == [3] and job.can_save and job.names == []


def test_sequential_even_and_none(tmp_path):
    p = load_project(write(tmp_path, cards(9)))
    assert counts(make_job(p, params())) == [4, 4, 1]
    even = make_job(p, params(boards="even"))
    assert counts(even) == [3, 3, 3] and even.can_save
    none = make_job(p, params(boards="none"))
    assert counts(none) == [9] and not none.can_save  # bez rozdělení: přesah desky
    seq = make_job(p, params())
    assert [pl.item_id for b in seq.boards for pl in sorted(b.layout.placements, key=lambda x: x.index)] == \
        [f"G{i}" for i in range(1, 10)]  # každý kus právě jednou, v pořadí
    assert seq.names == ["Stránka 1 – deska 2", "Stránka 1 – deska 3"]


def test_fill_last_board(tmp_path):
    p = load_project(write(tmp_path, cards(5)))
    job = make_job(p, params(fill_last=True))
    assert counts(job) == [4, 4] and job.can_save
    assert len(job.filled) == 3 and set(job.filled.values()) == {"G5"}


def test_by_product_with_fill(tmp_path):
    p = load_project(write(tmp_path, cards(2)))
    copies = {f"G1+{k}": "G1" for k in range(1, 5)} | {f"G2+{k}": "G2" for k in range(1, 3)}
    order = ("G1", *[f"G1+{k}" for k in range(1, 5)], "G2", "G2+1", "G2+2")
    job = make_job(p, params(order, copies=copies, boards="product", board_name="{page} – deska {n}",
                             labels={"G2": "Klíčenka"}))
    assert counts(job) == [4, 1, 3]
    srcs = [{job.copies.get(pl.item_id, pl.item_id) for pl in b.layout.placements} for b in job.boards]
    assert srcs == [{"G1"}, {"G1"}, {"G2"}]
    assert job.names == ["Stránka 1 – deska 2 – K1", "Stránka 1 – deska 3 – Klíčenka"]
    filled = make_job(p, params(order, copies=copies, boards="product", fill_last=True))
    assert counts(filled) == [4, 4, 4]
    assert [{filled.copies.get(pl.item_id, pl.item_id) for pl in b.layout.placements} for b in filled.boards] == srcs


def test_item_too_large_blocks(tmp_path):
    p = load_project(write(tmp_path, project([card(0, 0, 300, 60, text="X"), card(0, 100)], mirror_x=False)))
    job = make_job(p, params())
    assert not job.can_save
    with pytest.raises(GridError) as e:
        execute_job(job, out_dir=tmp_path)
    assert e.value.code == "validation_failed"


def test_boards_written_as_pages_and_verified(tmp_path):
    src = write(tmp_path, cards(9))
    before = src.read_bytes()
    job = make_job(load_project(src), params())
    res = execute_job(job, out_dir=tmp_path)
    assert res.problems == [] and src.read_bytes() == before
    root = parse(res.output.read_bytes())
    assert [g.attrs["Name"] for g in page_groups(root)] == ["Stránka 1 – deska 2", "Stránka 1 – deska 3"]
    labels = [[it.label for it in load_project(res.output, k).items] for k in range(3)]
    assert labels == [["K1", "K2", "K3", "K4"], ["K5", "K6", "K7", "K8"], ["K9"]]
    for k in range(3):  # každá deska v rohu u počátku
        q = load_project(res.output, k)
        assert min(it.screen_bounds.left for it in q.items) == pytest.approx(5)
        assert min(it.screen_bounds.top for it in q.items) == pytest.approx(5)
    proto = json.loads(res.protocol.read_text(encoding="utf-8"))
    assert [b["pieces"] for b in proto["boards"]] == [4, 4, 1] and proto["pieces_per_item"]["G9"] == 1


def test_boards_as_separate_files(tmp_path):
    src = write(tmp_path, cards(6))
    job = make_job(load_project(src), params())
    res = execute_job(job, out_dir=tmp_path, separate=True, file_word="deska")
    assert [p.name for p in res.outputs] == ["b__grid_001__deska1.lbrn2", "b__grid_001__deska2.lbrn2"]
    a, b = load_project(res.outputs[0]), load_project(res.outputs[1])
    assert [it.label for it in a.items] == ["K1", "K2", "K3", "K4"] and len(a.pages) == 1
    assert [it.label for it in b.items] == ["K5", "K6"] and len(b.pages) == 1
    proto = json.loads(res.protocol.read_text(encoding="utf-8"))
    assert len(proto["output"]) == 2


def test_separate_files_with_copies_only_on_later_board(tmp_path):
    src = write(tmp_path, cards(1))
    copies = {f"G1+{k}": "G1" for k in range(1, 6)}
    job = make_job(load_project(src), params(("G1", *copies), copies=copies))
    assert counts(job) == [4, 2]
    res = execute_job(job, out_dir=tmp_path, separate=True)
    assert [len(load_project(p).items) for p in res.outputs] == [4, 2]
    res2 = execute_job(job, out_dir=tmp_path)  # stránky
    assert [len(load_project(res2.output, k).items) for k in range(2)] == [4, 2]


def test_original_moved_to_later_board_is_removed_from_first_page(tmp_path):
    # kopie před originálem: originál G1 skončí na desce 2, na první stránce ho nahradí přesun
    src = write(tmp_path, cards(4))
    copies = {"G4+1": "G4"}
    order = ("G4+1", "G2", "G3", "G1", "G4")
    job = make_job(load_project(src), params(order, copies=copies))
    assert counts(job) == [4, 1]
    res = execute_job(job, out_dir=tmp_path)
    assert [it.label for it in load_project(res.output, 0).items] == ["K1", "K2", "K3", "K4"]
    assert [it.label for it in load_project(res.output, 1).items] == ["K4"]


def test_arrange_second_page_keeps_other_pages(tmp_path):
    other1 = card(0, 0, text="P1")
    page2 = PageG("Druha", [card(0, 400 + 70 * i, text=f"D{i}") for i in range(6)])
    page3 = PageG("Treti", [card(50, 50, text="T")])
    data = project([other1, page2, page3], mirror_x=False)
    src = write(tmp_path, data)
    p = load_project(src, page=1)
    assert [it.label for it in p.items] == [f"D{i}" for i in range(6)]
    job = make_job(p, params())
    assert counts(job) == [4, 2] and job.names == ["Druha – deska 2"]
    res = execute_job(job, out_dir=tmp_path)
    out = res.output.read_bytes()
    root = parse(out)
    assert [g.attrs["Name"] for g in page_groups(root)] == ["Druha", "Druha – deska 2", "Treti"]
    assert [it.label for it in load_project(res.output, 0).items] == ["P1"]
    assert load_project(res.output, 0).items[0].file_bbox == load_project(src, 0).items[0].file_bbox
    assert [it.label for it in load_project(res.output, 3).items] == ["T"]
    assert [len(load_project(res.output, k).items) for k in (1, 2)] == [4, 2]


def test_empty_page_and_unknown_page(tmp_path):
    data = project([card(0, 0, text="A"), PageG("Prazdna", [])], mirror_x=False)
    p = load_project(write(tmp_path, data), page=1)
    assert p.items == [] and [x.name for x in p.pages] == ["Stránka 1", "Prazdna"]
    with pytest.raises(GridError) as e:
        load_project(write(tmp_path, data, "c.lbrn2"), page=5)
    assert e.value.code == "unknown_page"


def test_shared_geometry_definer_moves_to_later_board(tmp_path):
    outline = rect(0, 0, 100, 60)
    shapes = [Group([outline, Text("A", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 0, 400))]
    shapes += [Group([rect(0, 0, 100, 60, share_from=outline), Text(f"S{i}", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 0, 480 + 70 * i))
               for i in range(5)]
    src = write(tmp_path, project(shapes, mirror_x=False))
    order = ("G2", "G3", "G4", "G5", "G1", "G6")  # definující skupina G1 až na desce 2
    job = make_job(load_project(src), params(order))
    assert counts(job) == [4, 2]
    res = execute_job(job, out_dir=tmp_path)
    for k in range(2):
        q = load_project(res.output, k)
        assert all(it.supported for it in q.items)
        for it in q.items:
            assert it.file_bbox[2] - it.file_bbox[0] == pytest.approx(100)


def test_mirrored_conversion_refuses_other_pages(tmp_path):
    data = project([card(0, 0, text="A"), PageG("Druha", [card(0, 0, text="B")])], mirror_x=True)
    p = load_project(write(tmp_path, data))
    with pytest.raises(GridError) as e:
        make_job(p, params(boards="none", target=TargetLaser("L", Orientation(False, True))))
    assert e.value.code == "convert_needs_whole_project"


def test_keep_policy_obstacle_only_on_first_board(tmp_path):
    # nevybraný výrobek v rohu desky 1 zabírá místo jen na první desce
    data = project([card(120, 80, 20, 20, text="X")] + [card(0, 400 + 70 * i, text=f"K{i}") for i in range(5)], mirror_x=False)
    p = load_project(write(tmp_path, data))
    job = make_job(p, params(tuple(f"G{i}" for i in range(2, 7))))
    assert counts(job) == [3, 2] and job.can_save
    res = execute_job(job, out_dir=tmp_path)
    assert [it.label for it in load_project(res.output, 0).items][0] == "X"

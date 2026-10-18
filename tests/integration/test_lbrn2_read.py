"""Čtení `.lbrn2`: T-FMT-01…03, 05; T-MVP-07, 25; LB-04, 05, 06, 08, 10 (spec. kap. 14.2, 26.1, 41.5)."""

from __future__ import annotations

import math

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.domain import GridError, Rect

from .lbrn2_builder import Group, Path, Raw, Text, card, project, rect


def codes(item):
    return [r.code for r in item.reasons]


# --- T-FMT-01: platný projekt --------------------------------------------------------------


def test_t_fmt01_valid_project_items_and_info(write_project):
    p = load_project(write_project(project([card(10, 20, text="A"), card(200, 20, 80, 50, text="B")])))
    assert p.info.app_version == "2.2.00" and p.info.device_name == "Syntetický laser"
    assert p.info.orientation.origin == "top_right"
    assert p.info.layer_names == {"1": "C01", "2": "C02"}
    a, b = p.items
    assert a.supported and b.supported
    assert (a.id, a.label, a.outline_layer) == ("G1", "A", "C02")
    assert a.file_bbox == (10, 20, 110, 80)
    assert b.file_bbox == (200, 20, 280, 70)
    assert p.loose == []


# --- LB-06: orientace ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "mx, origin, expected",
    [(True, "top_right", Rect(-110, 20, -10, 80)), (False, "top_left", Rect(10, 20, 110, 80))],
)
def test_lb06_verified_orientations(write_project, mx, origin, expected):
    p = load_project(write_project(project([card(10, 20)], mirror_x=mx, mirror_y=True)))
    assert p.info.orientation.origin == origin
    assert p.items[0].screen_bounds == expected


@pytest.mark.parametrize(
    "mx, origin, expected",
    [(False, "bottom_left", Rect(10, -80, 110, -20)), (True, "bottom_right", Rect(-110, -80, -10, -20))],
)
def test_bottom_origins_are_loaded_with_y_up(write_project, mx, origin, expected):
    # diodové lasery (GRBL) mají počátek často vlevo / vpravo dole: osa Y souboru míří nahoru (spec. v1.22)
    p = load_project(write_project(project([card(10, 20)], mirror_x=mx, mirror_y=False)))
    assert p.info.orientation.origin == origin and p.info.orientation.verified  # KAL-04
    assert p.items[0].screen_bounds == expected


# --- T-FMT-02/03: formát a poškozený obsah -------------------------------------------------


def test_t_fmt02_legacy_lbrn_rejected(write_project):
    with pytest.raises(GridError) as e:
        load_project(write_project(project([card(0, 0)]), name="stary.lbrn"))
    assert e.value.code == "legacy_format"


def test_other_extension_rejected(write_project):
    with pytest.raises(GridError) as e:
        load_project(write_project(b"<svg/>", name="x.svg"))
    assert e.value.code == "not_lbrn2"


@pytest.mark.parametrize(
    "data, code",
    [
        (b"this is not xml", "xml_malformed"),
        (b"<LightBurnProject><Shape></LightBurnProject>", "xml_malformed"),
        (b'<?xml version="1.0"?><svg/>', "not_lightburn_project"),
        (b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><LightBurnProject/>', "xml_dtd_forbidden"),
        (b'<?xml version="1.0" encoding="ISO-8859-1"?><LightBurnProject/>', "xml_encoding"),
    ],
)
def test_t_fmt03_bad_content_rejected(write_project, data, code):
    with pytest.raises(GridError) as e:
        load_project(write_project(data))
    assert e.value.code == code


# --- T-MVP-25 / LB-10: verze --------------------------------------------------------------


@pytest.mark.parametrize("app, fmt", [("2.3.00", "1"), ("1.7.08", "1"), ("2.2.00", "2"), ("", "1")])
def test_t_mvp25_unknown_version_rejected(write_project, app, fmt):
    with pytest.raises(GridError) as e:
        load_project(write_project(project([card(0, 0)], app=app, fmt=fmt)))
    assert e.value.code == "unsupported_version"


# --- T-FMT-05: neznámé kritické struktury --------------------------------------------------


def test_t_fmt05_unknown_top_level_element_rejected(write_project):
    with pytest.raises(GridError) as e:
        load_project(write_project(project([card(0, 0)], extra_top='<Page Index="1"/>')))
    assert e.value.code == "unknown_element"


def test_unknown_project_attribute_rejected(write_project):
    with pytest.raises(GridError) as e:
        load_project(write_project(project([card(0, 0)], extra_root_attrs=' Page1Name="Druhá"')))
    assert e.value.code == "unknown_project_attribute"


# --- T-MVP-07 / LB-08: nepodporované skupiny ----------------------------------------------


def test_unknown_shape_type_inside_item_blocks(write_project):
    g = Group([rect(0, 0, 100, 60), Raw('<Shape Type="Bitmap" CutIndex="3" W="10" H="10"><XForm>1 0 0 1 5 5</XForm></Shape>')])
    it = load_project(write_project(project([g]))).items[0]
    assert not it.supported and "unsupported_shape_type" in codes(it)


def test_locked_or_unknown_group_attribute_blocks(write_project):
    it = load_project(write_project(project([card(0, 0, extra_attrs=' Locked="1"')]))).items[0]
    assert not it.supported and "unknown_group_attribute" in codes(it)


def test_group_without_closed_outline_blocks(write_project):
    g = Group([rect(0, 0, 100, 60, prims="L0 1L1 2L2 3")])  # otevřená cesta
    it = load_project(write_project(project([g]))).items[0]
    assert codes(it) == ["no_outline"]


def test_content_outside_outline_blocks(write_project):
    g = Group([rect(0, 0, 100, 60), rect(90, 10, 30, 10, cut=1)])  # vyčnívá o 20 mm
    it = load_project(write_project(project([g]))).items[0]
    assert codes(it) == ["content_outside_outline"]


def test_duplicate_outline_is_ambiguous(write_project):
    g = Group([rect(0, 0, 100, 60, cut=2), rect(0, 0, 100, 60, cut=1)])
    it = load_project(write_project(project([g]))).items[0]
    assert codes(it) == ["ambiguous_outline"]


def test_text_backup_mismatch_blocks(write_project):
    g = Group([rect(0, 0, 100, 60), Text("X", (5, 5, 20, 10), backup_offset=(3, 0))], xform=(1, 0, 0, 1, 50, 50))
    it = load_project(write_project(project([g]))).items[0]
    assert "text_backup_mismatch" in codes(it)


def test_text_without_backup_is_warning_only(write_project):
    g = Group([rect(0, 0, 100, 60), Text("bez geometrie", (0, 0, 1, 1), backup=False)])
    it = load_project(write_project(project([g]))).items[0]
    assert it.supported
    assert [w.code for w in it.warnings] == ["text_unmeasurable"]
    assert it.content_bbox is None  # jako překážka by nebyl změřitelný


def test_text_backup_outside_outline_blocks(write_project):
    g = Group([rect(0, 0, 100, 60), Text("dlouhý", (5, 5, 150, 10))])
    it = load_project(write_project(project([g]))).items[0]
    assert "content_outside_outline" in codes(it)


# --- geometrie ------------------------------------------------------------------------------


def test_lb04_nested_subgroup_is_measured(write_project):
    inner = Group([rect(10, 10, 20, 20, cut=1)], xform=(1, 0, 0, 1, 5, 5))
    g = Group([rect(0, 0, 100, 60), inner], xform=(1, 0, 0, 1, 100, 0))
    it = load_project(write_project(project([g]))).items[0]
    assert it.supported and it.file_bbox == (100, 0, 200, 60)


def test_shared_vertlist_by_id(write_project):
    outline = rect(0, 0, 100, 60)
    copy = Path(outline.corners, cut=1, share_from=outline)  # stejné VertID, bez vlastního seznamu
    g1 = Group([outline], xform=(1, 0, 0, 1, 0, 0))
    g2 = Group([copy], xform=(1, 0, 0, 1, 300, 0))
    p = load_project(write_project(project([g1, g2])))
    assert p.items[1].supported and p.items[1].file_bbox == (300, 0, 400, 60)


def test_bezier_outline_closed_chain_and_exact_bbox(write_project):
    o = rect(0, 0, 100, 60, prims="B0 1B1 2B2 3B3 0", bezier_ctrl=True)
    it = load_project(write_project(project([Group([o])]))).items[0]
    assert it.supported
    # řídicí body ±1 mm vybočí křivku jen o max. 3·t(1−t)(1−2t) = √3/6 mm (extrém Bézierovy křivky)
    bulge = math.sqrt(3) / 6
    assert it.file_bbox == pytest.approx((-bulge, 0, 100 + bulge, 60))


def test_scaled_group_transform_applies(write_project):
    g = Group([rect(0, 0, 100, 60)], xform=(2, 0, 0, 2, 10, 10))
    it = load_project(write_project(project([g]))).items[0]
    assert it.file_bbox == (10, 10, 210, 130)


# --- LB-05: volné objekty jako překážky -----------------------------------------------------


def test_lb05_loose_objects_become_obstacles(write_project):
    loose_path = rect(500, 500, 10, 10, cut=1)
    bitmap = Raw('<Shape Type="Bitmap" CutIndex="3" W="10" H="10"><XForm>1 0 0 1 0 0</XForm></Shape>')
    p = load_project(write_project(project([card(0, 0), loose_path, bitmap])))
    obs = {o.id: o for o in p.obstacles_for({"G1"})}
    assert obs["S2"].bounds == Rect(-510, 500, -500, 510)  # MirrorX → zrcadlené X
    assert obs["S3"].bounds is None  # bitmapa: nezměřitelná → blokuje uložení
    obs_none = {o.id for o in p.obstacles_for(set())}
    assert "G1" in obs_none  # nevybraný výrobek je překážka

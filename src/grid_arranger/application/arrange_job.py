"""Orchestrace úlohy MVP (spec. kap. 21.5): načtení → plán → validace → zápis → kontrola → protokol.

Souřadnice zadávané uživatelem jsou **souřadnice LightBurnu/stroje** — tytéž hodnoty
X/Y, které ukazuje LightBurn (KAL-00), tj. vzdálenosti od počátku laseru.

Umístění mřížky (spec. v1.10, kap. 12.3):

* ``origin`` (výchozí) — roh mřížky nejbližší počátku laseru leží v rohu využitelné
  plochy desky u počátku (deska u počátku + okraj),
* ``center`` — mřížka uprostřed využitelné plochy desky,
* ``manual`` — roh mřížky u počátku na zadaných souřadnicích LightBurnu,
* ``selection`` — levý horní roh (na obrazovce) původní polohy vybraných výrobků.

Pořadí plnění: ``origin`` (výchozí) začíná v rohu počátku laseru, ``reading`` vlevo nahoře.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..adapters.lightburn.read import LoadedProject, load_project
from ..adapters.lightburn.write import apply_patches, next_output_path, plan_patches, write_new_file
from ..core import arrange_to_grid, validate_layout
from ..core.collision import ValidationReport, usable_area
from ..domain.errors import GridError
from ..domain.models import Corner, GridRequest, Item, LayoutResult, MaterialSpec
from ..safety.verify import verify_output
from ..version import __version__

ANCHORS = ("origin", "center", "manual", "selection")
FILL_MODES = ("origin", "reading")
DEFAULT_MARGIN_MM = 5.0


@dataclass(frozen=True, slots=True)
class MaterialInput:
    """Deska: rozměr a poloha jejího rohu u počátku v souřadnicích LightBurnu (obvykle 0, 0).

    Okraje jsou vizuální (vlevo/vpravo/nahoře/dole na obrazovce).
    """

    width: float
    height: float
    x: float = 0.0
    y: float = 0.0
    margin_left: float = DEFAULT_MARGIN_MM
    margin_right: float = DEFAULT_MARGIN_MM
    margin_top: float = DEFAULT_MARGIN_MM
    margin_bottom: float = DEFAULT_MARGIN_MM


@dataclass(slots=True)
class ArrangeParams:
    columns: int
    gap_x: float
    gap_y: float
    material: MaterialInput | None
    order: tuple[str, ...] | None = None
    """Vybrané výrobky v požadovaném pořadí; None = všechny podporované v pořadí dokumentu."""
    anchor: str = "origin"
    start: tuple[float, float] | None = None
    """Pro ``anchor="manual"``: roh mřížky u počátku laseru v souřadnicích LightBurnu."""
    fill: str = "origin"


@dataclass(slots=True)
class Plan:
    project: LoadedProject
    request: GridRequest
    layout: LayoutResult
    report: ValidationReport
    moves_file: dict[str, tuple[float, float]]
    origin_corner_lightburn: tuple[float, float]
    """Roh mřížky nejbližší počátku laseru v souřadnicích LightBurnu."""
    anchor: str
    fill: str


@dataclass(slots=True)
class JobResult:
    plan: Plan
    output: Path | None = None
    protocol: Path | None = None
    problems: list[str] = field(default_factory=list)


def material_to_core(project: LoadedProject, m: MaterialInput) -> MaterialSpec:
    """Převede desku do souřadnic jádra. Neplatné rozměry nechá na validátoru (chyba invalid_material)."""
    o = project.info.orientation
    r = o.to_screen_rect((m.x, m.y, m.x + max(m.width, 0.0), m.y + max(m.height, 0.0)))
    return MaterialSpec(r.left, r.top, m.width, m.height, m.margin_left, m.margin_right, m.margin_top, m.margin_bottom)


def _origin_on_right(project: LoadedProject) -> bool:
    return project.info.orientation.mirror_x


def make_plan(project: LoadedProject, params: ArrangeParams) -> Plan:
    if params.anchor not in ANCHORS:
        raise GridError("invalid_anchor", "Neznámý způsob umístění mřížky.", anchor=params.anchor)
    if params.fill not in FILL_MODES:
        raise GridError("invalid_fill_corner", "Neznámé pořadí plnění.", fill=params.fill)
    supported = [it for it in project.items if it.supported]
    order = params.order if params.order is not None else tuple(it.id for it in supported)
    for item_id in order:
        it = project.item(item_id)
        if not it.supported:
            raise GridError("item_not_supported", "Vybraný výrobek nelze přesunout.", item_id=item_id, reasons=[r.code for r in it.reasons])
    if not order:
        raise GridError("empty_selection", "Není vybrán žádný výrobek.")

    o = project.info.orientation
    right = _origin_on_right(project)
    core_items = [Item(it.id, it.screen_bounds, it.label, it.source_order) for it in supported]
    corner = Corner.TOP_RIGHT if (params.fill == "origin" and right) else Corner.TOP_LEFT
    material = material_to_core(project, params.material) if params.material else None

    # 1. průchod: rozměr mřížky (poloha nehraje roli, výpočet je čistá translace)
    probe = arrange_to_grid(core_items, GridRequest(tuple(order), params.columns, params.gap_x, params.gap_y, 0.0, 0.0, fill_from=corner))
    gw, gh = probe.grid_bounds.width, probe.grid_bounds.height

    # 2. levý horní roh mřížky (souřadnice jádra) podle způsobu umístění
    if params.anchor in ("origin", "center"):
        if material is None:
            raise GridError("material_missing", "Pro umístění na desku je nutné zadat desku.")
        area, issues = usable_area(material)
        if area is None:
            raise GridError(issues[0].code, "Deska nebo okraje jsou neplatné.", **issues[0].params)
        if params.anchor == "origin":
            sx, sy = (area.right - gw if right else area.left), area.top
        else:
            sx, sy = (area.left + area.right - gw) / 2.0, (area.top + area.bottom - gh) / 2.0
    elif params.anchor == "manual":
        if params.start is None:
            raise GridError("invalid_start", "Pro ruční umístění zadejte souřadnice rohu mřížky u počátku.")
        cx, cy = o.to_screen_point(*params.start)
        sx, sy = (cx - gw if right else cx), cy
    else:  # selection
        sel = [project.item(i).screen_bounds for i in order]
        sx, sy = min(r.left for r in sel), min(r.top for r in sel)

    req = GridRequest(tuple(order), params.columns, params.gap_x, params.gap_y, sx, sy, fill_from=corner)
    layout = arrange_to_grid(core_items, req)
    report = validate_layout(layout, req.gap_x, req.gap_y, material, project.obstacles_for(set(order)))
    moves = {p.item_id: o.to_file_delta(p.dx, p.dy) for p in layout.placements}
    g = layout.grid_bounds
    corner_screen = (g.right if right else g.left, g.top)
    return Plan(project, req, layout, report, moves, o.to_file_point(*corner_screen), params.anchor, params.fill)


def _protocol(plan: Plan, output: Path, out_bytes: bytes, problems: list[str]) -> dict:
    p, info = plan.project, plan.project.info
    o = info.orientation
    return {
        "tool": "Grid Arranger for LightBurn",
        "app_version": __version__,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {"path": str(info.path), "sha256": info.sha256, "bytes": info.size},
        "output": {"path": str(output), "sha256": hashlib.sha256(out_bytes).hexdigest(), "bytes": len(out_bytes)},
        "lightburn": {"app_version": info.app_version, "format_version": info.format_version,
                      "device": info.device_name, "origin": o.origin},
        "parameters": {
            "columns": plan.request.columns, "gap_x_mm": plan.request.gap_x, "gap_y_mm": plan.request.gap_y,
            "anchor": plan.anchor, "fill": plan.fill, "order": list(plan.request.ordered_item_ids),
            "grid_corner_at_origin_lightburn_xy": plan.origin_corner_lightburn,
        },
        "grid": {"columns": plan.layout.columns, "rows": plan.layout.rows,
                 "width_mm": plan.layout.grid_bounds.width, "height_mm": plan.layout.grid_bounds.height},
        "placements": [
            {"item": pl.item_id, "label": p.item(pl.item_id).label, "index": pl.index + 1,
             "row": pl.row + 1, "column_from_fill_corner": pl.column + 1,
             "move_lightburn_xy_mm": plan.moves_file[pl.item_id],
             "size_mm": [pl.target_bounds.width, pl.target_bounds.height]}
            for pl in plan.layout.placements
        ],
        "warnings": [{"code": i.code, "items": list(i.item_ids)} for i in plan.report.warnings],
        "verification": {"problems": problems, "passed": not problems},
        "reminder": "Open the output in LightBurn via File > Open and check layers, Preview and position before cutting.",
    }


def execute(plan: Plan, out_dir: Path | None = None) -> JobResult:
    """Zapíše nový projekt jen při platné validaci a úspěšné nezávislé kontrole."""
    if not plan.report.can_save:
        raise GridError("validation_failed", "Rozložení neprošlo kontrolou; nic nebylo uloženo.",
                        codes=sorted({i.code for i in plan.report.errors}))
    project = plan.project
    src_path = project.info.path

    ops = plan_patches(project, plan.moves_file)
    out_bytes = apply_patches(project.data, ops)

    tops = {it.id: it.source_order for it in project.items}
    problems = verify_output(project.data, out_bytes, {tops[k]: v for k, v in plan.moves_file.items()})
    if not problems:
        problems += _check_reloaded_bounds(plan, out_bytes)
    if problems:
        raise GridError("verification_failed", "Kontrola výstupu selhala; nic nebylo uloženo.", problems=problems)

    if hashlib.sha256(src_path.read_bytes()).hexdigest() != project.info.sha256:
        raise GridError("source_changed", "Původní soubor se od načtení změnil; načtěte jej znovu.")

    target = next_output_path(src_path, out_dir)
    write_new_file(target, out_bytes, forbidden=src_path)
    proto_path = target.with_suffix(".json")
    with open(proto_path, "x", encoding="utf-8") as fh:
        json.dump(_protocol(plan, target, out_bytes, problems), fh, ensure_ascii=False, indent=2)

    if hashlib.sha256(src_path.read_bytes()).hexdigest() != project.info.sha256:
        raise GridError("source_changed", "Původní soubor se během zápisu změnil.")
    return JobResult(plan, target, proto_path, problems)


def _check_reloaded_bounds(plan: Plan, out_bytes: bytes) -> list[str]:
    import tempfile

    from ..adapters.lightburn import read as rd

    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d) / "check.lbrn2"
        tmp.write_bytes(out_bytes)
        reloaded = rd.load_project(tmp)
    problems = []
    for pl in plan.layout.placements:
        got = reloaded.item(pl.item_id).screen_bounds
        exp = pl.target_bounds
        if got is None or max(abs(got.left - exp.left), abs(got.top - exp.top),
                              abs(got.right - exp.right), abs(got.bottom - exp.bottom)) > 1e-3:
            problems.append(f"outline_not_at_target: {pl.item_id}")
    for it in plan.project.items:
        if it.id not in plan.moves_file and it.supported:
            if reloaded.item(it.id).file_bbox != it.file_bbox:
                problems.append(f"unselected_moved: {it.id}")
    return problems


def run(path: str | Path, params: ArrangeParams, write: bool = True, out_dir: Path | None = None) -> JobResult:
    project = load_project(path)
    plan = make_plan(project, params)
    if not write:
        return JobResult(plan)
    return execute(plan, out_dir)


__all__ = ["ANCHORS", "FILL_MODES", "ArrangeParams", "JobResult", "MaterialInput", "Plan", "execute", "make_plan", "run"]

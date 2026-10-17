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

Natočení (spec. v1.13 kap. 7.6): ``none`` | ``90`` (jen po 90°) | ``any`` (libovolný úhel —
nejmenší obdélník kolem výrobku). Ve všech režimech se navíc zvolí společná orientace
(beze změny / všechny na šířku / všechny na výšku), která dá nejmenší mřížku, přednostně
takovou, která se vejde na desku. Výrobky v ``no_rotate`` se nenatáčí nikdy.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path

from ..adapters.lightburn.read import LoadedProject, load_project
from ..adapters.lightburn.write import apply_with_copies, next_output_path, plan_patches, write_new_file
from ..core import arrange_to_grid, validate_layout
from ..core.rotation import min_area_angle, rotated_bounds
from ..core.collision import ValidationReport, usable_area
from ..domain.errors import GridError
from ..domain.models import Corner, GridRequest, Item, LayoutResult, MaterialSpec, Rect
from ..safety.verify import verify_output
from ..version import __version__

ANCHORS = ("origin", "center", "manual", "selection")
ROTATION_MODES = ("none", "90", "any")
GEOMETRY_TOL = 0.002  # mm — odchylka rozvinutí křivek; obdélník natočeného výrobku se o ni zvětší
ORIENTATION_GAIN = 0.005  # jiná orientace jen při úspoře aspoň 0,5 % plochy mřížky (nebo když se jinak nevejde)
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
    rotation: str = "none"
    """``none`` | ``90`` | ``any`` (spec. v1.13)."""
    no_rotate: frozenset[str] = frozenset()
    """Výrobky, které se nikdy nenatáčí (výjimky v seznamu)."""
    angles: dict[str, float] = field(default_factory=dict)
    """Ruční natočení výrobků ve stupních (jádro, kladně po směru hodin) — přednost před automatikou,
    platí i v režimu ``none`` (spec. v1.15 kap. 7.6)."""
    copies: dict[str, str] = field(default_factory=dict)
    """Kopie výrobků: ``{id kopie: id zdrojového výrobku}`` (spec. v1.16). Kopie se rozmisťuje jako
    samostatný výrobek, jen pokud je v ``order``; do výstupu se zapíše jako nová skupina."""


class ItemGeometry:
    """Body skutečných křivek výrobků v souřadnicích jádra (pro natočení); výsledky se cachují."""

    def __init__(self, project: LoadedProject) -> None:
        from ..adapters.lightburn.render import ProjectRenderer

        self._renderer = ProjectRenderer(project)
        self._hull: dict[str, list[tuple[float, float]]] = {}
        self._angle: dict[str, float] = {}
        self.aliases: dict[str, str] = {}
        """Kopie → zdrojový výrobek (stejné křivky)."""

    def hull(self, item_id: str) -> list[tuple[float, float]]:
        item_id = self.aliases.get(item_id, item_id)
        if item_id not in self._hull:
            from ..adapters.lightburn.render import stroke_points
            from ..core.rotation import convex_hull

            self._hull[item_id] = convex_hull(stroke_points(self._renderer.strokes(item_id), GEOMETRY_TOL))
        return self._hull[item_id]

    def min_angle(self, item_id: str) -> float:
        item_id = self.aliases.get(item_id, item_id)
        if item_id not in self._angle:
            pts = self.hull(item_id)
            self._angle[item_id] = min_area_angle(pts) if len(pts) >= 3 else 0.0
        return self._angle[item_id]


def _turned_bounds(it, angle: float, geometry: ItemGeometry) -> Rect:
    """Obdélník výrobku po natočení o ``angle`` kolem středu jeho obrysu (souřadnice jádra)."""
    b = it.screen_bounds
    cx, cy = (b.left + b.right) / 2.0, (b.top + b.bottom) / 2.0
    q = round(angle / 90.0)
    if abs(angle - 90.0 * q) < 1e-9:  # násobek 90°: přesně z (konzervativního) obdélníku obrysu
        return rotated_bounds([(b.left, b.top), (b.right, b.bottom)], angle, cx, cy)
    r = rotated_bounds(geometry.hull(it.id), angle, cx, cy)
    t = GEOMETRY_TOL
    return Rect(r.left - t, r.top - t, r.right + t, r.bottom + t)


SQUARE_TOL = 0.01  # mm


def normalize_angle(deg: float) -> float:
    """Úhel do intervalu (−180°, 180°]."""
    d = math.fmod(deg, 360.0)
    if d > 180.0:
        d -= 360.0
    elif d <= -180.0:
        d += 360.0
    return 0.0 if abs(d) < 1e-9 else d


def _choose_rotations(project: LoadedProject, params: ArrangeParams, order: tuple[str, ...], corner: Corner,
                      geometry: ItemGeometry, fit: tuple[float, float] | None) -> dict[str, float]:
    """Úhel pro každý vybraný výrobek (0 = beze změny). Ruční úhly se nikdy nemění."""
    manual = {iid: normalize_angle(a) for iid, a in params.angles.items() if iid in order}
    if params.rotation == "none":
        return {iid: a for iid, a in manual.items() if a}
    base = {}
    for iid in order:
        if iid in manual:
            base[iid] = manual[iid]
        elif iid in params.no_rotate:
            base[iid] = 0.0
        else:
            base[iid] = geometry.min_angle(iid) if params.rotation == "any" else 0.0

    def variant(kind: str) -> dict[str, float]:
        out = {}
        for iid, a in base.items():
            if iid in params.no_rotate or iid in manual or kind == "keep":
                out[iid] = a
                continue
            r = _turned_bounds(project.item(iid), a, geometry)
            if abs(r.width - r.height) <= SQUARE_TOL:  # čtverec / kruh: otočení o 90° nic nezmění
                out[iid] = a
                continue
            landscape = r.width > r.height
            want_landscape = kind == "landscape"
            # o 90° navíc tím směrem, který dá menší celkové natočení (−60° místo 120°)
            out[iid] = a if landscape == want_landscape else (a + 90.0 if a <= 0 else a - 90.0)
        return out

    candidates = []
    # „original“ = nic nenatáčet: natočení se použije, jen když mřížka opravdu vyjde menší
    for kind in ("original", "keep", "landscape", "portrait"):
        angles = {iid: manual.get(iid, 0.0) for iid in base} if kind == "original" else variant(kind)
        items = [Item(it.id, _turned_bounds(it, angles.get(it.id, 0.0), geometry) if it.id in angles else it.screen_bounds,
                      it.label, it.source_order) for it in project.items if it.supported]
        lay = arrange_to_grid(items, GridRequest(order, params.columns, params.gap_x, params.gap_y, 0.0, 0.0, fill_from=corner))
        w, h = lay.grid_bounds.width, lay.grid_bounds.height
        fits = fit is None or (w <= fit[0] + 1e-6 and h <= fit[1] + 1e-6)
        candidates.append((kind, angles, w * h, fits))
    best = candidates[0]
    for c in candidates[1:]:
        better_fit = c[3] and not best[3]
        smaller = c[3] == best[3] and c[2] < best[2] * (1.0 - ORIENTATION_GAIN)
        if better_fit or smaller:
            best = c
    return {iid: a for iid, a in best[1].items() if abs(a) > 1e-9}


def _cos_sin(deg: float) -> tuple[float, float]:
    """Přesné hodnoty pro násobky 90° (žádné 6e-17 v souboru)."""
    q = round(deg / 90.0)
    if abs(deg - 90.0 * q) < 1e-9:
        return ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0))[q % 4]
    r = math.radians(deg)
    return math.cos(r), math.sin(r)


def _screen_to_file(t: tuple[float, ...], sx: float, sy: float) -> tuple[float, ...]:
    """Transformace v souřadnicích jádra → souboru: ``S ∘ T ∘ S`` pro ``S = diag(sx, sy)``."""
    a, b, c, d, e, f = t
    k = sx * sy
    return (a, k * b, k * c, d, sx * e, sy * f)


@dataclass(slots=True)
class Plan:
    project: LoadedProject
    request: GridRequest
    layout: LayoutResult
    report: ValidationReport
    moves_file: dict[str, tuple[float, ...]]
    """Posun ``(dx, dy)`` nebo afinní transformace ``(a, b, c, d, e, f)`` v souřadnicích souboru."""
    origin_corner_lightburn: tuple[float, float]
    """Roh mřížky nejbližší počátku laseru v souřadnicích LightBurnu."""
    anchor: str
    fill: str
    rotations: dict[str, float] = field(default_factory=dict)
    """Natočení výrobků ve stupních (souřadnice jádra, kladně po směru hodin); chybí = 0."""
    pivots: dict[str, tuple[float, float]] = field(default_factory=dict)
    """Střed natočení (střed obrysu v původní poloze, souřadnice jádra)."""
    rotation_mode: str = "none"
    manual: frozenset[str] = frozenset()
    """Výrobky s ručně zadaným úhlem."""
    copies: dict[str, str] = field(default_factory=dict)
    """Rozmístěné kopie ``{id kopie: zdroj}`` v pořadí zápisu do výstupu."""


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


def make_plan(project: LoadedProject, params: ArrangeParams, geometry: ItemGeometry | None = None) -> Plan:
    if params.anchor not in ANCHORS:
        raise GridError("invalid_anchor", "Neznámý způsob umístění mřížky.", anchor=params.anchor)
    if params.fill not in FILL_MODES:
        raise GridError("invalid_fill_corner", "Neznámé pořadí plnění.", fill=params.fill)
    if params.rotation not in ROTATION_MODES:
        raise GridError("invalid_rotation", "Neznámý režim natočení.", rotation=params.rotation)
    if not all(math.isfinite(a) for a in params.angles.values()):
        raise GridError("invalid_rotation", "Neplatný úhel natočení.")
    order = params.order if params.order is not None else tuple(it.id for it in project.items if it.supported)
    copies = {cid: src for cid, src in params.copies.items() if cid in order}
    if copies:
        project = _with_copies(project, copies)
        if geometry is not None:
            geometry.aliases.update(copies)
    supported = [it for it in project.items if it.supported]
    for item_id in order:
        it = project.item(item_id)
        if not it.supported:
            raise GridError("item_not_supported", "Vybraný výrobek nelze přesunout.", item_id=item_id, reasons=[r.code for r in it.reasons])
    if not order:
        raise GridError("empty_selection", "Není vybrán žádný výrobek.")

    o = project.info.orientation
    right = _origin_on_right(project)
    corner = Corner.TOP_RIGHT if (params.fill == "origin" and right) else Corner.TOP_LEFT
    material = material_to_core(project, params.material) if params.material else None

    rotations: dict[str, float] = {}
    if params.rotation != "none" or params.angles:
        if geometry is None:
            geometry = ItemGeometry(project)
            geometry.aliases.update(copies)
        fit = None
        if material is not None and params.anchor in ("origin", "center"):
            area, _ = usable_area(material)
            fit = (area.width, area.height) if area is not None else None
        rotations = _choose_rotations(project, params, tuple(order), corner, geometry, fit)
    core_items = [Item(it.id, _turned_bounds(it, rotations[it.id], geometry) if it.id in rotations else it.screen_bounds,
                       it.label, it.source_order) for it in supported]

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
    moves: dict[str, tuple[float, ...]] = {}
    pivots: dict[str, tuple[float, float]] = {}
    for p in layout.placements:
        if p.item_id not in rotations:
            moves[p.item_id] = o.to_file_delta(p.dx, p.dy)
            continue
        b = project.item(p.item_id).screen_bounds
        cx, cy = (b.left + b.right) / 2.0, (b.top + b.bottom) / 2.0
        cs, sn = _cos_sin(rotations[p.item_id])
        # jádro: T = Tr(dx, dy) ∘ Tr(c) ∘ R ∘ Tr(−c);  x' = a·x + c·y + e
        t = (cs, sn, -sn, cs, cx - cs * cx + sn * cy + p.dx, cy - sn * cx - cs * cy + p.dy)
        moves[p.item_id] = _screen_to_file(t, o.sx, o.sy)
        pivots[p.item_id] = (cx, cy)
    g = layout.grid_bounds
    corner_screen = (g.right if right else g.left, g.top)
    return Plan(project, req, layout, report, moves, o.to_file_point(*corner_screen), params.anchor, params.fill,
                {k: v for k, v in rotations.items() if k in moves}, pivots, params.rotation,
                frozenset(k for k in params.angles if k in moves),
                {cid: copies[cid] for cid in order if cid in copies})


def _with_copies(project: LoadedProject, copies: dict[str, str]) -> LoadedProject:
    """Projekt doplněný o kopie výrobků (stejný uzel, rozměry i poloha jako zdroj, vlastní id)."""
    extra = []
    for cid, src in copies.items():
        if cid in {it.id for it in project.items}:
            raise GridError("duplicate_item", "Kopie má stejné označení jako existující výrobek.", item_id=cid)
        it = project.item(src)
        if not it.supported:
            raise GridError("item_not_supported", "Nepodporovaný výrobek nelze kopírovat.", item_id=src)
        extra.append(replace(it, id=cid, reasons=list(it.reasons), warnings=list(it.warnings)))
    return replace(project, items=[*project.items, *extra])


def _move_xy(m: tuple[float, ...]) -> tuple[float, float]:
    return (m[0], m[1]) if len(m) == 2 else (m[4], m[5])


def _rotation_mode(plan: Plan) -> str:
    return plan.rotation_mode


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
            "rotation_mode": _rotation_mode(plan),
            "grid_corner_at_origin_lightburn_xy": plan.origin_corner_lightburn,
        },
        "grid": {"columns": plan.layout.columns, "rows": plan.layout.rows,
                 "width_mm": plan.layout.grid_bounds.width, "height_mm": plan.layout.grid_bounds.height},
        "placements": [
            {"item": pl.item_id, "label": p.item(pl.item_id).label, "index": pl.index + 1,
             "copy_of": plan.copies.get(pl.item_id),
             "row": pl.row + 1, "column_from_fill_corner": pl.column + 1,
             "move_lightburn_xy_mm": _move_xy(plan.moves_file[pl.item_id]),
             "rotation_deg_screen_clockwise": plan.rotations.get(pl.item_id, 0.0),
             "rotation_manual": pl.item_id in plan.manual,
             "transform_lightburn": list(plan.moves_file[pl.item_id]) if len(plan.moves_file[pl.item_id]) == 6 else None,
             "size_mm": [pl.target_bounds.width, pl.target_bounds.height]}
            for pl in plan.layout.placements
        ],
        "warnings": [{"code": i.code, "items": list(i.item_ids)} for i in plan.report.warnings],
        "verification": {"problems": problems, "passed": not problems},
        "reminder": "Open the output in LightBurn via File > Open and check layers, Preview and position before cutting.",
    }


PROTOCOL_BESIDE = "beside"
PROTOCOL_NONE = "none"


def _protocol_path(target: Path, protocol: str | Path) -> Path | None:
    """Kam zapsat protokol: vedle výstupu (``<název>.json``), do zvolené složky (bez přepsání: ``_2``, ``_3``…), nebo nikam."""
    if protocol == PROTOCOL_NONE:
        return None
    if protocol == PROTOCOL_BESIDE:
        return target.with_suffix(".json")
    folder = Path(protocol)
    folder.mkdir(parents=True, exist_ok=True)
    cand = folder / f"{target.stem}.json"
    n = 2
    while cand.exists():
        cand = folder / f"{target.stem}_{n}.json"
        n += 1
    return cand


def check_output_path(target: Path, source: Path, protocol: str | Path = PROTOCOL_BESIDE) -> Path:
    """Cíl zvolený uživatelem: přípona ``.lbrn2``, nikdy originál, nikdy existující soubor (ani protokol vedle něj)."""
    target = Path(target)
    if target.suffix.lower() != ".lbrn2":
        target = target.with_name(target.name + ".lbrn2")
    if target.resolve() == source.resolve():
        raise GridError("would_overwrite_source", "Výstup by přepsal originál.")
    if target.exists() or (protocol == PROTOCOL_BESIDE and target.with_suffix(".json").exists()):
        raise GridError("output_exists", "Výstupní soubor už existuje.", path=str(target))
    if not target.parent.is_dir():
        raise GridError("write_failed", "Složka neexistuje.", detail=str(target.parent))
    return target


def execute(plan: Plan, out_dir: Path | None = None, output: Path | None = None,
            protocol: str | Path = PROTOCOL_BESIDE) -> JobResult:
    """Zapíše nový projekt jen při platné validaci a úspěšné nezávislé kontrole.

    ``output`` = cesta zvolená uživatelem (jinak ``puvodni__grid_NNN.lbrn2`` vedle originálu / v ``out_dir``).
    ``protocol`` = ``"beside"`` (vedle výstupu), ``"none"`` (nezapisovat) nebo složka pro protokoly.
    """
    if not plan.report.can_save:
        raise GridError("validation_failed", "Rozložení neprošlo kontrolou; nic nebylo uloženo.",
                        codes=sorted({i.code for i in plan.report.errors}))
    project = plan.project
    src_path = project.info.path

    originals = {k: v for k, v in plan.moves_file.items() if k not in plan.copies}
    copy_moves = [(src, plan.moves_file[cid]) for cid, src in plan.copies.items()]
    ops = plan_patches(project, originals)
    out_bytes = apply_with_copies(project, ops, copy_moves)

    tops = {it.id: it.source_order for it in project.items if it.id not in plan.copies}
    problems = verify_output(project.data, out_bytes, {tops[k]: v for k, v in originals.items()},
                             [(tops[src], move) for src, move in copy_moves])
    if not problems:
        problems += _check_reloaded_bounds(plan, out_bytes)
    if problems:
        raise GridError("verification_failed", "Kontrola výstupu selhala; nic nebylo uloženo.", problems=problems)

    if hashlib.sha256(src_path.read_bytes()).hexdigest() != project.info.sha256:
        raise GridError("source_changed", "Původní soubor se od načtení změnil; načtěte jej znovu.")

    target = check_output_path(output, src_path, protocol) if output is not None else next_output_path(src_path, out_dir)
    proto_path = _protocol_path(target, protocol)
    write_new_file(target, out_bytes, forbidden=src_path)
    if proto_path is not None:
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
    geo_out = None
    n_top = len(plan.project.root.findall("Shape"))
    reload_id = {cid: f"G{n_top + k}" for k, cid in enumerate(plan.copies, start=1)}
    if len(reloaded.items) != len([it for it in plan.project.items if it.id not in plan.copies]) + len(plan.copies):
        return ["copy_count_mismatch"]
    for pl in plan.layout.placements:
        exp = pl.target_bounds
        rid = reload_id.get(pl.item_id, pl.item_id)
        if pl.item_id in plan.rotations:
            # natočený výrobek: skutečné křivky znovu načteného výstupu musí ležet v cílovém obdélníku
            if geo_out is None:
                geo_out = ItemGeometry(reloaded)
            pts = geo_out.hull(rid)
            q = round(plan.rotations[pl.item_id] / 90.0)
            if abs(plan.rotations[pl.item_id] - 90.0 * q) < 1e-9:
                got = reloaded.item(rid).screen_bounds
            else:
                got = Rect(min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts))
                got = Rect(got.left - GEOMETRY_TOL, got.top - GEOMETRY_TOL, got.right + GEOMETRY_TOL, got.bottom + GEOMETRY_TOL)
            tol = 1e-3 if abs(plan.rotations[pl.item_id] - 90.0 * q) < 1e-9 else 0.02
        else:
            got = reloaded.item(rid).screen_bounds
            tol = 1e-3
        if got is None or max(abs(got.left - exp.left), abs(got.top - exp.top),
                              abs(got.right - exp.right), abs(got.bottom - exp.bottom)) > tol:
            problems.append(f"outline_not_at_target: {pl.item_id}")
    for it in plan.project.items:
        if it.id not in plan.moves_file and it.supported and it.id not in plan.copies:
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

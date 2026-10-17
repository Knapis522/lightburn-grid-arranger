"""Čtení projektu `.lbrn2` a rozpoznání výrobků (spec. kap. 5, 9.1, 41; KAL-00).

Výsledkem je :class:`LoadedProject`: informace o projektu, výrobky (nejvyšší skupiny)
se stavem podporováno/blokováno a důvody, a překážky pro kontrolu kolizí.
Soubor se nikdy nemění.

Konzervativní pravidla (spec. kap. 13 „neznámé = unsupported“):

* podporovaná verze: ``AppVersion`` 2.2.x, ``FormatVersion`` 1;
* podporovaná orientace: ``MirrorY="True"`` (ověřeno KAL-00);
* uvnitř výrobku jsou dovoleny jen ověřené typy ``Group``, ``Path``, ``Text`` a nativní tvary
  ``Ellipse``, ``Rect``, ``Polygon`` (:mod:`.shapes`; neověřené varianty se blokují).
  Neznámý typ může nést souřadnice ve světovém systému (jako ``BackupPath``)
  a po přesunu by zůstal na místě → výrobek se blokuje.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from pathlib import Path

from ...domain.errors import GridError
from ...domain.models import Obstacle, Rect
from ...core.tolerance import EPSILON
from . import geometry as geo
from . import shapes
from .coords import Orientation
from .xmltree import Node, parse

MAX_FILE_BYTES = 64 * 1024 * 1024
SUPPORTED_APP_VERSION_PREFIXES = ("2.2.",)
SUPPORTED_FORMAT_VERSIONS = ("1",)
KNOWN_ROOT_CHILDREN = {"Thumbnail", "VariableText", "UIPrefs", "CutSetting", "Shape", "Notes"}
KNOWN_ROOT_ATTRS = {
    "AppVersion", "DeviceName", "FormatVersion", "MaterialHeight", "MirrorX", "MirrorY",
    "AskForSendName", "CurrentPage", "Page0Name",
}
GROUP_ATTRS = {"Type", "CutIndex"}
GROUP_CHILDREN = {"XForm", "Children"}
PATH_CHILDREN = {"XForm", "VertList", "PrimList"}
TEXT_CHILDREN = {"XForm", "BackupPath"}
BACKUP_TOLERANCE = 0.01  # mm; shoda XForm(BackupPath) se složenou transformací textu


@dataclass(frozen=True, slots=True)
class Reason:
    code: str
    params: dict = field(default_factory=dict)


@dataclass(slots=True)
class ProjectInfo:
    path: Path
    sha256: str
    size: int
    app_version: str
    format_version: str
    device_name: str
    orientation: Orientation
    layer_names: dict[str, str]


@dataclass(slots=True)
class SourceItem:
    id: str
    source_order: int
    label: str
    node: Node
    supported: bool
    reasons: list[Reason]
    warnings: list[Reason]
    file_bbox: geo.BBox | None
    """AABB řezného obrysu v souřadnicích souboru (jen u podporovaných)."""
    outline_layer: str | None
    content_bbox: geo.BBox | None
    """AABB veškerého změřitelného obsahu; ``None`` pokud něco nelze změřit."""
    screen_bounds: Rect | None = None


@dataclass(slots=True)
class LooseShape:
    id: str
    node: Node
    file_bbox: geo.BBox | None
    kind: str


@dataclass(slots=True)
class LoadedProject:
    info: ProjectInfo
    data: bytes
    root: Node
    items: list[SourceItem]
    loose: list[LooseShape]

    def item(self, item_id: str) -> SourceItem:
        for it in self.items:
            if it.id == item_id:
                return it
        raise GridError("unknown_item", "Neznámý výrobek.", item_id=item_id)

    def obstacles_for(self, selected_ids: set[str]) -> list[Obstacle]:
        """Nevybrané výrobky a volné objekty jako překážky (spec. kap. 21.2, 21.4)."""
        o = self.info.orientation
        out: list[Obstacle] = []
        for it in self.items:
            if it.id in selected_ids:
                continue
            bbox = it.file_bbox if it.supported else it.content_bbox
            out.append(Obstacle(it.id, o.to_screen_rect(bbox) if bbox else None, label=it.label, kind="group"))
        for ls in self.loose:
            out.append(Obstacle(ls.id, o.to_screen_rect(ls.file_bbox) if ls.file_bbox else None, kind=ls.kind))
        return out


# --------------------------------------------------------------------------------------------


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes_checked(path: Path) -> bytes:
    suffix = path.suffix.lower()
    if suffix == ".lbrn":
        raise GridError("legacy_format", "Podporovány jsou pouze projekty .lbrn2. Uložte projekt v LightBurnu jako .lbrn2.")
    if suffix != ".lbrn2":
        raise GridError("not_lbrn2", "Soubor nemá příponu .lbrn2.", suffix=suffix)
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise GridError("file_too_large", "Soubor je příliš velký.", size=size)
    return path.read_bytes()


class _Ctx:
    def __init__(self, root: Node) -> None:
        self.verts: dict[str, str] = {}
        self.prims: dict[str, str] = {}
        for n in root.iter():
            if n.tag == "Shape":
                v, p = n.find("VertList"), n.find("PrimList")
                if v is not None and "VertID" in n.attrs:
                    self.verts.setdefault(n.attrs["VertID"], v.text)
                if p is not None and "PrimID" in n.attrs:
                    self.prims.setdefault(n.attrs["PrimID"], p.text)

    def path_geometry(self, shape: Node) -> tuple[list[geo.Vertex], str | None]:
        v = shape.find("VertList")
        vtext = v.text if v is not None else self.verts.get(shape.attrs.get("VertID", ""))
        if vtext is None:
            raise geo.GeometryError("Chybí seznam vrcholů")
        p = shape.find("PrimList")
        ptext = p.text if p is not None else self.prims.get(shape.attrs.get("PrimID", ""))
        return geo.parse_vertlist(vtext), ptext


def _xform(node: Node) -> geo.Affine:
    x = node.find("XForm")
    return geo.parse_xform(x.text) if x is not None else geo.IDENTITY


@dataclass
class _Measure:
    boxes: list[tuple[geo.BBox, Node, bool]] = field(default_factory=list)  # (bbox, shape, closed path?)
    blocking: list[Reason] = field(default_factory=list)
    warnings: list[Reason] = field(default_factory=list)
    unmeasurable: int = 0
    texts: list[str] = field(default_factory=list)


def _measure(shape: Node, parent_m: geo.Affine, ctx: _Ctx, acc: _Measure) -> None:
    """Rekurzivně změří tvar; neznámé konstrukce zapíše jako blokující důvod."""
    kind = shape.attrs.get("Type", "")
    try:
        m = geo.compose(parent_m, _xform(shape))
    except geo.GeometryError as e:
        acc.blocking.append(Reason("bad_xform", {"type": kind, "detail": str(e)}))
        return
    child_tags = {c.tag for c in shape.children}

    if kind == "Group":
        extra = child_tags - GROUP_CHILDREN
        if extra:
            acc.blocking.append(Reason("unknown_element", {"in": "Group", "tags": sorted(extra)}))
        kids = shape.find("Children")
        for c in kids.children if kids is not None else []:
            if c.tag == "Shape":
                _measure(c, m, ctx, acc)
            else:
                acc.blocking.append(Reason("unknown_element", {"in": "Children", "tags": [c.tag]}))
        return

    if kind == "Path":
        extra = child_tags - PATH_CHILDREN
        if extra:
            acc.blocking.append(Reason("unknown_element", {"in": "Path", "tags": sorted(extra)}))
        try:
            verts, prims = ctx.path_geometry(shape)
            acc.boxes.append((geo.path_bbox(verts, m), shape, geo.is_closed(prims, len(verts))))
        except geo.GeometryError as e:
            acc.unmeasurable += 1
            acc.blocking.append(Reason("unreadable_path", {"detail": str(e)}))
        return

    if kind == "Text":
        extra = child_tags - TEXT_CHILDREN
        if extra:
            acc.blocking.append(Reason("unknown_element", {"in": "Text", "tags": sorted(extra)}))
        acc.texts.append(" ".join(shape.attrs.get("Str", "").split()))
        bp = shape.find("BackupPath")
        if bp is None:
            acc.unmeasurable += 1
            acc.warnings.append(Reason("text_unmeasurable", {"text": acc.texts[-1]}))
            return
        if {c.tag for c in bp.children} - PATH_CHILDREN:
            acc.blocking.append(Reason("unknown_element", {"in": "BackupPath"}))
            return
        try:
            b = _xform(bp)  # ve světových souřadnicích (KAL-00, V-001 bod 5)
            if any(abs(u - v) > BACKUP_TOLERANCE for u, v in zip(b, m)):
                acc.blocking.append(Reason("text_backup_mismatch", {"text": acc.texts[-1]}))
                return
            verts, _ = ctx.path_geometry(bp)
            acc.boxes.append((geo.path_bbox(verts, b), bp, False))
        except geo.GeometryError as e:
            acc.unmeasurable += 1
            acc.warnings.append(Reason("text_unmeasurable", {"text": acc.texts[-1], "detail": str(e)}))
        return

    if kind in shapes.NATIVE_TYPES:
        extra = child_tags - shapes.NATIVE_CHILDREN
        if extra:
            acc.blocking.append(Reason("unknown_element", {"in": kind, "tags": sorted(extra)}))
        attrs = shapes.unknown_attrs(shape.attrs)
        if attrs:
            acc.blocking.append(Reason("unknown_shape_attribute", {"type": kind, "attrs": attrs}))
        try:
            native = shapes.parse_native(shape.attrs)
        except geo.GeometryError as e:
            acc.unmeasurable += 1
            acc.blocking.append(Reason("unreadable_shape", {"type": kind, "detail": str(e)}))
            return
        pending = shapes.unverified(native)
        if pending:
            acc.blocking.append(Reason(*pending))
        acc.boxes.append((shapes.native_bbox(native, m), shape, True))
        return

    acc.unmeasurable += 1
    acc.blocking.append(Reason("unsupported_shape_type", {"type": kind}))


def _analyse_item(node: Node, idx: int, ctx: _Ctx, layers: dict[str, str]) -> SourceItem:
    item_id = f"G{idx}"
    reasons: list[Reason] = []
    extra_attrs = set(node.attrs) - GROUP_ATTRS
    if extra_attrs:
        reasons.append(Reason("unknown_group_attribute", {"attrs": sorted(extra_attrs)}))
    acc = _Measure()
    _measure(node, geo.IDENTITY, ctx, acc)
    reasons.extend(acc.blocking)

    content = geo.union([b for b, _, _ in acc.boxes]) if acc.boxes else None
    outline_bbox: geo.BBox | None = None
    outline_layer: str | None = None
    if content is None:
        reasons.append(Reason("empty_group"))
    else:
        cands = [(b, s) for b, s, closed in acc.boxes if closed and geo.contains(b, content, EPSILON)]
        if not cands:
            closed_paths = [b for b, _, c in acc.boxes if c]
            if closed_paths:
                largest = max(closed_paths, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
                reasons.append(Reason("content_outside_outline", {"outline": largest, "content": content}))
            else:
                reasons.append(Reason("no_outline"))
        elif len(cands) > 1:
            reasons.append(Reason("ambiguous_outline", {"count": len(cands)}))
        else:
            outline_bbox = cands[0][0]
            ci = cands[0][1].attrs.get("CutIndex", "")
            outline_layer = layers.get(ci, ci)
        if outline_bbox and (outline_bbox[2] - outline_bbox[0] <= 0 or outline_bbox[3] - outline_bbox[1] <= 0):
            reasons.append(Reason("degenerate_outline"))

    label = next((t for t in acc.texts if t), "")
    supported = not reasons
    return SourceItem(
        id=item_id,
        source_order=idx,
        label=label,
        node=node,
        supported=supported,
        reasons=reasons,
        warnings=acc.warnings,
        file_bbox=outline_bbox if supported else None,
        outline_layer=outline_layer,
        content_bbox=content if acc.unmeasurable == 0 else None,
    )


def load_project(path: str | Path) -> LoadedProject:
    """Načte a ověří projekt. Projekt jako celek odmítne výjimkou ``GridError``."""
    path = Path(path)
    data = read_bytes_checked(path)
    root = parse(data)
    if root.tag != "LightBurnProject":
        raise GridError("not_lightburn_project", "Kořen dokumentu není LightBurnProject.", root=root.tag)

    a = root.attrs
    app, fmt = a.get("AppVersion", ""), a.get("FormatVersion", "")
    if not app.startswith(SUPPORTED_APP_VERSION_PREFIXES) or fmt not in SUPPORTED_FORMAT_VERSIONS:
        raise GridError("unsupported_version", "Nepodporovaná verze projektu LightBurn.", app_version=app, format_version=fmt)
    unknown_attrs = set(a) - KNOWN_ROOT_ATTRS
    if unknown_attrs:
        raise GridError("unknown_project_attribute", "Projekt obsahuje neznámé vlastnosti.", attrs=sorted(unknown_attrs))
    if a.get("CurrentPage", "0") != "0":
        raise GridError("multi_page_unsupported", "Projekty s více stránkami nejsou podporovány.")
    flags = {}
    for k in ("MirrorX", "MirrorY"):
        if a.get(k) not in ("True", "False"):
            raise GridError("unknown_orientation", "Chybí nebo je neplatný příznak zrcadlení.", flag=k, value=a.get(k))
        flags[k] = a[k] == "True"
    orientation = Orientation(flags["MirrorX"], flags["MirrorY"])
    if not orientation.verified:
        raise GridError("unsupported_orientation", "Neověřené nastavení počátku laseru.", origin=orientation.origin)

    unknown_children = {c.tag for c in root.children} - KNOWN_ROOT_CHILDREN
    if unknown_children:
        raise GridError("unknown_element", "Projekt obsahuje neznámé části.", tags=sorted(unknown_children))

    layers: dict[str, str] = {}
    for cs in root.findall("CutSetting"):
        idx, name = cs.find("index"), cs.find("name")
        if idx is not None:
            layers[idx.attrs.get("Value", "")] = name.attrs.get("Value", "") if name is not None else ""

    ctx = _Ctx(root)
    items: list[SourceItem] = []
    loose: list[LooseShape] = []
    for i, shape in enumerate(root.findall("Shape"), start=1):
        if shape.attrs.get("Type") == "Group":
            items.append(_analyse_item(shape, i, ctx, layers))
        else:
            acc = _Measure()
            _measure(shape, geo.IDENTITY, ctx, acc)
            bbox = geo.union([b for b, _, _ in acc.boxes]) if acc.boxes and not acc.unmeasurable and not acc.blocking else None
            loose.append(LooseShape(f"S{i}", shape, bbox, shape.attrs.get("Type", "?")))

    for it in items:
        if it.supported and it.file_bbox is not None:
            it.screen_bounds = orientation.to_screen_rect(it.file_bbox)
            for v in it.file_bbox:
                if not math.isfinite(v):
                    raise GridError("invalid_bounds", "Nekonečné souřadnice.", item_id=it.id)

    info = ProjectInfo(
        path=path,
        sha256=_sha256(data),
        size=len(data),
        app_version=app,
        format_version=fmt,
        device_name=a.get("DeviceName", ""),
        orientation=orientation,
        layer_names=layers,
    )
    return LoadedProject(info=info, data=data, root=root, items=items, loose=loose)

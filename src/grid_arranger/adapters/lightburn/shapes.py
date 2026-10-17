"""Nativní tvary LightBurnu: ``Ellipse``, ``Rect``, ``Polygon`` (spec. v1.14 kap. 5 bod 8; KAL-02).

Tyto tvary nemají seznam vrcholů — LightBurn ukládá jen rozměry a ``XForm`` (posun = střed tvaru):

* ``<Shape Type="Ellipse" Rx="20" Ry="20">`` — elipsa s poloosami Rx, Ry kolem počátku;
* ``<Shape Type="Rect" W="60" H="40" Cr="0">`` — obdélník W × H se středem v počátku, Cr = poloměr
  rohů v mm (nejvýš polovina kratší strany); roh = čtvrtelipsa jako Bézierova křivka;
* ``<Shape Type="Polygon" Rx="30.5" Ry="30.5" N="6">`` — pravidelný N-úhelník vepsaný do elipsy
  Rx, Ry; vrcholy v úhlech ``90° + 180°/N + k·360°/N`` (lichý N: vrchol v ``(0, −Ry)``).

Ověřeno: Test_tvary_A/L_A (elipsy, klíčenky ve vnořené skupině, obdélník, šestiúhelník) a KAL-02 —
tvary převedené v LightBurnu na křivky (Convert to Path) se s výpočtem shodují na 0,0000 mm
(mnohoúhelníky N = 3–8 včetně zrcadleného a eliptického, poloměry rohů 5, 12 a 30 mm, natočená elipsa).

Tvar se převádí na ekvivalentní cestu (stejné ``Vertex`` / ``PrimList`` jako ``Path``), takže
náhled i výpočet natočení používají stejný kód. Obdélník kolem tvaru (AABB) se počítá přesně:
u elipsy analyticky, u mnohoúhelníku z vrcholů, u obdélníku z rohů vnitřního obdélníku + elipsy rohu.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import geometry as geo

NATIVE_TYPES = frozenset({"Ellipse", "Rect", "Polygon"})
NATIVE_CHILDREN = frozenset({"XForm"})
_ATTRS = {
    "Ellipse": ("Rx", "Ry"),
    "Rect": ("W", "H", "Cr"),
    "Polygon": ("Rx", "Ry", "N"),
}
COMMON_ATTRS = frozenset({"Type", "CutIndex"})
MAX_POLYGON_SIDES = 1000
KAPPA = 0.5522847498307936  # čtvrtkruh Bézierovou křivkou (stejné číslo používá LightBurn)


@dataclass(frozen=True, slots=True)
class Native:
    kind: str
    rx: float = 0.0
    ry: float = 0.0
    w: float = 0.0
    h: float = 0.0
    cr: float = 0.0
    n: int = 0


def unknown_attrs(shape_attrs: dict[str, str]) -> list[str]:
    kind = shape_attrs.get("Type", "")
    allowed = COMMON_ATTRS | set(_ATTRS.get(kind, ()))
    return sorted(set(shape_attrs) - allowed)


def _num(attrs: dict[str, str], key: str) -> float:
    if key not in attrs:
        raise geo.GeometryError(f"Chybí rozměr {key}")
    try:
        v = float(attrs[key])
    except ValueError:
        raise geo.GeometryError(f"Nečíselný rozměr {key}={attrs[key]!r}") from None
    if not math.isfinite(v):
        raise geo.GeometryError(f"Nekonečný rozměr {key}")
    return v


def parse_native(attrs: dict[str, str]) -> Native:
    """Rozměry nativního tvaru; nečitelné nebo nesmyslné hodnoty → ``GeometryError``."""
    kind = attrs.get("Type", "")
    if kind == "Ellipse":
        rx, ry = _num(attrs, "Rx"), _num(attrs, "Ry")
        if rx <= 0 or ry <= 0:
            raise geo.GeometryError("Elipsa s nulovým rozměrem")
        return Native(kind, rx=rx, ry=ry)
    if kind == "Rect":
        w, h, cr = _num(attrs, "W"), _num(attrs, "H"), _num(attrs, "Cr")
        if w <= 0 or h <= 0 or cr < 0:
            raise geo.GeometryError("Obdélník s nulovým rozměrem")
        return Native(kind, w=w, h=h, cr=cr)
    if kind == "Polygon":
        rx, ry, n = _num(attrs, "Rx"), _num(attrs, "Ry"), _num(attrs, "N")
        if rx <= 0 or ry <= 0:
            raise geo.GeometryError("Mnohoúhelník s nulovým rozměrem")
        if n != int(n) or not 3 <= n <= MAX_POLYGON_SIDES:
            raise geo.GeometryError(f"Neplatný počet stran N={attrs['N']!r}")
        return Native(kind, rx=rx, ry=ry, n=int(n))
    raise geo.GeometryError(f"Neznámý tvar {kind!r}")


def _v(x: float, y: float, c0: tuple[float, float] | None = None, c1: tuple[float, float] | None = None) -> geo.Vertex:
    return geo.Vertex(x, y, c0, c1)


def _ellipse(rx: float, ry: float) -> tuple[list[geo.Vertex], str]:
    kx, ky = KAPPA * rx, KAPPA * ry
    verts = [
        _v(rx, 0, (rx, ky), (rx, -ky)),
        _v(0, ry, (-kx, ry), (kx, ry)),
        _v(-rx, 0, (-rx, -ky), (-rx, ky)),
        _v(0, -ry, (kx, -ry), (-kx, -ry)),
    ]
    return verts, "B0 1B1 2B2 3B3 0"


def _rect(w: float, h: float, cr: float) -> tuple[list[geo.Vertex], str]:
    x, y = w / 2, h / 2
    r = min(cr, x, y)
    if r <= 0:
        return [_v(x, -y), _v(x, y), _v(-x, y), _v(-x, -y)], "LineClosed"
    k = KAPPA * r
    # stejné pořadí jako zaoblený obdélník převedený v LightBurnu na křivky (Test_tvary_A „Obdéln“)
    verts = [
        _v(x, -y + r, (x, -y + r - k), None), _v(x - r, -y, None, (x - r + k, -y)),
        _v(-x + r, -y, (-x + r - k, -y), None), _v(-x, -y + r, None, (-x, -y + r - k)),
        _v(-x, y - r, (-x, y - r + k), None), _v(-x + r, y, None, (-x + r - k, y)),
        _v(x - r, y, (x - r + k, y), None), _v(x, y - r, None, (x, y - r + k)),
    ]
    return verts, "B0 1L1 2B2 3L3 4B4 5L5 6B6 7L7 0"


def _polygon(rx: float, ry: float, n: int) -> tuple[list[geo.Vertex], str]:
    verts = []
    for k in range(n):
        t = math.pi / 2 + math.pi / n + 2 * math.pi * k / n  # jako LightBurn (KAL-02)
        verts.append(_v(rx * math.cos(t), ry * math.sin(t)))
    return verts, "LineClosed"


def native_path(native: Native) -> tuple[list[geo.Vertex], str]:
    """Ekvivalentní cesta v místních souřadnicích tvaru (před ``XForm``)."""
    if native.kind == "Ellipse":
        return _ellipse(native.rx, native.ry)
    if native.kind == "Rect":
        return _rect(native.w, native.h, native.cr)
    return _polygon(native.rx, native.ry, native.n)


def native_bbox(native: Native, m: geo.Affine) -> geo.BBox:
    """Přesný AABB tvaru po transformaci ``m`` (souřadnice souboru)."""
    a, b, c, d, e, f = m
    if native.kind == "Ellipse":
        hx = math.hypot(a * native.rx, c * native.ry)
        hy = math.hypot(b * native.rx, d * native.ry)
        return e - hx, f - hy, e + hx, f + hy
    if native.kind == "Rect":
        x, y = native.w / 2, native.h / 2
        r = min(native.cr, x, y)
        hx, hy = r * math.hypot(a, c), r * math.hypot(b, d)  # elipsa rohu po transformaci
        pts = [geo.apply(m, sx * (x - r), sy * (y - r)) for sx in (-1, 1) for sy in (-1, 1)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs) - hx, min(ys) - hy, max(xs) + hx, max(ys) + hy
    else:
        pts = [geo.apply(m, v.x, v.y) for v in _polygon(native.rx, native.ry, native.n)[0]]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

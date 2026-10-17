"""Natočení výrobků pro úsporu materiálu (spec. v1.13 kap. 7.6) — čistá geometrie bez Qt a formátu.

Souřadnice jádra (X doprava, Y dolů). Úhel ve stupních; kladný = po směru hodinových ručiček na
obrazovce (stejně jako ``QGraphicsItem.setRotation``): ``x' = x·cos − y·sin``, ``y' = x·sin + y·cos``.

* :func:`min_area_angle` — úhel, při kterém má obdélník kolem bodů nejmenší plochu
  (konvexní obal + otáčení podle hran obalu; nejmenší obdélník má vždy stranu na hraně obalu).
* :func:`rotated_bounds` — osový obdélník natočených bodů.
* Natočí se jen tehdy, když to plochu zmenší aspoň o :data:`MIN_GAIN` — jinak by se výrobky
  zbytečně natáčely o zlomky stupně kvůli zaokrouhlení křivek.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

from ..domain.models import Rect

Point = tuple[float, float]
MIN_GAIN = 0.005  # natočit, jen když ušetří aspoň 0,5 % plochy obdélníku


def rotate_point(p: Point, deg: float, cx: float = 0.0, cy: float = 0.0) -> Point:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    x, y = p[0] - cx, p[1] - cy
    return cx + x * c - y * s, cy + x * s + y * c


def convex_hull(points: Iterable[Point]) -> list[Point]:
    """Monotónní řetězec (Andrew); vrací vrcholy proti směru (v matematické orientaci)."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o: Point, a: Point, b: Point) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[Point] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def rotated_bounds(points: Sequence[Point], deg: float, cx: float = 0.0, cy: float = 0.0) -> Rect:
    rp = [rotate_point(p, deg, cx, cy) for p in points]
    return Rect(min(p[0] for p in rp), min(p[1] for p in rp), max(p[0] for p in rp), max(p[1] for p in rp))


def _normalize(deg: float) -> float:
    """Do intervalu (−45°, 45°] — natočení o 90° navíc řeší volba orientace zvlášť."""
    d = math.fmod(deg, 90.0)
    if d > 45.0:
        d -= 90.0
    elif d <= -45.0:
        d += 90.0
    return 0.0 if abs(d) < 1e-9 else d


def min_area_angle(points: Sequence[Point]) -> float:
    """Úhel v (−45°, 45°], při kterém je osový obdélník kolem bodů nejmenší; 0 bez znatelné úspory."""
    hull = convex_hull(points)
    if len(hull) < 3:
        return 0.0
    base = rotated_bounds(hull, 0.0)
    base_area = base.width * base.height
    best_deg, best_area = 0.0, base_area
    n = len(hull)
    for i in range(n):
        (x0, y0), (x1, y1) = hull[i], hull[(i + 1) % n]
        if x0 == x1 and y0 == y1:
            continue
        deg = _normalize(-math.degrees(math.atan2(y1 - y0, x1 - x0)))  # hrana obalu → vodorovně
        r = rotated_bounds(hull, deg)
        area = r.width * r.height
        if area < best_area - 1e-9:
            best_deg, best_area = deg, area
    if base_area <= 0 or (base_area - best_area) / base_area < MIN_GAIN:
        return 0.0
    return _normalize(round(best_deg, 6))

"""Převod mezi souřadnicemi souboru/stroje a souřadnicemi jádra (spec. kap. 8, KAL-00).

Ověřeno pro LightBurn 2.2.00: souřadnice v souboru = hodnoty X/Y v UI LightBurnu;
``MirrorX``/``MirrorY`` řídí jen zobrazení::

    screen_x = −x  když MirrorX,  jinak +x
    screen_y = +y  když MirrorY,  jinak −y      (jádro: osa Y dolů)

Podporované kombinace: MirrorY = True (počátek nahoře). Ostatní jsou neověřené.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.models import Rect
from .geometry import BBox

ORIGIN_NAMES = {
    (True, True): "top_right",
    (False, True): "top_left",
    (False, False): "bottom_left",
    (True, False): "bottom_right",
}
VERIFIED = {(True, True), (False, True)}


@dataclass(frozen=True, slots=True)
class Orientation:
    mirror_x: bool
    mirror_y: bool

    @property
    def sx(self) -> float:
        return -1.0 if self.mirror_x else 1.0

    @property
    def sy(self) -> float:
        return 1.0 if self.mirror_y else -1.0

    @property
    def origin(self) -> str:
        return ORIGIN_NAMES[(self.mirror_x, self.mirror_y)]

    @property
    def verified(self) -> bool:
        return (self.mirror_x, self.mirror_y) in VERIFIED

    def to_screen_rect(self, b: BBox) -> Rect:
        xs = sorted((self.sx * b[0], self.sx * b[2]))
        ys = sorted((self.sy * b[1], self.sy * b[3]))
        return Rect(xs[0], ys[0], xs[1], ys[1])

    def to_screen_point(self, x: float, y: float) -> tuple[float, float]:
        return self.sx * x, self.sy * y

    def to_file_point(self, sx: float, sy: float) -> tuple[float, float]:
        return self.sx * sx, self.sy * sy  # převod je involuce

    def to_file_delta(self, dx: float, dy: float) -> tuple[float, float]:
        return self.sx * dx, self.sy * dy

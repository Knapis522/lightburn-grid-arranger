"""Vygeneruje ikonu aplikace (vlastní motiv: mřížka 3×3, jedna buňka zvýrazněná jako počátek laseru).

    python tools/make_icon.py

Výstup (verzuje se v Gitu, mění se jen spuštěním tohoto skriptu):
* ``src/grid_arranger/gui/resources/app_icon.png`` — ikona okna (256 px),
* ``packaging/GridArranger.ico`` — ikona EXE (16–256 px).

Nepoužívá logo ani grafiku LightBurnu (spec. kap. 33). Vyžaduje Pillow (jen pro tento skript).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "src" / "grid_arranger" / "gui" / "resources" / "app_icon.png"
ICO = ROOT / "packaging" / "GridArranger.ico"

BG = (31, 58, 95, 255)
CELL = (232, 238, 245, 255)
ORIGIN = (228, 87, 46, 255)


def draw(size: int = 1024) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = size * 0.04
    d.rounded_rectangle((pad, pad, size - pad, size - pad), radius=size * 0.2, fill=BG)
    inner = size * 0.2
    gap = size * 0.06
    cell = (size - 2 * inner - 2 * gap) / 3
    for row in range(3):
        for col in range(3):
            x = inner + col * (cell + gap)
            y = inner + row * (cell + gap)
            color = ORIGIN if (row, col) == (0, 2) else CELL  # počátek vpravo nahoře
            d.rounded_rectangle((x, y, x + cell, y + cell), radius=cell * 0.16, fill=color)
    return img


def main() -> None:
    big = draw()
    PNG.parent.mkdir(parents=True, exist_ok=True)
    ICO.parent.mkdir(parents=True, exist_ok=True)
    big.resize((256, 256), Image.Resampling.LANCZOS).save(PNG)
    big.save(ICO, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"{PNG}\n{ICO}")


if __name__ == "__main__":
    main()

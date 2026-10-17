"""KAL-02: kalibrace nativních tvarů LightBurnu (diagnostika, není součástí aplikace).

    python tools/kal02/native_shapes_calibration.py <šablona.lbrn2> [výstupní_složka]
    python tools/kal02/native_shapes_calibration.py --compare <převedený.lbrn2>

1. Vytvoří ``<šablona>__kal02_tvary.lbrn2`` (nikdy nepřepíše): ze šablony se převezme jen hlavička
   a vrstvy, obsah je nový. Každý výrobek = skupina s nativním tvarem (vrstva 0) a s naší
   „kopií“ téhož tvaru jako křivky (vrstva 1), spočítanou stejně, jako ji počítá aplikace.
   V LightBurnu musí obě čáry ležet přesně na sobě.
2. Pro přesné porovnání: v LightBurnu vybrat vše na vrstvě 0 → Převést na křivky (Convert to Path)
   → Uložit jako ``…_prevedeno.lbrn2``; ``--compare`` pak změří odchylku našich křivek od LightBurnu.

Šablona musí mít vrstvy (CutSetting) s indexy 0 a 1.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from grid_arranger.adapters.lightburn import geometry as geo  # noqa: E402
from grid_arranger.adapters.lightburn import shapes  # noqa: E402
from grid_arranger.adapters.lightburn.coords import Orientation  # noqa: E402
from grid_arranger.adapters.lightburn.read import _Ctx, _xform  # noqa: E402
from grid_arranger.adapters.lightburn.render import Stroke, _path_ops, stroke_points  # noqa: E402
from grid_arranger.adapters.lightburn.xmltree import parse  # noqa: E402
from grid_arranger.adapters.lightburn.write import write_new_file  # noqa: E402

# (název, typ, atributy, XForm tvaru bez posunu)
CASES = [
    ("P3", "Polygon", {"Rx": 20, "Ry": 20, "N": 3}, (1, 0, 0, 1)),
    ("P4", "Polygon", {"Rx": 20, "Ry": 20, "N": 4}, (1, 0, 0, 1)),
    ("P5", "Polygon", {"Rx": 20, "Ry": 20, "N": 5}, (1, 0, 0, 1)),
    ("P5zrc", "Polygon", {"Rx": 20, "Ry": 20, "N": 5}, (-1, 0, 0, 1)),  # jako šestiúhelník z LightBurnu
    ("P7", "Polygon", {"Rx": 20, "Ry": 20, "N": 7}, (1, 0, 0, 1)),
    ("P8", "Polygon", {"Rx": 20, "Ry": 20, "N": 8}, (1, 0, 0, 1)),
    ("P5elip", "Polygon", {"Rx": 25, "Ry": 14, "N": 5}, (1, 0, 0, 1)),
    ("P6", "Polygon", {"Rx": 20, "Ry": 20, "N": 6}, (1, 0, 0, 1)),  # kontrola: ověřeno už v Test_tvary_A
    ("R5", "Rect", {"W": 50, "H": 34, "Cr": 5}, (1, 0, 0, 1)),
    ("R12", "Rect", {"W": 50, "H": 34, "Cr": 12}, (1, 0, 0, 1)),
    ("R30", "Rect", {"W": 50, "H": 34, "Cr": 30}, (1, 0, 0, 1)),  # poloměr větší než polovina výšky
    ("E30", "Ellipse", {"Rx": 25, "Ry": 12}, (math.cos(math.radians(30)), math.sin(math.radians(30)),
                                              -math.sin(math.radians(30)), math.cos(math.radians(30)))),
]
PITCH = 60.0  # mm mezi středy
PER_ROW = 4


def _xf(m: geo.Affine) -> str:
    return " ".join(geo.fmt_num(v) for v in m)


def _vertlist(verts: list[geo.Vertex]) -> str:
    out = []
    for v in verts:
        s = f"V{geo.fmt_num(v.x)} {geo.fmt_num(v.y)}"
        s += f"c0x{geo.fmt_num(v.c0[0])}c0y{geo.fmt_num(v.c0[1])}" if v.c0 else "c0x1"
        s += f"c1x{geo.fmt_num(v.c1[0])}c1y{geo.fmt_num(v.c1[1])}" if v.c1 else "c1x1"
        out.append(s)
    return "".join(out)


def build(template: bytes) -> tuple[bytes, list[str]]:
    text = template.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    first = next(i for i, ln in enumerate(lines) if ln.startswith("    <Shape "))
    notes = next(i for i, ln in enumerate(lines) if ln.startswith("    <Notes"))
    body, table = [], []
    for k, (name, kind, attrs, lin) in enumerate(CASES):
        cx = 60.0 + PITCH * (k % PER_ROW)
        cy = 60.0 + PITCH * (k // PER_ROW)
        m = (*lin, cx, cy)
        native = shapes.parse_native({"Type": kind, **{a: str(v) for a, v in attrs.items()}})
        verts, prims = shapes.native_path(native)
        a = "".join(f' {key}="{geo.fmt_num(float(v))}"' for key, v in attrs.items())
        body += [
            '    <Shape Type="Group">',
            "        <XForm>1 0 0 1 0 0</XForm>",
            "        <Children>",
            f'            <Shape Type="{kind}" CutIndex="0"{a}>',
            f"                <XForm>{_xf(m)}</XForm>",
            "            </Shape>",
            f'            <Shape Type="Path" CutIndex="1" VertID="{k + 1}" PrimID="{k + 1}">',
            f"                <XForm>{_xf(m)}</XForm>",
            f"                <VertList>{_vertlist(verts)}</VertList>",
            f"                <PrimList>{prims}</PrimList>",
            "            </Shape>",
            "        </Children>",
            "    </Shape>",
        ]
        table.append(f"  {k + 1:2}. {name:7} {kind:8} {attrs}  střed X {cx:.0f}, Y {cy:.0f}")
    out = lines[:first] + body + lines[notes:]
    return nl.join(out).encode("utf-8"), table


def _points(node, m: geo.Affine, ctx: _Ctx) -> list[tuple[float, float]]:
    """Body křivky (Path nebo nativní tvar) v souřadnicích souboru."""
    o = Orientation(False, True)  # sx = sy = 1
    kind = node.attrs.get("Type", "")
    if kind == "Path":
        verts, prims = ctx.path_geometry(node)
    else:
        verts, prims = shapes.native_path(shapes.parse_native(node.attrs))
    return stroke_points([Stroke("", _path_ops(verts, prims, m, o))], 0.001)


def _dist_to(pts_a, pts_b) -> float:
    """Největší vzdálenost bodu z ``pts_a`` k nejbližšímu bodu ``pts_b`` (hrubě, stačí pro kalibraci)."""
    worst = 0.0
    for ax, ay in pts_a[:: max(1, len(pts_a) // 400)]:
        worst = max(worst, min(math.hypot(ax - bx, ay - by) for bx, by in pts_b))
    return worst


def compare(converted: Path) -> int:
    root = parse(converted.read_bytes())
    ctx = _Ctx(root)
    groups = [s for s in root.findall("Shape") if s.attrs.get("Type") == "Group"]
    worst_all = 0.0
    for k, g in enumerate(groups):
        gm = _xform(g)
        kids = g.find("Children")
        by_cut = {}
        for c in kids.children if kids is not None else []:
            by_cut[c.attrs.get("CutIndex")] = c
        if "0" not in by_cut or "1" not in by_cut:
            print(f"  {k + 1:2}. chybí tvar na vrstvě 0 nebo 1")
            continue
        theirs = _points(by_cut["0"], geo.compose(gm, _xform(by_cut["0"])), ctx)
        ours = _points(by_cut["1"], geo.compose(gm, _xform(by_cut["1"])), ctx)
        d = max(_dist_to(theirs, ours), _dist_to(ours, theirs))
        worst_all = max(worst_all, d)
        name = CASES[k][0] if k < len(CASES) else "?"
        kind = by_cut["0"].attrs.get("Type")
        print(f"  {k + 1:2}. {name:7} vrstva 0 = {kind:8} odchylka {d:.4f} mm  {'OK' if d <= 0.01 else 'NESEDÍ'}")
    print(f"Největší odchylka: {worst_all:.4f} mm")
    return 0 if worst_all <= 0.01 else 1


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--compare":
        return compare(Path(sys.argv[2]))
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent
    data, table = build(src.read_bytes())
    if not re.search(rb'<index Value="0"/>', data) or not re.search(rb'<index Value="1"/>', data):
        print("Šablona nemá vrstvy 0 a 1.")
        return 1
    target = out_dir / f"{src.stem}__kal02_tvary.lbrn2"
    write_new_file(target, data, forbidden=src)
    print("Tvary (vrstva 0 = nativní tvar LightBurnu, vrstva 1 = výpočet aplikace):")
    print("\n".join(table))
    print(f"Uloženo: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

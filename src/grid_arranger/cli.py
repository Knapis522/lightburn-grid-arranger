"""Vývojářská příkazová řádka (spec. kap. 11, 12.1) — není uživatelským rozhraním.

Příklady::

    python -m grid_arranger info projekt.lbrn2
    python -m grid_arranger arrange projekt.lbrn2 --columns 3 --gap 5 --board 700 500 --dry-run

Souřadnice (``--start``, ``--board-at``) jsou hodnoty X/Y z LightBurnu (vzdálenost od počátku laseru).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapters.lightburn.read import load_project
from .application.arrange_job import (
    ANCHORS, DEFAULT_MARGIN_MM, FILL_MODES, ROTATION_MODES, ArrangeParams, MaterialInput, execute, make_plan,
)
from .domain.errors import GridError
from .version import display_version

ORIGIN_TEXT = {"top_right": "top right", "top_left": "top left", "bottom_left": "bottom left", "bottom_right": "bottom right"}


def _copies(specs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for spec in specs:
        iid, sep, n = spec.partition("=")
        if not sep or not iid.strip() or not n.strip().isdigit():
            raise SystemExit(f"--copies: expected ID=N, got {spec!r}")
        iid = iid.strip()
        for k in range(1, int(n) + 1):
            out[f"{iid}+{k}"] = iid
    return out


def _angles(specs: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for spec in specs:
        iid, sep, deg = spec.partition("=")
        try:
            out[iid.strip()] = float(deg)
        except ValueError:
            raise SystemExit(f"--angle: expected ID=DEG, got {spec!r}") from None
        if not sep or not iid.strip():
            raise SystemExit(f"--angle: expected ID=DEG, got {spec!r}")
    return out


def _cmd_info(a: argparse.Namespace) -> int:
    p = load_project(a.file)
    i = p.info
    print(f"File:      {i.path.name}")
    print(f"LightBurn: {i.app_version} (format {i.format_version})")
    print(f"Device:    {i.device_name} — origin {ORIGIN_TEXT[i.orientation.origin]}")
    print(f"SHA-256:   {i.sha256}")
    print(f"Items:     {sum(it.supported for it in p.items)} supported / {len(p.items)} groups; loose objects: {len(p.loose)}")
    for it in p.items:
        if it.supported:
            b = it.file_bbox
            size = f"{b[2]-b[0]:8.2f} x {b[3]-b[1]:7.2f} mm  layer {it.outline_layer}"
        else:
            size = "BLOCKED: " + ", ".join(r.code for r in it.reasons)
        warn = ("  warnings: " + ", ".join(w.code for w in it.warnings)) if it.warnings else ""
        print(f"  {it.id:>4}  {it.label[:28]:<28}  {size}{warn}")
    for ls in p.loose:
        print(f"  {ls.id:>4}  loose {ls.kind:<22}  {'measurable' if ls.file_bbox else 'NOT measurable (blocks saving)'}")
    return 0


def _cmd_arrange(a: argparse.Namespace) -> int:
    project = load_project(a.file)
    margin = a.margin if a.margin else [DEFAULT_MARGIN_MM]
    if len(margin) == 1:
        margin = margin * 4
    if len(margin) != 4:
        raise GridError("invalid_margin", "--margin takes one value or LEFT RIGHT TOP BOTTOM")
    material = None
    if a.board:
        bx, by = a.board_at if a.board_at else (0.0, 0.0)
        material = MaterialInput(a.board[0], a.board[1], bx, by, *margin)
    copies = _copies(a.copies)
    order = tuple(a.order.split(",")) if a.order else None
    if copies:  # kopie za ostatní výrobky
        base = order if order is not None else tuple(it.id for it in project.items if it.supported)
        order = base + tuple(c for c in copies if c not in base)
    params = ArrangeParams(
        columns=a.columns,
        gap_x=a.gap_x if a.gap_x is not None else a.gap,
        gap_y=a.gap_y if a.gap_y is not None else a.gap,
        material=material,
        order=order,
        anchor=a.anchor,
        start=tuple(a.start) if a.start else None,
        fill=a.fill,
        rotation=a.rotate,
        no_rotate=frozenset(a.no_rotate.split(",")) if a.no_rotate else frozenset(),
        angles=_angles(a.angle),
        copies=copies,
    )
    plan = make_plan(project, params)
    lay = plan.layout
    cx, cy = plan.origin_corner_lightburn
    print(f"Laser:     {project.info.device_name} — origin {ORIGIN_TEXT[project.info.orientation.origin]}")
    print(f"Grid: {lay.columns} columns x {lay.rows} rows, {lay.grid_bounds.width:.3f} x {lay.grid_bounds.height:.3f} mm;"
          f" anchor {plan.anchor}, fill from {plan.fill}; grid corner at origin side: LightBurn X {cx:.3f}, Y {cy:.3f}")
    for pl in lay.placements:
        m = plan.moves_file[pl.item_id]
        dx, dy = (m[0], m[1]) if len(m) == 2 else (m[4], m[5])
        rot = f"  rotate {plan.rotations[pl.item_id]:+.2f}°" if pl.item_id in plan.rotations else ""
        print(f"  {pl.index + 1:>3}. {pl.item_id:>4}  row {pl.row + 1} col {pl.column + 1}  move X {dx:+9.3f}  Y {dy:+9.3f}{rot}")
    for issue in plan.report.issues:
        print(f"  [{issue.severity.value.upper()}] {issue.code} {' '.join(issue.item_ids)} {issue.params or ''}")
    if not plan.report.can_save:
        print("Not saved: fix the errors above.")
        return 2
    if a.dry_run:
        print("Dry run: nothing written.")
        return 0
    res = execute(plan, Path(a.out_dir) if a.out_dir else None)
    print(f"Saved:     {res.output}")
    print(f"Protocol:  {res.protocol}")
    print("Open the output in LightBurn via File > Open and check layers, Preview and position before cutting.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="grid_arranger", description=f"Grid Arranger for LightBurn {display_version()} (developer CLI)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("info", help="show groups found in a .lbrn2 project")
    pi.add_argument("file")
    pa = sub.add_parser("arrange", help="arrange selected groups into a grid and save a NEW .lbrn2")
    pa.add_argument("file")
    pa.add_argument("--columns", type=int, required=True)
    pa.add_argument("--gap", type=float, default=3.0, help="gap X and Y in mm (default 3)")
    pa.add_argument("--gap-x", type=float)
    pa.add_argument("--gap-y", type=float)
    pa.add_argument("--order", help="comma-separated item ids, e.g. G9,G2,G1 (default: all supported, document order)")
    pa.add_argument("--board", type=float, nargs=2, metavar=("W", "H"), help="board size in mm, placed at the laser origin")
    pa.add_argument("--board-at", type=float, nargs=2, metavar=("X", "Y"), help="board corner at the origin side (LightBurn X Y, default 0 0)")
    pa.add_argument("--margin", type=float, nargs="+", metavar="MM", help=f"one value or LEFT RIGHT TOP BOTTOM (default {DEFAULT_MARGIN_MM:g})")
    pa.add_argument("--anchor", choices=ANCHORS, default="origin", help="where to put the grid (default: origin corner of the board)")
    pa.add_argument("--start", type=float, nargs=2, metavar=("X", "Y"), help="for --anchor manual: grid corner at origin side (LightBurn X Y)")
    pa.add_argument("--fill", choices=FILL_MODES, default="origin", help="first item at the laser origin corner (default) or top-left")
    pa.add_argument("--rotate", choices=ROTATION_MODES, default="none",
                    help="rotate items to save material: none (default), 90 (in 90° steps), any (smallest bounding box)")
    pa.add_argument("--no-rotate", help="comma-separated item ids that must never be rotated")
    pa.add_argument("--copies", action="append", default=[], metavar="ID=N",
                    help="add N copies of an item, placed after the other items (e.g. G5=4); repeatable")
    pa.add_argument("--angle", action="append", default=[], metavar="ID=DEG",
                    help="manual rotation of one item in degrees, clockwise on screen (e.g. G3=90); repeatable")
    pa.add_argument("--out-dir")
    pa.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    try:
        return _cmd_info(a) if a.cmd == "info" else _cmd_arrange(a)
    except GridError as e:
        print(f"ERROR {e.code}: {e} {e.params or ''}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

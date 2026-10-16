"""Vývojářská příkazová řádka (spec. kap. 11, 12.1) — není uživatelským rozhraním.

Příklady::

    python -m grid_arranger info projekt.lbrn2
    python -m grid_arranger arrange projekt.lbrn2 --columns 3 --gap 5 \\
        --material 0 0 1300 900 --margin 5 --dry-run

Souřadnice (``--start``, ``--material``) jsou hodnoty X/Y z LightBurnu.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adapters.lightburn.read import load_project
from .application.arrange_job import ArrangeParams, MaterialInput, execute, make_plan
from .domain.errors import GridError
from .version import display_version

ORIGIN_TEXT = {"top_right": "top right", "top_left": "top left", "bottom_left": "bottom left", "bottom_right": "bottom right"}


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
    margin = a.margin or [0.0]
    if len(margin) == 1:
        margin = margin * 4
    material = MaterialInput(*a.material, *margin) if a.material else None
    params = ArrangeParams(
        columns=a.columns,
        gap_x=a.gap_x if a.gap_x is not None else a.gap,
        gap_y=a.gap_y if a.gap_y is not None else a.gap,
        material=material,
        order=tuple(a.order.split(",")) if a.order else None,
        start=tuple(a.start) if a.start else None,
    )
    plan = make_plan(project, params)
    lay = plan.layout
    print(f"Grid: {lay.columns} columns x {lay.rows} rows, {lay.grid_bounds.width:.3f} x {lay.grid_bounds.height:.3f} mm,"
          f" top-left corner at LightBurn X {plan.start_lightburn[0]:.3f}, Y {plan.start_lightburn[1]:.3f}")
    for pl in lay.placements:
        dx, dy = plan.moves_file[pl.item_id]
        print(f"  {pl.index + 1:>3}. {pl.item_id:>4}  row {pl.row + 1} col {pl.column + 1}  move X {dx:+9.3f}  Y {dy:+9.3f}")
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
    pa.add_argument("--start", type=float, nargs=2, metavar=("X", "Y"), help="visual top-left corner of the grid (LightBurn X Y)")
    pa.add_argument("--material", type=float, nargs=4, metavar=("X", "Y", "W", "H"), required=True,
                    help="material rectangle in LightBurn coordinates")
    pa.add_argument("--margin", type=float, nargs="+", metavar="MM", help="one value or LEFT RIGHT TOP BOTTOM")
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

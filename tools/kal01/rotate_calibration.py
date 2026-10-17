"""KAL-01: kalibrace natočení skupin v .lbrn2 (diagnostika, není součástí aplikace).

    python tools/kal01/rotate_calibration.py <projekt.lbrn2> [výstupní_složka]

Natočí vybrané výrobky kolem středu jejich obrysu o pevné úhly v souřadnicích SOUBORU
(G1 90°, G2 30°, G3 180°, G4 −15°; ostatní beze změny) stejným zápisem, jaký použije
aplikace (``XForm' = T ∘ XForm`` skupiny i ``BackupPath`` textů). Výstup ověří nezávislou
kontrolou a opětovným načtením a uloží jako ``<název>__kal01_rot.lbrn2`` (nikdy nepřepíše).
Výsledek je potřeba otevřít v LightBurnu (File → Open) a zapsat do FORMAT_COMPATIBILITY.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from grid_arranger.adapters.lightburn import geometry as geo  # noqa: E402
from grid_arranger.adapters.lightburn.read import load_project  # noqa: E402
from grid_arranger.adapters.lightburn.write import apply_patches, plan_patches, write_new_file  # noqa: E402
from grid_arranger.safety.verify import verify_output  # noqa: E402

ANGLES = {"G1": 90.0, "G2": 30.0, "G3": 180.0, "G4": -15.0}


def rotation_about(cx: float, cy: float, deg: float) -> geo.Affine:
    r = math.radians(deg)
    cos, sin = math.cos(r), math.sin(r)
    # T = Tr(c) ∘ R ∘ Tr(−c); x' = a·x + c·y + e
    return (cos, sin, -sin, cos, cx - cos * cx + sin * cy, cy - sin * cx - cos * cy)


def main() -> int:
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent
    p = load_project(src)
    transforms = {}
    for item_id, deg in ANGLES.items():
        it = p.item(item_id)
        if not it.supported:
            print(f"{item_id}: nepodporovaný, přeskočen")
            continue
        x0, y0, x1, y1 = it.file_bbox
        transforms[item_id] = rotation_about((x0 + x1) / 2, (y0 + y1) / 2, deg)
        print(f"{item_id} ({it.label}): {deg:+.0f}° kolem středu ({(x0 + x1) / 2:.2f}, {(y0 + y1) / 2:.2f}), "
              f"rozměr {x1 - x0:.2f} × {y1 - y0:.2f} mm")
    ops = plan_patches(p, transforms)
    out = apply_patches(p.data, ops)
    tops = {it.id: it.source_order for it in p.items}
    problems = verify_output(p.data, out, {tops[k]: v for k, v in transforms.items()})
    print(f"Změněné XForm: {len(ops)}, nezávislá kontrola: {'OK' if not problems else problems}")
    target = out_dir / f"{src.stem}__kal01_rot.lbrn2"
    write_new_file(target, out, forbidden=src)
    q = load_project(target)
    for item_id, deg in ANGLES.items():
        it = q.item(item_id)
        b = it.file_bbox
        print(f"  po načtení {item_id}: podporovaný={it.supported}, rozměr {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} mm"
              + ("" if it.supported else f", důvody {[r.code for r in it.reasons]}"))
    print(f"Uloženo: {target}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())

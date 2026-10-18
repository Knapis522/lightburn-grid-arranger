"""Počet kusů výrobků (V11-02, spec. kap. 22.2): kopie hned za výrobkem, 0 = vynechat."""

from __future__ import annotations

import json

from grid_arranger.adapters.lightburn.read import load_project

from .lbrn2_builder import card, project


def test_cli_quantity_places_exact_counts(write_project, tmp_path, capsys):
    from grid_arranger.cli import main

    src = write_project(project([card(0, 0, text="A"), card(200, 0, text="B"), card(400, 300, text="C")]))
    assert main(["arrange", str(src), "--columns", "auto", "--board", "700", "500", "--quantity", "G1=4",
                 "--quantity", "G2=2", "--quantity", "G3=0", "--out-dir", str(tmp_path)]) == 0
    out = next(tmp_path.glob("*__grid_001.lbrn2"))
    o = load_project(out)
    assert len(o.items) == 3 + 3 + 1  # 3 originály (C zůstává na místě) + 4 kopie
    proto = json.loads(next(tmp_path.glob("*__grid_001.json")).read_text(encoding="utf-8"))
    assert proto["pieces_per_item"] == {"G1": 4, "G2": 2}
    text = capsys.readouterr().out
    assert "G1+q1" in text and "G1+q3" in text and "G2+q1" in text

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def write_project(tmp_path: Path):
    """Uloží syntetický projekt do dočasné složky a vrátí cestu."""

    def _w(data: bytes, name: str = "test.lbrn2") -> Path:
        p = tmp_path / name
        p.write_bytes(data)
        return p

    return _w

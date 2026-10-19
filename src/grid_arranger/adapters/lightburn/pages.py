"""Stránky projektu LightBurnu (KAL-06, spec. v1.29 kap. 23.1).

* Stránka 0 = nejvyšší tvary projektu, které nejsou stránkou (název v ``Page0Name``).
* Stránka K ≥ 1 = nejvyšší ``<Shape Type="Group" SubType="Page" Name="…">`` s ``XForm`` ``1 0 0 1 0 0``;
  tvary stránky jsou v jejím ``Children`` (prázdná stránka ``<Children/>``).

Souřadnice jsou na všech stránkách společné. Modul nezávisí na čtečce projektu, aby jej mohla
použít i nezávislá kontrola výstupu.
"""

from __future__ import annotations

from .xmltree import Node

PAGE_ATTRS = ("Type", "SubType", "Name")
PAGE_XFORM = "1 0 0 1 0 0"


def is_page(node: Node) -> bool:
    return node.tag == "Shape" and node.attrs.get("Type") == "Group" and node.attrs.get("SubType") == "Page"


def page_groups(root: Node) -> list[Node]:
    """Skupiny stránek 2, 3, … v pořadí dokumentu."""
    return [s for s in root.findall("Shape") if is_page(s)]


def page_count(root: Node) -> int:
    return 1 + len(page_groups(root))


def page_shapes(root: Node, page: int = 0) -> list[Node]:
    """Nejvyšší tvary dané stránky (u stránky 0 bez skupin stránek)."""
    if page == 0:
        return [s for s in root.findall("Shape") if not is_page(s)]
    groups = page_groups(root)
    if not 1 <= page <= len(groups):
        raise IndexError(page)
    ch = groups[page - 1].find("Children")
    return ch.findall("Shape") if ch is not None else []


def page_name(root: Node, page: int) -> str:
    if page == 0:
        return root.attrs.get("Page0Name", "")
    return page_groups(root)[page - 1].attrs.get("Name", "")

"""Bezpečné načtení XML `.lbrn2` do stromu s bajtovými pozicemi (spec. kap. 9.1, ADR-0002).

Používá `xml.parsers.expat` ze standardní knihovny. DTD a entity jsou odmítnuty
předem; parser nikdy nečte externí zdroje ani síť. Každý uzel zná bajtový rozsah
svého obsahu, aby zápis mohl přepsat jen konkrétní úseky.
"""

from __future__ import annotations

import xml.parsers.expat
from collections.abc import Iterator
from dataclasses import dataclass, field

from ...domain.errors import GridError


@dataclass(eq=False)
class Node:
    tag: str
    attrs: dict[str, str]
    start: int
    """Bajtová pozice znaku ``<`` začátečního tagu."""
    parent: Node | None = None
    children: list[Node] = field(default_factory=list)
    content_start: int | None = None
    """Bajt hned za ``>`` začátečního tagu (None u prázdného ``<x/>``)."""
    content_end: int | None = None
    """Bajt znaku ``<`` koncového tagu (None u prázdného ``<x/>``)."""
    _text: list[str] = field(default_factory=list, repr=False)

    @property
    def text(self) -> str:
        return "".join(self._text)

    def find(self, tag: str) -> Node | None:
        return next((c for c in self.children if c.tag == tag), None)

    def findall(self, tag: str) -> list[Node]:
        return [c for c in self.children if c.tag == tag]

    def iter(self) -> Iterator[Node]:
        stack = [self]
        while stack:
            n = stack.pop()
            yield n
            stack.extend(reversed(n.children))

    def ancestors(self) -> Iterator[Node]:
        p = self.parent
        while p is not None:
            yield p
            p = p.parent


_FORBIDDEN = (b"<!DOCTYPE", b"<!ENTITY", b"<!doctype", b"<!entity")


def _end_of_start_tag(data: bytes, pos: int) -> int:
    """Index za ``>`` začátečního tagu; respektuje uvozovky v atributech."""
    quote = 0
    i = pos + 1
    n = len(data)
    while i < n:
        ch = data[i]
        if quote:
            if ch == quote:
                quote = 0
        elif ch in (0x22, 0x27):  # " '
            quote = ch
        elif ch == 0x3E:  # >
            return i + 1
        i += 1
    raise GridError("xml_malformed", "Neukončený tag.", position=pos)


def parse(data: bytes) -> Node:
    """Rozparsuje dokument; při jakékoli vadě vyhodí ``GridError`` (nic neopravuje)."""
    head = data[:200].lstrip()
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    if head.startswith(b"<?xml") and b"encoding" in head.split(b"?>", 1)[0]:
        decl = head.split(b"?>", 1)[0].lower()
        if b'encoding="utf-8"' not in decl and b"encoding='utf-8'" not in decl:
            raise GridError("xml_encoding", "Podporováno je pouze kódování UTF-8.")
    if any(f in data for f in _FORBIDDEN):
        raise GridError("xml_dtd_forbidden", "Soubor obsahuje DTD nebo entity — z bezpečnostních důvodů odmítnut.")

    p = xml.parsers.expat.ParserCreate("UTF-8")
    p.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER)
    root: list[Node] = []
    stack: list[Node] = []

    def start(name: str, attrs: dict[str, str]) -> None:
        pos = p.CurrentByteIndex
        node = Node(tag=name, attrs=dict(attrs), start=pos, parent=stack[-1] if stack else None)
        end = _end_of_start_tag(data, pos)
        if data[end - 2 : end] != b"/>":
            node.content_start = end
        if stack:
            stack[-1].children.append(node)
        else:
            root.append(node)
        stack.append(node)

    def end(name: str) -> None:
        node = stack.pop()
        pos = p.CurrentByteIndex
        if node.content_start is not None and data[pos : pos + 2] == b"</":
            node.content_end = pos
        else:
            node.content_start = None

    def chars(text: str) -> None:
        if stack:
            stack[-1]._text.append(text)

    p.StartElementHandler = start
    p.EndElementHandler = end
    p.CharacterDataHandler = chars
    p.buffer_text = True
    try:
        p.Parse(data, True)
    except xml.parsers.expat.ExpatError as e:
        raise GridError("xml_malformed", f"Poškozené XML: {e}", line=e.lineno) from None
    if len(root) != 1:
        raise GridError("xml_malformed", "Dokument nemá právě jeden kořen.")
    return root[0]

"""Nezávislá kontrola výstupu před zveřejněním (MVP-05; spec. kap. 9.3, 14.3, 21.5).

Kontrola **nepoužívá plán přepisů** — oba soubory znovu rozparsuje a porovná:

1. Počet prvků ``XForm`` je stejný a soubory jsou bajtově shodné všude mimo obsah
   ``XForm`` (tím jsou prokazatelně beze změny tvary, texty, vrstvy, CutSetting…).
   Jedinou dovolenou výjimkou je nic — thumbnail se nemění.
2. Každý ``XForm`` je beze změny, kromě nejvyšší skupiny přesouvaného výrobku a
   ``BackupPath`` textů v ní; u nich musí výsledek přesně odpovídat ``T ∘ původní``
   (čistý posun: lineární část bajtově beze změny, ``e, f`` o plánovaný posun).
3. Výstup je znovu čitelný a struktura (tagy, atributy) je shodná.
4. Kopie výrobků (v1.16): nové nejvyšší tvary za posledním původním. Po jejich odebrání musí výstup
   splnit body 1–3. Každá kopie musí být bajtově shodná se svým zdrojovým elementem mimo obsah
   ``XForm`` a bez ``VertList`` / ``PrimList`` tvarů se sdíleným ID; tato ID musí být v původním
   souboru definována. ``XForm`` skupiny a ``BackupPath`` = ``T ∘ původní``, ostatní beze změny.
5. Cílový laser (v1.23): v hlavičce ``<LightBurnProject>`` smí být změněny jen atributy
   ``DeviceName``, ``MirrorX``, ``MirrorY`` přesně na očekávané hodnoty; ostatní atributy i jejich
   pořadí zůstávají. Po vrácení původní hlavičky musí výstup splnit body 1–4.
6. Vynechané objekty (v1.27): ve výstupu chybí právě vynechané nejvyšší tvary, ostatní jsou v původním
   pořadí. Navíc smí být jen definice sdílené geometrie (``VertList`` / ``PrimList``) přesunuté z
   vynechaného tvaru — bajtově shodné, v **prvním** ponechaném tvaru, který na dané ID odkazuje a sám
   ho nedefinuje. Po jejich odebrání musí výstup proti originálu bez vynechaných tvarů splnit body 1–5.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..adapters.lightburn import geometry as geo
from ..adapters.lightburn.pages import PAGE_XFORM, page_groups, page_shapes
from ..adapters.lightburn.xmltree import Node, parse
from ..domain.errors import GridError

TOLERANCE = 1e-3  # mm; zápis na 8 platných číslic
LINEAR_TOLERANCE = 1e-6  # koeficienty natočení (bezrozměrné)


@dataclass(frozen=True, slots=True)
class _X:
    node: Node
    top_index: int | None  # pořadí nejvyšší Shape, pod kterou leží (1-based), jinak None
    role: str  # "group" | "text_backup" | "other"


def _collect(root: Node, page: int = 0) -> list[_X]:
    out: list[_X] = []
    tops = {id(s): i for i, s in enumerate(page_shapes(root, page), start=1)}
    for n in root.iter():
        if n.tag != "XForm":
            continue
        owner = n.parent
        chain = [owner, *owner.ancestors()] if owner is not None else []
        top = next((tops[id(a)] for a in chain if id(a) in tops), None)
        if owner is not None and id(owner) in tops and owner.attrs.get("Type") == "Group":
            role = "group"
        elif owner is not None and owner.tag == "BackupPath" and owner.parent is not None and owner.parent.attrs.get("Type") == "Text":
            role = "text_backup"
        else:
            role = "other"
        out.append(_X(n, top, role))
    return out


def _masked(data: bytes, xs: list[_X]) -> bytes:
    parts, last = [], 0
    for x in sorted(xs, key=lambda x: x.node.content_start or 0):
        if x.node.content_start is None:
            continue
        parts.append(data[last : x.node.content_start])
        last = x.node.content_end
    parts.append(data[last:])
    return b"\x00".join(parts)


def _structure(root: Node) -> list[tuple[str, tuple]]:
    return [(n.tag, tuple(sorted(n.attrs.items()))) for n in root.iter()]


def _affine(move: tuple[float, ...]) -> tuple[float, ...]:
    return (1.0, 0.0, 0.0, 1.0, float(move[0]), float(move[1])) if len(move) == 2 else tuple(float(v) for v in move)


def _element_span(data: bytes, node: Node) -> tuple[int, int]:
    """Celé řádky elementu (odsazení + koncový tag + konec řádku), nezávisle na zapisovači."""
    if node.content_end is None:
        end = data.index(b"/>", node.start) + 2
    else:
        end = node.content_end + len(f"</{node.tag}>")
        if data[node.content_end:end] != f"</{node.tag}>".encode():
            raise ValueError("koncový tag")
    ls = data.rfind(b"\n", 0, node.start) + 1
    le = data.find(b"\n", end)
    le = len(data) if le < 0 else le + 1
    if data[ls:node.start].strip() == b"" and data[end:le].strip() == b"":
        return ls, le
    return node.start, end


def _without_shared(data: bytes, group: Node) -> tuple[bytes, int]:
    """Bajty skupiny bez ``VertList`` / ``PrimList`` tvarů s ``VertID`` / ``PrimID``; vrací i začátek."""
    a, b = _element_span(data, group)
    cut = []
    for n in group.iter():
        if n.tag == "Shape":
            for tag, attr in (("VertList", "VertID"), ("PrimList", "PrimID")):
                c = n.find(tag)
                if attr in n.attrs and c is not None:
                    cut.append(_element_span(data, c))
    out, last = bytearray(), a
    for x, y in sorted(cut):
        out += data[last:x]
        last = y
    out += data[last:b]
    return bytes(out), a


def _check_copy(src_data: bytes, src: Node, out_data: bytes, cp: Node, t: tuple[float, ...], k: int,
                defined: tuple[set[str], set[str]]) -> list[str]:
    problems: list[str] = []
    expect_struct = [(n.tag, tuple(sorted(n.attrs.items()))) for n in src.iter()
                     if not (n.tag in ("VertList", "PrimList") and n.parent is not None
                             and {"VertList": "VertID", "PrimList": "PrimID"}[n.tag] in n.parent.attrs)]
    if _structure(cp) != expect_struct:
        return [f"copy_structure: copy #{k}"]
    for n in cp.iter():
        if n.tag == "Shape" and (n.attrs.get("VertID") not in (None, *defined[0]) or n.attrs.get("PrimID") not in (None, *defined[1])):
            problems.append(f"copy_undefined_geometry_id: copy #{k}")
    src_bytes, src_base = _without_shared(src_data, src)
    a, b = _element_span(out_data, cp)
    cp_bytes = out_data[a:b]

    def xforms(root: Node) -> list[tuple[Node, str]]:
        out = []
        for n in root.iter():
            if n.tag != "XForm":
                continue
            owner = n.parent
            if owner is root:
                role = "group"
            elif owner is not None and owner.tag == "BackupPath" and owner.parent is not None and owner.parent.attrs.get("Type") == "Text":
                role = "text_backup"
            else:
                role = "other"
            out.append((n, role))
        return out

    xs_src, xs_cp = xforms(src), xforms(cp)
    if len(xs_src) != len(xs_cp):
        return problems + [f"copy_xform_count: copy #{k}"]

    def masked(blob: bytes, base: int, xs) -> bytes:
        parts, last = [], 0
        for n, _ in sorted(xs, key=lambda x: x[0].content_start or 0):
            parts.append(blob[last : n.content_start - base])
            last = n.content_end - base
        parts.append(blob[last:])
        return b"\x00".join(parts)

    # zdrojové pozice po vyjmutí sdílené geometrie: přepočítat posun pro každé XForm
    removed = []
    for n in src.iter():
        if n.tag == "Shape":
            for tag, attr in (("VertList", "VertID"), ("PrimList", "PrimID")):
                c = n.find(tag)
                if attr in n.attrs and c is not None:
                    removed.append(_element_span(src_data, c))

    def shifted(pos: int) -> int:
        return pos - src_base - sum(y - x for x, y in removed if y <= pos)

    parts, last = [], 0
    for n, _ in sorted(xs_src, key=lambda x: x[0].content_start or 0):
        parts.append(src_bytes[last : shifted(n.content_start)])
        last = shifted(n.content_end)
    parts.append(src_bytes[last:])
    if b"\x00".join(parts) != masked(cp_bytes, a, xs_cp):
        problems.append(f"copy_bytes_differ: copy #{k}")
    for (na, role), (nb, _) in zip(xs_src, xs_cp):
        ta, tb = na.text, nb.text
        if role == "other":
            if ta != tb:
                problems.append(f"copy_unexpected_xform_change: copy #{k}")
            continue
        try:
            va, vb = geo.parse_xform(ta), geo.parse_xform(tb)
        except geo.GeometryError:
            problems.append(f"copy_unreadable_xform: copy #{k}")
            continue
        expected = geo.compose(_affine(t), va)  # type: ignore[arg-type]
        if any(abs(vb[i] - expected[i]) > LINEAR_TOLERANCE * max(1.0, abs(expected[i])) for i in range(4)):
            problems.append(f"copy_wrong_rotation: copy #{k} role={role}")
        if abs(vb[4] - expected[4]) > TOLERANCE or abs(vb[5] - expected[5]) > TOLERANCE:
            problems.append(f"copy_wrong_translation: copy #{k} role={role}")
    return problems


def _check_header(source: bytes, output: bytes, header: dict[str, str]) -> tuple[list[str], bytes]:
    """Ověří změnu hlavičky a vrátí výstup s původní hlavičkou (pro další, bajtové kontroly)."""
    r_src, r_out = parse(source), parse(output)
    if r_out.content_start is None or r_src.content_start is None:
        return ["header_unreadable"], output
    expected = dict(r_src.attrs)
    for k, v in header.items():
        if k not in ("DeviceName", "MirrorX", "MirrorY") or k not in expected:
            return [f"header_attr_not_allowed: {k}"], output
        expected[k] = v
    problems = []
    if r_out.attrs != expected or list(r_out.attrs) != list(r_src.attrs):
        problems.append("header_mismatch")
    # mimo hodnoty změněných atributů musí být začáteční tag bajtově shodný
    pat = rb'(\s(?:' + b"|".join(k.encode("ascii") for k in header) + rb')=")[^"]*(")'
    src_tag = source[r_src.start:r_src.content_start]
    out_tag = output[r_out.start:r_out.content_start]
    if re.sub(pat, rb"\1\2", src_tag) != re.sub(pat, rb"\1\2", out_tag):
        problems.append("header_bytes_changed")
    return problems, output[:r_out.start] + src_tag + output[r_out.content_start:]


_LISTS = (("VertList", "VertID"), ("PrimList", "PrimID"))


def _cut(data: bytes, spans: list[tuple[int, int]]) -> bytes:
    out, last = bytearray(), 0
    for a, b in sorted(spans):
        out += data[last:a]
        last = b
    out += data[last:]
    return bytes(out)


def _definitions(data: bytes, nodes: list[Node]) -> dict[tuple[str, str], bytes]:
    """Definice sdílených seznamů ``(tag, id) → bajty elementu`` v podstromech ``nodes``."""
    out: dict[tuple[str, str], bytes] = {}
    for top in nodes:
        for n in top.iter():
            if n.tag == "Shape":
                for tag, attr in _LISTS:
                    c = n.find(tag)
                    if attr in n.attrs and c is not None:
                        out.setdefault((tag, n.attrs[attr]), data[c.start:_element_span(data, c)[1]].rstrip())
    return out


def _strip_relocated(source: bytes, output: bytes, omitted_nodes: list[Node]) -> tuple[list[str], bytes, set[tuple[str, str]]]:
    """Definice sdílené geometrie z vynechaných tvarů musí ve výstupu být právě jednou, bajtově shodné,
    v **prvním** tvaru (v pořadí dokumentu), který na dané ID odkazuje. Vrátí výstup bez nich."""
    defs = _definitions(source, omitted_nodes)
    if not defs:
        return [], output, set()
    r_out = parse(output)
    problems: list[str] = []
    cut: list[tuple[int, int]] = []
    relocated: set[tuple[str, str]] = set()
    index: dict[tuple[str, str], list[Node]] = {}
    for n in r_out.iter():
        if n.tag == "Shape":
            for tag, attr in _LISTS:
                if attr in n.attrs:
                    index.setdefault((tag, n.attrs[attr]), []).append(n)
    for (tag, ident), blob in defs.items():
        refs = index.get((tag, ident), [])
        if not refs:
            continue  # nikdo na ID neodkazuje: definice se nepřenáší
        if not any(n.find(tag) is not None for n in refs):
            problems.append(f"geometry_definition_missing: {tag} {ident}")
            continue
        c = refs[0].find(tag)
        if c is None:
            continue  # ID dál definuje ponechaný tvar originálu; ověří bajtové porovnání
        span = _element_span(output, c)
        if output[c.start:span[1]].rstrip() != blob:
            continue  # vlastní definice ponechaného tvaru
        relocated.add((tag, ident))
        cut.append(span)
    return problems, _cut(output, cut), relocated


def _strip_new_pages(source: bytes, output: bytes, page: int, new_pages, defined) -> tuple[list[str], bytes]:
    """Nové stránky (desky 2…) hned za rozkládanou stránkou: přesně povolený obal a jen kopie výrobků."""
    r_src, r_out = parse(source), parse(output)
    src_groups, out_groups = page_groups(r_src), page_groups(r_out)
    if len(out_groups) != len(src_groups) + len(new_pages):
        return ["page_count_mismatch"], output
    new_nodes = out_groups[page:page + len(new_pages)]
    src_shapes = page_shapes(r_src, page)
    problems: list[str] = []
    k = 0
    for (name, pieces), g in zip(new_pages, new_nodes):
        if list(g.attrs.items()) != [("Type", "Group"), ("SubType", "Page"), ("Name", name)]:
            problems.append(f"page_attributes: {name}")
        x = g.find("XForm")
        ch = g.find("Children")
        if x is None or x.text != PAGE_XFORM or [c.tag for c in g.children] != ["XForm", "Children"] or ch is None:
            problems.append(f"page_structure: {name}")
            continue
        kids = ch.findall("Shape")
        if len(kids) != len(pieces) or len(ch.children) != len(kids):
            problems.append(f"page_piece_count: {name}")
            continue
        for (src_idx, t), node in zip(pieces, kids):
            k += 1
            if not 1 <= src_idx <= len(src_shapes):
                problems.append(f"page_piece_source: {name}")
                continue
            problems += _check_copy(source, src_shapes[src_idx - 1], output, node, t, k, defined)
    cut = []
    for g in new_nodes:
        cut.append(_element_span(output, g))
    return problems, _cut(output, cut)


def verify_output(source: bytes, output: bytes, moves_file: dict[int, tuple[float, ...]],
                  copies: list[tuple[int, tuple[float, ...]]] = (), header: dict[str, str] | None = None,
                  omitted: set[int] | frozenset[int] = frozenset(), page: int = 0,
                  new_pages: list[tuple[str, list[tuple[int, tuple[float, ...]]]]] = ()) -> list[str]:
    """Vrátí seznam nalezených problémů (prázdný = v pořádku).

    Pořadí tvarů (1-based) se počítá na rozkládané stránce ``page``. ``moves_file`` mapuje pořadí
    nejvyšší skupiny na posun ``(dx, dy)`` nebo afinní transformaci ``(a, b, c, d, e, f)`` v souřadnicích
    souboru. ``copies`` = kopie na stránce v pořadí výstupu: (pořadí zdrojové skupiny, transformace).
    ``omitted`` = vynechané tvary stránky. ``new_pages`` = nové stránky hned za ``page``:
    ``[(název, [(pořadí zdrojové skupiny, transformace), …]), …]`` (v1.29).
    """
    problems: list[str] = []
    try:
        r_src, r_out = parse(source), parse(output)
    except GridError as e:
        return [f"output_unreadable: {e}"]
    if header:
        found, output = _check_header(source, output, header)
        problems += found
    try:
        src_shapes = page_shapes(r_src, page)
    except IndexError:
        return problems + ["unknown_page"]
    if any(i < 1 or i > len(src_shapes) for i in omitted):
        return problems + ["omitted_unknown"]
    if any(i in omitted for i in moves_file) or any(i in omitted for i, _ in copies):
        problems.append("omitted_item_moved_or_copied")
    relocated: set[tuple[str, str]] = set()
    try:
        if omitted:
            found, output, relocated = _strip_relocated(source, output, [src_shapes[i - 1] for i in sorted(omitted)])
            problems += found
        omitted_defs = set(_definitions(source, [src_shapes[i - 1] for i in omitted]))
        all_defs = {(t, n.attrs[a]) for n in r_src.iter() if n.tag == "Shape" for t, a in _LISTS
                    if a in n.attrs and n.find(t) is not None}
        kept_defs = all_defs - omitted_defs | relocated | {k for k in all_defs & omitted_defs
                                                             if _defined_outside(r_src, src_shapes, omitted, k)}
        defined = ({i for t, i in kept_defs if t == "VertList"}, {i for t, i in kept_defs if t == "PrimList"})
        if new_pages:
            found, output = _strip_new_pages(source, output, page, list(new_pages), defined)
            problems += found
        if omitted:
            kept = [i for i in range(1, len(src_shapes) + 1) if i not in omitted]
            renumber = {i: k for k, i in enumerate(kept, start=1)}
            source = _cut(source, [_element_span(source, src_shapes[i - 1]) for i in omitted])
            moves_file = {renumber[i]: m for i, m in moves_file.items() if i in renumber}
            copies = [(renumber[i], t) for i, t in copies if i in renumber]
        r_src, r_out = parse(source), parse(output)
    except (GridError, ValueError, IndexError) as e:
        return problems + [f"output_unreadable: {e}"]

    if copies:
        src_tops, out_tops = page_shapes(r_src, page), page_shapes(r_out, page)
        if len(out_tops) != len(src_tops) + len(copies):
            return problems + ["copy_count_mismatch"]
        extra = out_tops[len(src_tops):]
        try:
            for k, ((src_idx, t), cp) in enumerate(zip(copies, extra), start=1):
                problems += _check_copy(source, src_tops[src_idx - 1], output, cp, t, k, defined)
            first, _ = _element_span(output, extra[0])
            _, last = _element_span(output, extra[-1])
        except (ValueError, IndexError):
            return problems + ["copy_unreadable"]
        output = output[:first] + output[last:]  # zbytek musí odpovídat běžnému přesunu
        try:
            r_out = parse(output)
        except GridError as e:
            return problems + [f"output_unreadable: {e}"]

    if _structure(r_src) != _structure(r_out):
        problems.append("structure_changed")

    xs_src, xs_out = _collect(r_src, page), _collect(r_out, page)
    if len(xs_src) != len(xs_out):
        return problems + ["xform_count_changed"]
    if _masked(source, xs_src) != _masked(output, xs_out):
        problems.append("bytes_outside_xform_changed")

    for a, b in zip(xs_src, xs_out):
        ta, tb = a.node.text, b.node.text
        move = moves_file.get(a.top_index) if a.top_index is not None else None
        allowed = move is not None and a.role in ("group", "text_backup")
        if not allowed:
            if ta != tb:
                problems.append(f"unexpected_xform_change: shape #{a.top_index} role={a.role}")
            continue
        try:
            va, vb = geo.parse_xform(ta), geo.parse_xform(tb)
        except geo.GeometryError:
            problems.append(f"unreadable_xform: shape #{a.top_index}")
            continue
        t = _affine(move)
        if t[:4] == (1.0, 0.0, 0.0, 1.0):
            if ta.split()[:4] != tb.split()[:4]:
                problems.append(f"linear_part_changed: shape #{a.top_index}")
        expected = geo.compose(t, va)  # type: ignore[arg-type]
        if any(abs(vb[i] - expected[i]) > LINEAR_TOLERANCE * max(1.0, abs(expected[i])) for i in range(4)):
            problems.append(f"wrong_rotation: shape #{a.top_index} role={a.role}")
        if abs(vb[4] - expected[4]) > TOLERANCE or abs(vb[5] - expected[5]) > TOLERANCE:
            problems.append(f"wrong_translation: shape #{a.top_index} role={a.role}")
    return problems


def _defined_outside(root: Node, shapes: list[Node], omitted, key: tuple[str, str]) -> bool:
    """Je ID definované i mimo vynechané tvary rozkládané stránky?"""
    tag, ident = key
    attr = dict(_LISTS)[tag]
    inside = {id(n) for i in omitted for n in shapes[i - 1].iter()}
    return any(n.tag == "Shape" and n.attrs.get(attr) == ident and n.find(tag) is not None and id(n) not in inside
               for n in root.iter())

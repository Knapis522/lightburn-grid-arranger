"""Generátor **syntetických** projektů `.lbrn2` napodobujících LightBurn 2.2 (KAL-00).

Žádná zákaznická data. Struktura odpovídá vzorku V-001: CRLF, odsazení mezerami,
skupiny s ``Children``, cesty s ``VertList``/``PrimList``, text s ``BackupPath``
ve světových souřadnicích.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import quoteattr

Affine = tuple[float, float, float, float, float, float]
I: Affine = (1, 0, 0, 1, 0, 0)


def compose(o: Affine, i: Affine) -> Affine:
    a, b, c, d, e, f = o
    a2, b2, c2, d2, e2, f2 = i
    return (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2, a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def xf(m: Affine) -> str:
    return " ".join(format(v, ".8g") for v in m)


_ids = {"v": 0}


def _vid() -> str:
    _ids["v"] += 1
    return str(_ids["v"])


@dataclass
class Path:
    corners: list[tuple[float, float]]
    cut: int = 2
    xform: Affine = (1, 0, 0, 1, 0, 0)
    prims: str = "LineClosed"
    share_from: "Path | None" = None
    vid: str = field(default_factory=_vid)
    bezier_ctrl: bool = False

    def lines(self, ind: str) -> list[str]:
        vid = self.share_from.vid if self.share_from else self.vid
        out = [f'{ind}<Shape Type="Path" CutIndex="{self.cut}" VertID="{vid}" PrimID="{vid}">', f"{ind}    <XForm>{xf(self.xform)}</XForm>"]
        if not self.share_from:
            if self.bezier_ctrl:
                vl = "".join(f"V{x} {y}c0x{x + 1}c0y{y}c1x{x - 1}c1y{y}" for x, y in self.corners)
            else:
                vl = "".join(f"V{x} {y}c0x1c1x1" for x, y in self.corners)
            out += [f"{ind}    <VertList>{vl}</VertList>", f"{ind}    <PrimList>{self.prims}</PrimList>"]
        out.append(f"{ind}</Shape>")
        return out


def rect(x: float, y: float, w: float, h: float, **kw) -> Path:
    return Path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], **kw)


@dataclass
class Text:
    s: str
    box: tuple[float, float, float, float]  # x, y, w, h glyph box in local coords
    xform: Affine = (1, 0, 0, 1, 0, 0)
    backup: bool = True
    backup_offset: tuple[float, float] = (0.0, 0.0)  # simulace nesouladu
    cut: int = 1

    def lines(self, ind: str, world: Affine) -> list[str]:
        out = [f'{ind}<Shape Type="Text" CutIndex="{self.cut}" Font="Arial,-1,100,5,50,0,0,0,0,0" Str={quoteattr(self.s)} H="10" LS="0" LnS="0" Ah="1" Av="1" Weld="1" HasBackupPath="{1 if self.backup else 0}">']
        if self.backup:
            m = compose(world, self.xform)
            m = (*m[:4], m[4] + self.backup_offset[0], m[5] + self.backup_offset[1])
            x, y, w, h = self.box
            vl = f"V{x} {y}c0x1c1x1V{x + w} {y}c0x1c1x1V{x + w} {y + h}c0x1c1x1V{x} {y + h}c0x1c1x1"
            out += [f'{ind}    <BackupPath Type="Path" CutIndex="{self.cut}">', f"{ind}        <XForm>{xf(m)}</XForm>",
                    f"{ind}        <VertList>{vl}</VertList>", f"{ind}        <PrimList>LineClosed</PrimList>", f"{ind}    </BackupPath>"]
        out += [f"{ind}    <XForm>{xf(self.xform)}</XForm>", f"{ind}</Shape>"]
        return out


@dataclass
class Native:
    """Nativní tvar LightBurnu (Ellipse / Rect / Polygon) — rozměry v atributech, střed v XForm."""

    kind: str
    attrs: dict
    xform: Affine = (1, 0, 0, 1, 0, 0)
    cut: int = 2
    children: str = ""

    def lines(self, ind: str, world: Affine | None = None) -> list[str]:
        a = "".join(f' {k}="{v}"' for k, v in self.attrs.items())
        out = [f'{ind}<Shape Type="{self.kind}" CutIndex="{self.cut}"{a}>', f"{ind}    <XForm>{xf(self.xform)}</XForm>"]
        if self.children:
            out.append(ind + "    " + self.children)
        out.append(f"{ind}</Shape>")
        return out


def ellipse(cx: float, cy: float, rx: float, ry: float | None = None, **kw) -> Native:
    return Native("Ellipse", {"Rx": rx, "Ry": rx if ry is None else ry}, xform=(1, 0, 0, 1, cx, cy), **kw)


def keyring(cx: float, cy: float, r: float = 20, text: str = "K1", xform: Affine = (1, 0, 0, 1, 0, 0)) -> Group:
    """Klíčenka jako v Test_tvary_A: vnořená skupina (kruh + otvor) a text."""
    inner = Group([ellipse(cx, cy, r, cut=0), ellipse(cx, cy - r + 4.5, 2.5, cut=0)])
    return Group([inner, Text(text, (cx - 8, cy - 4, 16, 8))], xform=xform)


@dataclass
class Raw:
    """Libovolný tvar (např. neznámý typ) — vložen doslova."""

    xml: str

    def lines(self, ind: str, world: Affine | None = None) -> list[str]:
        return [ind + self.xml]


@dataclass
class Group:
    children: list
    xform: Affine = (1, 0, 0, 1, 0, 0)
    extra_attrs: str = ""

    def lines(self, ind: str, world: Affine = I) -> list[str]:
        m = compose(world, self.xform)
        out = [f'{ind}<Shape Type="Group" CutIndex="0"{self.extra_attrs}>', f"{ind}    <XForm>{xf(self.xform)}</XForm>", f"{ind}    <Children>"]
        for c in self.children:
            if isinstance(c, (Group, Text)):
                out += c.lines(ind + "        ", m)
            elif isinstance(c, (Raw, Native)):
                out += c.lines(ind + "        ")
            else:
                out += c.lines(ind + "        ")
        out += [f"{ind}    </Children>", f"{ind}</Shape>"]
        return out


def card(x: float, y: float, w: float = 100, h: float = 60, text: str = "Karta", **kw) -> Group:
    """Kartička jako ve V-001: skupina s posunem, obrys (zaoblení nahrazeno obdélníkem) a text."""
    return Group([rect(0, 0, w, h), Text(text, (5, 5, w - 10, 10), xform=(1, 0, 0, 1, 0, 0))], xform=(1, 0, 0, 1, x, y), **kw)


def project(shapes: list, mirror_x: bool = True, mirror_y: bool = True, app: str = "2.2.00", fmt: str = "1",
            extra_root_attrs: str = "", extra_top: str = "") -> bytes:
    L = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<LightBurnProject AppVersion="{app}" DeviceName="Syntetický laser" FormatVersion="{fmt}" MaterialHeight="0" '
        f'MirrorX="{mirror_x}" MirrorY="{mirror_y}" AskForSendName="True" CurrentPage="0" Page0Name="Stránka 1"{extra_root_attrs}>',
        '    <Thumbnail Source="iVBORw0KGgoAAAANSUhEUg=="/>',
        "    <VariableText>",
        '        <Start Value="0"/>',
        "    </VariableText>",
        '    <CutSetting type="Cut">',
        '        <index Value="1"/>',
        '        <name Value="C01"/>',
        '        <maxPower Value="18"/>',
        "    </CutSetting>",
        '    <CutSetting type="Cut">',
        '        <index Value="2"/>',
        '        <name Value="C02"/>',
        '        <maxPower Value="40"/>',
        '        <speed Value="65"/>',
        "    </CutSetting>",
    ]
    for s in shapes:
        L += s.lines("    ") if not isinstance(s, (Group,)) else s.lines("    ", I)
    if extra_top:
        L.append("    " + extra_top)
    L += ['    <Notes ShowOnLoad="0" Notes=""/>', "</LightBurnProject>", ""]
    return "\r\n".join(L).encode("utf-8")

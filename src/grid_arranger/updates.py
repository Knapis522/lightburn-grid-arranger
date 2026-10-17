"""Kontrola a stažení aktualizací z GitHub Releases (spec. v1.11 kap. 32; ADR-0004).

Bez Qt — jen standardní knihovna, aby šlo vše testovat bez sítě (síťové funkce mají
injektovatelný ``urlopen``).

Zásady:

* Nic se nestahuje ani nespouští bez souhlasu uživatele; aktualizace se jen **nabídne**.
* Vždy se nabízí **nejnovější** vydání (instalátor obsahuje celou aplikaci), mezilehlé
  verze se neinstalují. Odmítnutá („přeskočená“) verze se znovu nenabízí automaticky,
  novější ano.
* Stažený instalátor se ověří proti ``SHA256SUMS.txt`` z téhož vydání; bez shody se nespustí.
* Při jakékoli chybě sítě/API výroba pokračuje; automatická kontrola chyby jen zaznamená.
* Anonymní GitHub API funguje jen u **veřejného** repozitáře (soukromý vrací 404).
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from .version import __version__, display_version

REPOSITORY = "Knapis522/lightburn-grid-arranger"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=30"
RELEASES_PAGE = f"https://github.com/{REPOSITORY}/releases"
SUMS_NAME = "SHA256SUMS.txt"
SETUP_RE = re.compile(r"^GridArranger-Setup-v(?P<version>[0-9A-Za-z.\-]+)-win-x64\.exe$")
AUTO_CHECK_INTERVAL = timedelta(hours=20)  # nejvýš jednou denně
TIMEOUT_S = 15
_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.\-]+))?$")


class UpdateError(Exception):
    """Chyba kontroly/stažení. ``code`` je stabilní kód pro lokalizovanou hlášku v GUI."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


# --- verze ----------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SemVer:
    major: int
    minor: int
    patch: int
    pre: tuple[str, ...] = ()

    @classmethod
    def parse(cls, text: str) -> SemVer | None:
        m = _SEMVER_RE.match(text.strip())
        if not m:
            return None
        pre = tuple(m.group(4).split(".")) if m.group(4) else ()
        if any(p == "" for p in pre):
            return None
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)), pre)

    @property
    def is_prerelease(self) -> bool:
        return bool(self.pre)

    def key(self) -> tuple:
        # SemVer 2.0 §11: vydání > předběžná verze; číselné identifikátory < textové; delší > kratší při shodě
        pre = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in self.pre)
        return (self.major, self.minor, self.patch, 0 if self.pre else 1, pre)

    def __lt__(self, other: SemVer) -> bool:
        return self.key() < other.key()

    def __gt__(self, other: SemVer) -> bool:
        return self.key() > other.key()

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}" + ("-" + ".".join(self.pre) if self.pre else "")


def current_version() -> SemVer:
    v = SemVer.parse(display_version(__version__))
    assert v is not None
    return v


# --- vydání ---------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Asset:
    name: str
    url: str
    size: int = 0


@dataclass(frozen=True, slots=True)
class Release:
    version: SemVer
    tag: str
    title: str
    notes: str
    prerelease: bool
    page_url: str
    assets: tuple[Asset, ...] = ()

    def asset(self, name: str) -> Asset | None:
        return next((a for a in self.assets if a.name == name), None)

    @property
    def setup(self) -> Asset | None:
        """Instalátor pro Windows, jehož verze v názvu odpovídá tagu."""
        for a in self.assets:
            m = SETUP_RE.match(a.name)
            if m and SemVer.parse(m.group("version")) == self.version:
                return a
        return None

    @property
    def sums(self) -> Asset | None:
        return self.asset(SUMS_NAME)


def parse_releases(data: object) -> list[Release]:
    """Odpověď ``GET /repos/{repo}/releases`` → vydání (bez konceptů a nečitelných tagů)."""
    if not isinstance(data, list):
        raise UpdateError("bad_response", "expected a list of releases")
    out: list[Release] = []
    for r in data:
        if not isinstance(r, dict) or r.get("draft"):
            continue
        tag = str(r.get("tag_name") or "")
        version = SemVer.parse(tag)
        if version is None:
            continue
        assets = tuple(
            Asset(str(a.get("name", "")), str(a.get("browser_download_url", "")), int(a.get("size") or 0))
            for a in r.get("assets") or [] if isinstance(a, dict)
        )
        out.append(Release(version, tag, str(r.get("name") or tag), str(r.get("body") or ""),
                           bool(r.get("prerelease")) or version.is_prerelease, str(r.get("html_url") or RELEASES_PAGE),
                           assets))
    return out


@dataclass(frozen=True)
class UpdateInfo:
    current: SemVer
    latest: Release
    newer: tuple[Release, ...] = field(default=())
    """Všechna novější vydání v kanálu, od nejnovějšího — pro přehled změn od nainstalované verze."""


def find_update(releases: list[Release], current: SemVer, include_prerelease: bool) -> UpdateInfo | None:
    """Nejnovější vydání novější než ``current``; předběžné verze jen na přání."""
    newer = sorted((r for r in releases if r.version > current and (include_prerelease or not r.prerelease)),
                   key=lambda r: r.version.key(), reverse=True)
    return UpdateInfo(current, newer[0], tuple(newer)) if newer else None


def should_offer_automatically(info: UpdateInfo | None, skipped: str) -> bool:
    """Automatická kontrola nenabízí verzi, kterou uživatel přeskočil; novější ano."""
    return info is not None and info.latest.tag != skipped


def auto_check_due(last_check: str, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    try:
        last = datetime.fromisoformat(last_check)
    except (TypeError, ValueError):
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return not (timedelta(0) <= now - last < AUTO_CHECK_INTERVAL)


# --- síť ------------------------------------------------------------------------------------

Urlopen = Callable[..., object]


def _request(url: str, accept: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={
        "Accept": accept,
        "User-Agent": f"GridArranger/{display_version()}",
        "X-GitHub-Api-Version": "2022-11-28",
    })


def fetch_releases(urlopen: Urlopen = urllib.request.urlopen, url: str = API_URL) -> list[Release]:
    try:
        with urlopen(_request(url, "application/vnd.github+json"), timeout=TIMEOUT_S) as resp:  # type: ignore[attr-defined]
            raw = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise UpdateError("not_found", "repository not public or no releases") from e
        if e.code in (403, 429):
            raise UpdateError("rate_limited", str(e.code)) from e
        raise UpdateError("network", f"HTTP {e.code}") from e
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise UpdateError("network", str(e)) from e
    try:
        return parse_releases(json.loads(raw.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise UpdateError("bad_response", str(e)) from e


def parse_sha256sums(text: str) -> dict[str, str]:
    """``<64 hex>  <název>`` (formát sha256sum, i s ``*`` před názvem) → {název: hash}."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$", line)
        if m:
            out[m.group(2)] = m.group(1).lower()
    return out


def download_installer(
    release: Release,
    dest_dir: Path,
    urlopen: Urlopen = urllib.request.urlopen,
    progress: Callable[[int, int], None] | None = None,
    cancelled: Callable[[], bool] = lambda: False,
) -> Path:
    """Stáhne instalátor vydání a ověří SHA-256. Vrátí cestu k ověřenému souboru."""
    setup, sums = release.setup, release.sums
    if setup is None:
        raise UpdateError("no_installer", release.tag)
    if sums is None:
        raise UpdateError("checksum_missing", release.tag)
    try:
        with urlopen(_request(sums.url, "application/octet-stream"), timeout=TIMEOUT_S) as resp:  # type: ignore[attr-defined]
            expected = parse_sha256sums(resp.read().decode("utf-8", "replace")).get(setup.name)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise UpdateError("network", str(e)) from e
    if not expected:
        raise UpdateError("checksum_missing", setup.name)

    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / setup.name
    part = dest_dir / (setup.name + ".part")
    digest = hashlib.sha256()
    done = 0
    try:
        with urlopen(_request(setup.url, "application/octet-stream"), timeout=TIMEOUT_S) as resp, part.open("wb") as f:  # type: ignore[attr-defined]
            total = int(getattr(resp, "headers", {}).get("Content-Length") or setup.size or 0)
            while True:
                if cancelled():
                    raise UpdateError("cancelled")
                chunk = resp.read(256 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                digest.update(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
    except UpdateError:
        part.unlink(missing_ok=True)
        raise
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        part.unlink(missing_ok=True)
        raise UpdateError("network", str(e)) from e
    if digest.hexdigest() != expected:
        part.unlink(missing_ok=True)
        raise UpdateError("checksum_mismatch", setup.name)
    target.unlink(missing_ok=True)  # jen náš vlastní dočasný soubor ve vlastní složce
    part.rename(target)
    return target


# --- instalace ------------------------------------------------------------------------------

def is_installed_copy(exe_dir: Path, frozen: bool) -> bool:
    """Aplikace nainstalovaná instalátorem (vedle EXE je odinstalátor Inno Setup), ne ZIP/vývoj."""
    return frozen and (exe_dir / "unins000.exe").is_file()


def installer_command(installer: Path) -> list[str]:
    """Spuštění instalátoru po souhlasu uživatele: bez dotazů, s ukazatelem průběhu; po instalaci
    se aplikace sama znovu spustí (sekce [Run] v ``packaging/GridArranger.iss``)."""
    return [str(installer), "/SILENT", "/SP-", "/NOCANCEL", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS"]

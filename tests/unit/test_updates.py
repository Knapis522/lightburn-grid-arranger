"""Aktualizace z GitHub Releases (spec. v1.11 kap. 32) — bez sítě, s falešným urlopen."""

from __future__ import annotations

import hashlib
import io
import json
import urllib.error
from datetime import datetime, timedelta, timezone

import pytest

from grid_arranger.updates import (
    SemVer, UpdateError, auto_check_due, download_installer, fetch_releases, find_update, installer_command,
    is_installed_copy, parse_releases, parse_sha256sums, should_offer_automatically,
)

V = SemVer.parse


@pytest.mark.parametrize("a, b", [
    ("0.1.0-alpha.1", "0.1.0-alpha.2"), ("0.1.0-alpha.2", "0.1.0-alpha.10"), ("0.1.0-alpha.9", "0.1.0-beta.1"),
    ("0.1.0-beta.1", "0.1.0-rc.1"), ("0.1.0-rc.1", "0.1.0"), ("0.1.0", "0.1.1"), ("0.9.9", "1.0.0"),
    ("1.0.0-alpha", "1.0.0-alpha.1"), ("1.0.0-alpha.1", "1.0.0-alpha.beta"), ("v1.2.3", "v1.10.0"),
])
def test_semver_precedence(a, b):
    assert V(a) < V(b) and V(b) > V(a) and not V(a) > V(b)


@pytest.mark.parametrize("bad", ["1.0", "v1", "1.0.0-", "1.0.0-a..b", "latest", ""])
def test_semver_rejects_invalid(bad):
    assert V(bad) is None


def gh_release(tag, prerelease=False, draft=False, setup=True, sums=True, body="notes"):
    ver = tag.lstrip("v")
    assets = []
    if setup:
        assets.append({"name": f"GridArranger-Setup-v{ver}-win-x64.exe", "browser_download_url": f"https://dl/{tag}/setup.exe", "size": 10})
    assets.append({"name": f"GridArranger-v{ver}-win-x64.zip", "browser_download_url": f"https://dl/{tag}/app.zip", "size": 10})
    if sums:
        assets.append({"name": "SHA256SUMS.txt", "browser_download_url": f"https://dl/{tag}/sums", "size": 1})
    return {"tag_name": tag, "name": f"Grid Arranger {tag}", "body": body, "prerelease": prerelease, "draft": draft,
            "html_url": f"https://github.com/x/releases/tag/{tag}", "assets": assets}


RELEASES = [
    gh_release("v0.2.0", body="newest stable"),
    gh_release("v0.3.0-alpha.1", prerelease=True),
    gh_release("v0.1.0"),
    gh_release("v0.4.0", draft=True),          # koncept se nikdy nenabízí
    gh_release("nightly"),                      # nečitelný tag se ignoruje
    gh_release("v0.1.0-alpha.2", prerelease=True),
]


def test_parse_releases_skips_drafts_and_bad_tags():
    tags = [r.tag for r in parse_releases(RELEASES)]
    assert tags == ["v0.2.0", "v0.3.0-alpha.1", "v0.1.0", "v0.1.0-alpha.2"]
    with pytest.raises(UpdateError) as e:
        parse_releases({"message": "x"})
    assert e.value.code == "bad_response"


def test_setup_asset_must_match_tag_version():
    r = parse_releases([gh_release("v0.2.0")])[0]
    assert r.setup.name == "GridArranger-Setup-v0.2.0-win-x64.exe" and r.sums is not None
    wrong = gh_release("v0.2.0")
    wrong["assets"][0]["name"] = "GridArranger-Setup-v0.1.9-win-x64.exe"
    assert parse_releases([wrong])[0].setup is None


def test_always_latest_skipping_intermediate_versions():
    rel = parse_releases(RELEASES)
    info = find_update(rel, V("0.1.0-alpha.1"), include_prerelease=False)
    assert info.latest.tag == "v0.2.0"
    assert [r.tag for r in info.newer] == ["v0.2.0", "v0.1.0"]  # přehled změn od nainstalované verze
    info = find_update(rel, V("0.1.0-alpha.1"), include_prerelease=True)
    assert info.latest.tag == "v0.3.0-alpha.1"
    assert [r.tag for r in info.newer] == ["v0.3.0-alpha.1", "v0.2.0", "v0.1.0", "v0.1.0-alpha.2"]


def test_no_update_when_current_is_newest():
    rel = parse_releases(RELEASES)
    assert find_update(rel, V("0.2.0"), include_prerelease=False) is None
    assert find_update(rel, V("0.3.0-alpha.1"), include_prerelease=True) is None


def test_skipped_version_not_offered_but_newer_is():
    rel = parse_releases(RELEASES)
    info = find_update(rel, V("0.1.0"), include_prerelease=False)
    assert not should_offer_automatically(info, skipped="v0.2.0")
    assert should_offer_automatically(info, skipped="v0.1.5")
    assert not should_offer_automatically(None, skipped="")


def test_auto_check_at_most_once_per_day():
    now = datetime(2026, 10, 17, 9, 0, tzinfo=timezone.utc)
    assert auto_check_due("", now)
    assert auto_check_due("garbage", now)
    assert not auto_check_due((now - timedelta(hours=2)).isoformat(), now)
    assert auto_check_due((now - timedelta(hours=25)).isoformat(), now)
    assert auto_check_due((now + timedelta(days=3)).isoformat(), now)  # posunuté hodiny → zkontrolovat


class FakeResp(io.BytesIO):
    def __init__(self, data: bytes):
        super().__init__(data)
        self.headers = {"Content-Length": str(len(data))}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def fake_urlopen(routes):
    calls = []

    def _open(req, timeout=None):
        url = req.full_url
        calls.append((url, dict(req.header_items())))
        r = routes[url]
        if isinstance(r, Exception):
            raise r
        return FakeResp(r)

    _open.calls = calls
    return _open


def test_fetch_releases_sends_user_agent_and_parses():
    op = fake_urlopen({"https://api/x": json.dumps(RELEASES).encode()})
    assert len(fetch_releases(op, "https://api/x")) == 4
    headers = op.calls[0][1]
    assert headers["User-agent"].startswith("GridArranger/") and "github" in headers["Accept"]


@pytest.mark.parametrize("exc, code", [
    (urllib.error.HTTPError("u", 404, "nf", {}, None), "not_found"),
    (urllib.error.HTTPError("u", 403, "rl", {}, None), "rate_limited"),
    (urllib.error.HTTPError("u", 500, "e", {}, None), "network"),
    (urllib.error.URLError("offline"), "network"),
    (TimeoutError(), "network"),
])
def test_fetch_errors_have_codes(exc, code):
    with pytest.raises(UpdateError) as e:
        fetch_releases(fake_urlopen({"https://api/x": exc}), "https://api/x")
    assert e.value.code == code


def test_fetch_bad_json():
    with pytest.raises(UpdateError) as e:
        fetch_releases(fake_urlopen({"https://api/x": b"<html>"}), "https://api/x")
    assert e.value.code == "bad_response"


def test_parse_sha256sums():
    h = "a" * 64
    text = f"{h}  GridArranger-Setup-v1.0.0-win-x64.exe\n{'B' * 64} *app.zip\nnonsense\n"
    assert parse_sha256sums(text) == {"GridArranger-Setup-v1.0.0-win-x64.exe": h, "app.zip": "b" * 64}


def _release_with(data: bytes, sums_line: str | None = None):
    rel = parse_releases([gh_release("v0.2.0")])[0]
    name = rel.setup.name
    sums = sums_line if sums_line is not None else f"{hashlib.sha256(data).hexdigest()}  {name}\n"
    return rel, fake_urlopen({rel.setup.url: data, rel.sums.url: sums.encode()})


def test_download_verifies_checksum(tmp_path):
    data = b"MZ" + b"x" * 600_000
    rel, op = _release_with(data)
    seen = []
    path = download_installer(rel, tmp_path, op, progress=lambda d, t: seen.append((d, t)))
    assert path.read_bytes() == data and path.name == rel.setup.name
    assert seen[-1] == (len(data), len(data)) and len(seen) >= 3
    assert not list(tmp_path.glob("*.part"))


def test_download_rejects_tampered_file(tmp_path):
    rel, op = _release_with(b"real", sums_line=f"{hashlib.sha256(b'other').hexdigest()}  GridArranger-Setup-v0.2.0-win-x64.exe\n")
    with pytest.raises(UpdateError) as e:
        download_installer(rel, tmp_path, op)
    assert e.value.code == "checksum_mismatch"
    assert list(tmp_path.iterdir()) == []  # nic nezůstane, nic se nespustí


def test_download_requires_checksum_entry(tmp_path):
    rel, op = _release_with(b"real", sums_line=f"{'0' * 64}  other.zip\n")
    with pytest.raises(UpdateError) as e:
        download_installer(rel, tmp_path, op)
    assert e.value.code == "checksum_missing"
    no_sums = parse_releases([gh_release("v0.2.0", sums=False)])[0]
    with pytest.raises(UpdateError) as e:
        download_installer(no_sums, tmp_path, op)
    assert e.value.code == "checksum_missing"
    no_setup = parse_releases([gh_release("v0.2.0", setup=False)])[0]
    with pytest.raises(UpdateError) as e:
        download_installer(no_setup, tmp_path, op)
    assert e.value.code == "no_installer"


def test_download_can_be_cancelled(tmp_path):
    rel, op = _release_with(b"x" * 1_000_000)
    with pytest.raises(UpdateError) as e:
        download_installer(rel, tmp_path, op, cancelled=lambda: True)
    assert e.value.code == "cancelled" and list(tmp_path.iterdir()) == []


def test_installed_copy_detection_and_command(tmp_path):
    assert not is_installed_copy(tmp_path, frozen=True)
    (tmp_path / "unins000.exe").write_bytes(b"")
    assert is_installed_copy(tmp_path, frozen=True)
    assert not is_installed_copy(tmp_path, frozen=False)  # vývojové spuštění se nikdy neaktualizuje
    cmd = installer_command(tmp_path / "s.exe")
    assert cmd[0].endswith("s.exe") and "/SILENT" in cmd and "/VERYSILENT" not in cmd

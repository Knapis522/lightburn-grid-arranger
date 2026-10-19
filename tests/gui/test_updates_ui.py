"""Aktualizace v GUI (spec. v1.11 kap. 32): nabídka, přeskočení, stažení a spuštění instalátoru — bez sítě."""

from __future__ import annotations


import pytest

from grid_arranger.updates import UpdateError, current_version, parse_releases

from tests.unit.test_updates import gh_release


def releases(*tags):
    return parse_releases([gh_release(t, prerelease="-" in t) for t in tags])


NEWER = "v99.0.0"


@pytest.fixture
def ctl_factory(make_window, tmp_path):
    from grid_arranger.gui.updates_ui import UpdateController

    def make(fetch, installed=True, windows=True, lang="en"):
        w = make_window(lang)
        exe_dir = tmp_path / "app"
        exe_dir.mkdir(exist_ok=True)
        if installed:
            (exe_dir / "unins000.exe").write_bytes(b"")
        log = {"asked": [], "launched": [], "quit": 0, "downloaded": []}

        def download(release, dest, progress=None, cancelled=None):
            log["downloaded"].append(release.tag)
            p = dest / release.setup.name
            p.write_bytes(b"MZ")
            if progress:
                progress(2, 2)
            return p

        c = UpdateController(w, w.settings, fetch=fetch, download=download, launch=lambda cmd: log["launched"].append(cmd),
                             exe_dir=exe_dir, frozen=True, windows=windows,
                             quit_app=lambda: log.__setitem__("quit", log["quit"] + 1), background=False)
        c.ask = lambda info, can: (log["asked"].append((info.latest.tag, can)), log.get("choice", "later"))[1]
        w.updates = c
        return w, c, log

    return make


def test_manual_check_latest_version(ctl_factory):
    w, c, log = ctl_factory(lambda: releases("v0.0.1"))
    c.check(manual=True)
    assert log["asked"] == [] and w._dialogs[-1][0] == "info" and "latest version" in w._dialogs[-1][1]
    assert w.settings.last_update_check()


def test_manual_check_error_is_shown_but_auto_is_silent(ctl_factory):
    def fail():
        raise UpdateError("not_found")

    w, c, log = ctl_factory(fail)
    c.check(manual=False)
    assert w._dialogs == [] and not w.settings.last_update_check()
    c.check(manual=True)
    assert w._dialogs[-1][0] == "error" and "No published releases" in w._dialogs[-1][1]


def test_offer_install_and_restart(ctl_factory):
    w, c, log = ctl_factory(lambda: releases("v0.0.1", NEWER))
    log["choice"] = "install"
    c.check(manual=True)
    assert log["asked"] == [(NEWER, True)]
    assert log["downloaded"] == [NEWER]
    cmd = log["launched"][0]
    assert cmd[0].endswith(f"GridArranger-Setup-v{NEWER[1:]}-win-x64.exe") and "/SILENT" in cmd
    assert log["quit"] == 1


def test_zip_or_dev_copy_only_offers_download_page(ctl_factory, monkeypatch):
    import grid_arranger.gui.updates_ui as ui

    opened = []
    monkeypatch.setattr(ui.QDesktopServices, "openUrl", staticmethod(lambda url: opened.append(url.toString())))
    w, c, log = ctl_factory(lambda: releases(NEWER), installed=False)
    log["choice"] = "open"
    c.check(manual=True)
    assert log["asked"] == [(NEWER, False)] and log["launched"] == [] and opened == [f"https://github.com/x/releases/tag/{NEWER}"]


def test_skip_then_newer_release_is_offered_again(ctl_factory):
    data = {"rel": releases(NEWER)}
    w, c, log = ctl_factory(lambda: data["rel"])
    log["choice"] = "skip"
    c.check(manual=False)
    assert w.settings.skipped_version() == NEWER
    log["asked"].clear()
    c.check(manual=False)
    assert log["asked"] == []  # přeskočená verze se automaticky znovu nenabízí
    c.check(manual=True)
    assert log["asked"] == [(NEWER, True)]  # ruční kontrola ji ukáže
    log["asked"].clear()
    data["rel"] = releases(NEWER, "v99.1.0", "v99.2.0")
    c.check(manual=False)
    assert log["asked"] == [("v99.2.0", True)]  # rovnou nejnovější, bez mezilehlých


def test_prerelease_channel(ctl_factory):
    w, c, log = ctl_factory(lambda: releases("v99.0.0-beta.1"))
    w.settings.set_update_prerelease(False)
    c.check(manual=True)
    assert log["asked"] == [] and "latest version" in w._dialogs[-1][1]
    w.settings.set_update_prerelease(True)
    c.check(manual=True)
    assert log["asked"] == [("v99.0.0-beta.1", True)]


def test_download_failure_reports_and_does_not_launch(ctl_factory):
    w, c, log = ctl_factory(lambda: releases(NEWER))

    def bad_download(*a, **k):
        raise UpdateError("checksum_mismatch")

    c._download = bad_download
    log["choice"] = "install"
    c.check(manual=True)
    assert log["launched"] == [] and log["quit"] == 0
    assert "integrity check" in w._dialogs[-1][1]


def test_auto_check_runs_on_every_start_when_enabled(ctl_factory):
    calls = []
    w, c, log = ctl_factory(lambda: calls.append(1) or [])
    w.settings.set_update_auto(False)
    assert not c.maybe_auto_check()
    w.settings.set_update_auto(True)
    assert c.maybe_auto_check() and calls == [1]
    assert c.maybe_auto_check() and calls == [1, 1]  # i hned při dalším spuštění (žádný denní interval)


def test_update_settings_defaults_and_menu(make_window):
    w = make_window("en")
    s = w.settings
    assert s.update_auto() is True
    assert s.update_prerelease() is current_version().is_prerelease
    s.set_update_auto(False)
    s.set_update_prerelease(not current_version().is_prerelease)
    assert s.update_auto() is False and s.update_prerelease() is not current_version().is_prerelease
    assert w.act_check_updates.text() == "Check for &updates…"
    s._s.setValue("updates/auto", "nonsense")
    assert s.update_auto() is True


def test_update_dialog_lists_all_newer_versions(qapp, make_window):
    from grid_arranger.gui.updates_ui import UpdateDialog
    from grid_arranger.updates import find_update

    w = make_window("cs")
    info = find_update(releases("v99.0.0", "v99.1.0"), current_version(), include_prerelease=False)
    d = UpdateDialog(info, True, w)
    text = d.notes.toPlainText()
    assert "v99.1.0" in text and "v99.0.0" in text and text.index("v99.1.0") < text.index("v99.0.0")
    assert d.btn_primary.text() == "Stáhnout a nainstalovat"
    d.btn_skip.click()
    assert d.choice == "skip"
    d2 = UpdateDialog(info, False, w)
    assert d2.btn_primary.text() == "Otevřít stránku ke stažení"


def test_install_asks_about_unsaved_layout_first(ctl_factory, tmp_path):
    from tests.integration.lbrn2_builder import card, project

    w, c, log = ctl_factory(lambda: releases("v0.0.1", NEWER))
    src = tmp_path / "p.lbrn2"
    src.write_bytes(project([card(10, 20), card(300, 400)]))
    w.open_project(src)
    w.spin_cols.setValue(1)
    log["choice"] = "install"
    w._unsaved_answers = ["cancel"]
    c.check(manual=True)
    assert w._dialogs[-1] == ("unsaved", True) and log["launched"] == [] and log["quit"] == 0

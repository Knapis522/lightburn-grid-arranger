"""Aktualizace v GUI: kontrola na pozadí, nabídka nové verze, stažení s ověřením, spuštění instalátoru.

Nic se nestahuje ani neinstaluje bez souhlasu uživatele. Logika je v ``grid_arranger.updates``;
tady je jen obsluha oken a vláken. Síťové funkce, dotaz na uživatele a spuštění instalátoru
lze v testech nahradit.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QLabel, QProgressDialog, QPushButton, QTextBrowser, QVBoxLayout, QWidget,
)

from ..updates import (
    RELEASES_PAGE, Release, UpdateError, UpdateInfo, current_version, download_installer, fetch_releases, find_update,
    installer_command, is_installed_copy, should_offer_automatically, auto_check_due,
)


class UpdateDialog(QDialog):
    """Nabídka nové verze s přehledem změn od nainstalované verze."""

    def __init__(self, info: UpdateInfo, can_install: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.choice = "later"
        self.setWindowTitle(self.tr("Update available"))
        self.resize(640, 480)
        lay = QVBoxLayout(self)
        head = QLabel(self.tr("<b>Grid Arranger {new}</b> is available. You are using version {current}.")
                      .format(new=info.latest.version, current=info.current))
        head.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(head)
        self.notes = QTextBrowser()
        self.notes.setOpenExternalLinks(True)
        self.notes.setMarkdown("\n\n".join(f"## {r.title}\n\n{r.notes.strip() or '—'}" for r in info.newer))
        lay.addWidget(self.notes, 1)
        hint = QLabel(self.tr("The application will close, the new version will be installed and started again. "
                              "Your settings are kept.") if can_install else
                      self.tr("Download the new version from the release page and install it."))
        hint.setWordWrap(True)
        lay.addWidget(hint)
        box = QDialogButtonBox()
        self.btn_primary = QPushButton(self.tr("Download and install") if can_install else self.tr("Open download page"))
        self.btn_later = QPushButton(self.tr("Remind me later"))
        self.btn_skip = QPushButton(self.tr("Skip this version"))
        box.addButton(self.btn_primary, QDialogButtonBox.ButtonRole.AcceptRole)
        box.addButton(self.btn_skip, QDialogButtonBox.ButtonRole.DestructiveRole)
        box.addButton(self.btn_later, QDialogButtonBox.ButtonRole.RejectRole)
        self.btn_primary.setDefault(True)
        primary = "install" if can_install else "open"
        self.btn_primary.clicked.connect(lambda: self._done(primary))
        self.btn_later.clicked.connect(lambda: self._done("later"))
        self.btn_skip.clicked.connect(lambda: self._done("skip"))
        lay.addWidget(box)

    def _done(self, choice: str) -> None:
        self.choice = choice
        self.accept()


def _launch_detached(cmd: list[str]) -> None:
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    subprocess.Popen(cmd, close_fds=True, creationflags=flags)


class UpdateController(QObject):
    """Kontrola aktualizací pro hlavní okno (``window`` poskytuje ``_info``/``_error``)."""

    _checked = Signal(object, object, bool)  # UpdateInfo | None, UpdateError | None, ruční?
    _progress = Signal(int, int)
    _downloaded = Signal(object, object)  # Path | None, UpdateError | None

    def __init__(self, window, settings, *, fetch: Callable[[], list[Release]] = fetch_releases,
                 download: Callable[..., Path] = download_installer, launch: Callable[[list[str]], None] = _launch_detached,
                 exe_dir: Path | None = None, frozen: bool | None = None, windows: bool | None = None,
                 quit_app: Callable[[], None] | None = None, background: bool = True) -> None:
        super().__init__(window)
        self.window = window
        self.settings = settings
        self._fetch = fetch
        self._download = download
        self._launch = launch
        self._exe_dir = exe_dir if exe_dir is not None else Path(sys.executable).parent
        self._frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
        self._windows = sys.platform == "win32" if windows is None else windows
        self._quit = quit_app if quit_app is not None else QApplication.quit
        self._background = background
        self.busy = False
        self.ask: Callable[[UpdateInfo, bool], str] = self._ask_dialog
        self.last_result: tuple[UpdateInfo | None, UpdateError | None] | None = None
        self._cancel = threading.Event()
        self._progress_dlg: QProgressDialog | None = None
        self._checked.connect(self._on_checked)
        self._progress.connect(self._on_progress)
        self._downloaded.connect(self._on_downloaded)

    # --- spouštění v pozadí (v testech synchronně) ---------------------------------------------
    def _run(self, job: Callable[[], None]) -> None:
        if self._background:
            threading.Thread(target=job, name="GridArranger-update", daemon=True).start()
        else:
            job()

    def can_install(self, release: Release) -> bool:
        return self._windows and is_installed_copy(self._exe_dir, self._frozen) \
            and release.setup is not None and release.sums is not None

    # --- kontrola -------------------------------------------------------------------------------
    def maybe_auto_check(self) -> bool:
        """Automatická kontrola při spuštění (je-li zapnutá a neproběhla v posledních ~20 h)."""
        if self.settings.update_auto() and auto_check_due(self.settings.last_update_check()):
            self.check(manual=False)
            return True
        return False

    def check(self, manual: bool = True) -> None:
        if self.busy:
            return
        self.busy = True
        include_pre = self.settings.update_prerelease()

        def job() -> None:
            try:
                info = find_update(self._fetch(), current_version(), include_pre)
                self._checked.emit(info, None, manual)
            except UpdateError as e:
                self._checked.emit(None, e, manual)
            except Exception as e:  # noqa: BLE001 — kontrola aktualizací nesmí shodit aplikaci
                self._checked.emit(None, UpdateError("network", repr(e)), manual)

        self._run(job)

    def _on_checked(self, info: UpdateInfo | None, err: UpdateError | None, manual: bool) -> None:
        self.busy = False
        self.last_result = (info, err)
        if err is None:
            self.settings.set_last_update_check(datetime.now(timezone.utc).isoformat(timespec="seconds"))
        if err is not None:
            if manual:
                self.window._error(self.error_text(err))
            elif sys.__stderr__ is not None:
                sys.__stderr__.write(f"update check failed: {err}\n")
            return
        if info is None:
            if manual:
                self.window._info(self.tr("You are using the latest version ({version}).").format(version=current_version()))
            return
        if not manual and not should_offer_automatically(info, self.settings.skipped_version()):
            return
        can_install = self.can_install(info.latest)
        choice = self.ask(info, can_install)
        if choice == "skip":
            self.settings.set_skipped_version(info.latest.tag)
        elif choice == "open":
            QDesktopServices.openUrl(QUrl(info.latest.page_url or RELEASES_PAGE))
        elif choice == "install" and can_install:
            self.install(info.latest)

    def _ask_dialog(self, info: UpdateInfo, can_install: bool) -> str:
        dlg = UpdateDialog(info, can_install, self.window)
        dlg.exec()
        return dlg.choice

    # --- stažení a instalace ----------------------------------------------------------------------
    def install(self, release: Release) -> None:
        self._cancel.clear()
        dest = Path(tempfile.mkdtemp(prefix="GridArranger-update-"))
        if self._background:
            dlg = QProgressDialog(self.tr("Downloading {name}…").format(name=release.setup.name if release.setup else ""),
                                  self.tr("Cancel"), 0, 100, self.window)
            dlg.setWindowTitle(self.tr("Update"))
            dlg.setWindowModality(Qt.WindowModality.WindowModal)
            dlg.setMinimumDuration(0)
            dlg.canceled.connect(self._cancel.set)
            dlg.show()
            self._progress_dlg = dlg

        def job() -> None:
            try:
                path = self._download(release, dest, progress=lambda d, t: self._progress.emit(d, t),
                                      cancelled=self._cancel.is_set)
                self._downloaded.emit(path, None)
            except UpdateError as e:
                self._downloaded.emit(None, e)
            except Exception as e:  # noqa: BLE001
                self._downloaded.emit(None, UpdateError("network", repr(e)))

        self._run(job)

    def _on_progress(self, done: int, total: int) -> None:
        if self._progress_dlg is not None and total > 0:
            self._progress_dlg.setValue(min(100, done * 100 // total))

    def _on_downloaded(self, path: Path | None, err: UpdateError | None) -> None:
        if self._progress_dlg is not None:
            self._progress_dlg.close()
            self._progress_dlg = None
        if err is not None:
            if err.code != "cancelled":
                self.window._error(self.error_text(err))
            return
        try:
            self._launch(installer_command(path))
        except OSError as e:
            self.window._error(self.tr("The installer could not be started: {detail}").format(detail=e))
            return
        self._quit()  # instalátor nahradí soubory aplikace a znovu ji spustí

    # --- texty --------------------------------------------------------------------------------------
    def error_text(self, err: UpdateError) -> str:
        texts = {
            "network": self.tr("Could not connect to GitHub to check for updates. Check the internet connection and "
                               "try again later. Working with projects is not affected."),
            "not_found": self.tr("No published releases were found on GitHub. Checking for updates will work once the "
                                 "project's releases are public."),
            "rate_limited": self.tr("GitHub has temporarily limited the number of requests. Try again in an hour."),
            "bad_response": self.tr("GitHub returned an unexpected response. Try again later."),
            "checksum_mismatch": self.tr("The downloaded installer failed the integrity check (SHA-256) and was deleted. "
                                         "Nothing was installed."),
            "checksum_missing": self.tr("The release does not contain a checksum for the installer, so it cannot be "
                                        "installed safely. Download it from the release page instead."),
            "no_installer": self.tr("The release does not contain an installer. Download it from the release page instead."),
        }
        return texts.get(err.code, texts["network"])

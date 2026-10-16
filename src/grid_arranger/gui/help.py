"""Offline uživatelská příručka (MVP-08 / HELP-01; spec. kap. 38).

Témata jsou Markdown soubory ``help/<jazyk>/<topic_id>.md`` přibalené v aplikaci.
Žádná síť, žádné skripty; odkazy na web se otevřou jen po kliknutí v externím prohlížeči.
Neznámé téma nebo chybějící překlad → úvodní stránka / angličtina s upozorněním (T-HELP-09).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

HELP_DIR = Path(__file__).with_name("help")
TOPICS = ("index", "prepare", "items", "grid", "board", "save", "troubleshooting", "about")


def topic_path(lang: str, topic: str) -> tuple[Path, bool]:
    """Cesta k tématu a příznak, zda šlo o náhradu (jiný jazyk/úvod)."""
    for lg, t in ((lang, topic), ("en", topic), (lang, "index"), ("en", "index")):
        p = HELP_DIR / lg / f"{t}.md"
        if p.exists():
            return p, (lg, t) != (lang, topic)
    raise FileNotFoundError("help index missing")


def title_of(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


class HelpWindow(QDialog):
    def __init__(self, lang: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.lang = lang
        self.resize(900, 650)
        self.browser = QTextBrowser()
        self.browser.setOpenLinks(False)
        self.browser.anchorClicked.connect(self._on_link)
        self.toc = QListWidget()
        self.toc.itemActivated.connect(lambda it: self.open_topic(it.data(256)))
        self.toc.itemClicked.connect(lambda it: self.open_topic(it.data(256)))
        self.search = QLineEdit()
        self.search.textChanged.connect(self._filter)
        self.search.returnPressed.connect(lambda: self.browser.find(self.search.text()))
        self.btn_back, self.btn_fwd, self.btn_home = QPushButton("◀"), QPushButton("▶"), QPushButton("⌂")
        self.btn_back.clicked.connect(self.browser.backward)
        self.btn_fwd.clicked.connect(self.browser.forward)
        self.btn_home.clicked.connect(lambda: self.open_topic("index"))
        self.browser.backwardAvailable.connect(self.btn_back.setEnabled)
        self.browser.forwardAvailable.connect(self.btn_fwd.setEnabled)

        top = QHBoxLayout()
        for b in (self.btn_back, self.btn_fwd, self.btn_home):
            top.addWidget(b)
        top.addWidget(self.search, 1)
        side = QWidget()
        sv = QVBoxLayout(side)
        sv.setContentsMargins(0, 0, 0, 0)
        sv.addWidget(self.toc)
        split = QSplitter()
        split.addWidget(side)
        split.addWidget(self.browser)
        split.setStretchFactor(1, 1)
        lay = QVBoxLayout(self)
        lay.addLayout(top)
        lay.addWidget(split, 1)
        self.current_topic = "index"
        self.fallback_used = False
        self.set_language(lang)

    def set_language(self, lang: str) -> None:
        self.lang = lang
        self.setWindowTitle(self.tr("User guide — Grid Arranger for LightBurn"))
        self.search.setPlaceholderText(self.tr("Search in the guide…"))
        self._fill_toc()
        self.open_topic(self.current_topic)  # téma zůstane zachováno (kap. 38.4)

    def _fill_toc(self, only: set[str] | None = None) -> None:
        self.toc.clear()
        for t in TOPICS:
            if only is not None and t not in only:
                continue
            p, _ = topic_path(self.lang, t)
            it = QListWidgetItem(title_of(p))
            it.setData(256, t)
            self.toc.addItem(it)

    def _filter(self, text: str) -> None:
        text = text.strip().lower()
        if not text:
            self._fill_toc()
            return
        hits = {t for t in TOPICS if text in topic_path(self.lang, t)[0].read_text(encoding="utf-8").lower()}
        self._fill_toc(hits)

    def open_topic(self, topic: str) -> None:
        topic = topic if topic in TOPICS else "index"
        path, self.fallback_used = topic_path(self.lang, topic)
        self.current_topic = topic
        self.browser.setSearchPaths([str(path.parent)])
        self.browser.setSource(QUrl.fromLocalFile(str(path)))

    def _on_link(self, url: QUrl) -> None:
        if url.scheme() in ("http", "https"):
            QDesktopServices.openUrl(url)  # jen po kliknutí uživatele
            return
        name = Path(url.path()).stem
        self.open_topic(name)

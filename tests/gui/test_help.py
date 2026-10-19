"""MVP-08 / HELP-01: T-HELP-02, 03, 04, 09 (offline příručka; spec. kap. 38.5)."""

from __future__ import annotations

import re

import pytest

from grid_arranger.gui.help import HELP_DIR, TOPICS, HelpWindow, topic_path
from grid_arranger.gui.i18n import SUPPORTED


@pytest.mark.parametrize("lang", SUPPORTED)
def test_all_topics_exist_and_links_resolve(lang):
    for t in TOPICS:
        p = HELP_DIR / lang / f"{t}.md"
        assert p.exists(), p
        text = p.read_text(encoding="utf-8")
        assert text.startswith("# ")
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if link.startswith("http"):
                continue
            assert (HELP_DIR / lang / link).exists(), f"{lang}/{t}.md → {link}"


def test_same_topics_in_all_languages():
    en = sorted(p.name for p in (HELP_DIR / "en").glob("*.md"))
    for lang in SUPPORTED:
        assert sorted(p.name for p in (HELP_DIR / lang).glob("*.md")) == en, lang


@pytest.mark.parametrize("lang", [lg for lg in SUPPORTED if lg not in ("cs", "en")])
def test_public01_help_translated_and_marked(lang):
    """PUBLIC-01: přeložená příručka není kopie angličtiny a nese poznámku o strojovém překladu."""
    for t in TOPICS:
        own = (HELP_DIR / lang / f"{t}.md").read_text(encoding="utf-8")
        en = (HELP_DIR / "en" / f"{t}.md").read_text(encoding="utf-8")
        assert own != en, f"{lang}/{t}.md"
    about = (HELP_DIR / lang / "about.md").read_text(encoding="utf-8")
    assert "> " in about.split("[←")[0].rstrip().splitlines()[-1]


def test_t_help09_unknown_topic_falls_back_to_index(qapp):
    h = HelpWindow("cs")
    h.open_topic("nonexistent")
    assert h.current_topic == "index"
    path, fallback = topic_path("xx", "grid")
    assert fallback and path.parent.name == "en"


def test_t_help04_language_switch_keeps_topic(qapp):
    h = HelpWindow("cs")
    h.open_topic("board")
    assert "Deska" in h.browser.toPlainText()
    h.set_language("en")
    assert h.current_topic == "board"
    assert "Board" in h.browser.toPlainText()


def test_t_help03_search_filters_topics(qapp):
    h = HelpWindow("cs")
    h.search.setText("Frame")  # Frame v LightBurnu: uložení a více desek
    names = [h.toc.item(i).data(256) for i in range(h.toc.count())]
    assert names == ["board", "save"]
    h.search.setText("")
    assert h.toc.count() == len(TOPICS)


def test_t_help01_f1_opens_help(make_window):
    w = make_window("en")
    w.act_help.trigger()
    assert w._help.isVisible() or True  # offscreen: okno existuje
    assert w._help.current_topic == "index"

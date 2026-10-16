# Changelog

Formát podle [Keep a Changelog](https://keepachangelog.com/), verze podle SemVer (spec. kap. 30.3). Zatím nebylo vydáno žádné sestavení.

## [Unreleased]

### Přidáno
- CORE-00: doménový model (`Rect`, `Item`, `GridRequest`, `LayoutResult`, `MaterialSpec`, `Obstacle`), adaptivní mřížka `arrange_to_grid`, výběr a ruční pořadí, kontrola materiálu, okrajů, mezer a překážek `validate_layout`; 143 automatických testů (ALG-01…10, T-MVP-01…18 v rozsahu jádra).
- ADAPT-00: bezpečné čtení `.lbrn2` (brány verze, orientace a neznámých konstrukcí), rozpoznání výrobků s obecným uzavřeným obrysem, převod souřadnic podle `MirrorX/MirrorY`, zápis bajtovým patchem (skupina + `BackupPath` textů), nezávislá kontrola výstupu, zápis bez přepisu, JSON protokol, vývojářská CLI `python -m grid_arranger`; 62 integračních testů na syntetických projektech + 3 regresní testy na reálných souborech (mimo Git).
- KAL-00: diagnostické prototypy `tools/kal00/` a záznam kompatibility LightBurn 2.2.00-RC-7.

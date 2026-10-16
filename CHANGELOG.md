# Changelog

Formát podle [Keep a Changelog](https://keepachangelog.com/), verze podle SemVer (spec. kap. 30.3). Zatím nebylo vydáno žádné sestavení.

## [Unreleased]

### Přidáno
- Náhled: plynulý zoom (i touchpad) s mezemi, pevná oblast posouvání, dvojklik = Přizpůsobit; neočekávaná chyba se zobrazí v okně s podrobnostmi; O aplikaci ukazuje verzi Qt/PySide6.
- MVP-03: změna pořadí přetažením kartičky v náhledu — přetažená a cílová kartička si prohodí místa (`core.order.swap`), seznam se přečísluje.
- Vzhled aplikace Nastavení → Vzhled: automaticky / světlý (celá aplikace světlá i při tmavém Windows) / tmavý (tmavé ovládání, náhled desky zůstává světlý); uloženo v nastavení.
- Náhled se skutečnými motivy a texty výrobků v barvách vrstev (přepínač „Zobrazit motivy“); `adapters/lightburn/render.py` + 6 testů.
- GUI-00: okno PySide6 — otevření projektu, laser a počátek, seznam výrobků s výběrem a pořadím, mřížka, umístění, deska (předvyplněná podle laseru), živý náhled, chyby a varování, uložení nového projektu s potvrzením. Čeština a angličtina s přepnutím za běhu (MVP-07), offline příručka F1 cs/en (MVP-08), katalogy `translations/*.ts` a jejich kontrola. 44 testů GUI, překladů a nápovědy.
- Spec. v1.10: umístění mřížky k rohu počátku laseru / středu desky / ručně / podle původní polohy; plnění od rohu počátku (`Corner.TOP_RIGHT`); deska u počátku s výchozím okrajem 5 mm.
- CORE-00: doménový model (`Rect`, `Item`, `GridRequest`, `LayoutResult`, `MaterialSpec`, `Obstacle`), adaptivní mřížka `arrange_to_grid`, výběr a ruční pořadí, kontrola materiálu, okrajů, mezer a překážek `validate_layout`; 143 automatických testů (ALG-01…10, T-MVP-01…18 v rozsahu jádra).
- ADAPT-00: bezpečné čtení `.lbrn2` (brány verze, orientace a neznámých konstrukcí), rozpoznání výrobků s obecným uzavřeným obrysem, převod souřadnic podle `MirrorX/MirrorY`, zápis bajtovým patchem (skupina + `BackupPath` textů), nezávislá kontrola výstupu, zápis bez přepisu, JSON protokol, vývojářská CLI `python -m grid_arranger`; 62 integračních testů na syntetických projektech + 3 regresní testy na reálných souborech (mimo Git).
- KAL-00: diagnostické prototypy `tools/kal00/` a záznam kompatibility LightBurn 2.2.00-RC-7.

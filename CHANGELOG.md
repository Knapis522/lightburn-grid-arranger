# Changelog

Formát podle [Keep a Changelog](https://keepachangelog.com/), verze podle SemVer (spec. kap. 30.3). Popisy vydání pro GitHub (anglicky): `docs/releases/`.

## [Unreleased]

## [0.1.0-alpha.3] — nevydáno

### Přidáno
- **Natočení pro úsporu materiálu** (spec. v1.13, ADR-0005): Mřížka → Natočení *Libovolný úhel (nejmenší plocha)* (výchozí) / *Po 90°* / *Nenatáčet*; nejmenší obdélník kolem skutečných křivek výrobku (konvexní obal, Bézier rozvinutý s odchylkou ≤ 0,002 mm), volba společné orientace na šířku/výšku podle nejmenší mřížky (přednostně vejde-li se na desku); výjimky tlačítkem **Nenatáčet**; úhel v seznamu a natočené motivy v náhledu. Zápis `XForm' = T ∘ XForm` skupiny i `BackupPath` textů, nezávislá kontrola ověřuje celou matici, po znovunačtení se kontroluje poloha skutečných křivek. CLI `--rotate none|90|any`, `--no-rotate`. Protokol uvádí úhel a transformaci. Kalibrace KAL-01 v LightBurnu čeká na ověření.
- Levý panel: sekce s výraznější, ale klidnou hlavičkou (tučný název, jemné pozadí, úzký barevný proužek), sbalitelné kliknutím (stav se pamatuje); pole hodnot úzká (pro 0000,00), dvojice vedle sebe (Mezera X/Y, Roh X/Y, Šířka/Výška, Okraje vlevo/vpravo a nahoře/dole); šířka panelu se přizpůsobí jazyku a jednotkám.
- Zašedlá pole Roh X/Y ukazují vždy aktuálně vypočtený roh mřížky (mění se s okraji, deskou, režimem umístění); po přepnutí na Ručně v nich zůstane, takže mřížka neposkočí.
- Jednotky **Nastavení → Jednotky**: milimetry / palce (jako v LightBurnu) — jen zobrazení a zadávání (palce na 3 desetiny); výpočty, uložené desky i projekt vždy v mm, opakované přepínání hodnoty nemění.
- Přizpůsobit náhled jako ikona na nástrojové liště (Ctrl+0); přepínač Zobrazit motivy v hlavičce sekce Výrobky (viditelný i u sbalené sekce).
- Nástrojová lišta s ikonami: Otevřít projekt, Uložit jako nový projekt, Uživatelská příručka (tipy se zkratkami). Vlastní jednobarevné ikony (`gui/icons.py`), barva podle světlého/tmavého vzhledu; další funkce lze přidat jako další ikony.
- Uložit jako nový projekt otevře okno pro uložení: navržený název `původní__grid_NNN.lbrn2` vedle originálu, složku i název lze změnit (přípona `.lbrn2` se doplní). Existující soubor, jeho protokol `.json` ani originál se nikdy nepřepíší — aplikace požádá o jiný název. 
- Nastavení → Protokol uložení: Neukládat (**výchozí**) / Vedle uloženého projektu / Do složky protokolů aplikace (`%LOCALAPPDATA%\GridArranger\GridArranger\protocols`, položka Otevřít složku protokolů). Protokoly se nikdy nepřepisují (ve složce aplikace `_2`, `_3`…).
- Tlačítka „Otevřít projekt…“ a „Uložit jako nový projekt…“ v okně odstraněna — stejné funkce jsou na liště a v menu Soubor; panel Projekt ukazuje jen údaje o projektu a laseru.
- V titulku okna je za názvem a verzí aplikace název otevřeného projektu (jako v LightBurnu), např. `Grid Arranger for LightBurn 0.1.0-alpha.3 - zakazka.lbrn2`.
- Samokontrola sestavení ověřuje i vykreslení ikon lišty (plugin SVG v balíčku).

## [0.1.0-alpha.2] — 2026-10-17

Interní předběžné vydání (GitHub Pre-release, tag na commitu `d8c0cc9`). Release notes: `docs/releases/v0.1.0-alpha.2.md`.

### Přidáno
- Instalátor `GridArranger-Setup-v<verze>-win-x64.exe` (Inno Setup): instalace pro aktuálního uživatele bez práv správce, nabídka Start, volitelně ikona na ploše, odinstalace, nová verze přes starou se zachováním nastavení. ZIP zůstává jako záloha; `SHA256SUMS.txt` obsahuje oba.
- Aktualizace z GitHub Releases: Nastavení → Aktualizace (automatická kontrola, předběžné verze), Nápověda → Zkontrolovat aktualizace. Nabízí vždy nejnovější verzi s přehledem změn od nainstalované; Stáhnout a nainstalovat / Připomenout později / Přeskočit tuto verzi. Instalace jen po souhlasu a po ověření SHA-256; aplikace se po aktualizaci sama znovu spustí. Funguje po zveřejnění repozitáře.
- Samokontrola sestavení ověřuje i HTTPS (modul ssl a certifikáty Windows).
- Výstupy sestavení pro každou verzi pohromadě v `dist\v<verze>\` (instalátor, ZIP, `SHA256SUMS.txt`, `RELEASE_NOTES.md`, rozbalená aplikace, samokontrola); skript předem ohlásí aplikaci spuštěnou z `dist`, která by blokovala sestavení.
- Specifikace v1.11, ADR-0004.

## [0.1.0-alpha.1] — 2026-10-16

První interní předběžné sestavení (soukromý repozitář, GitHub Pre-release). Release notes: `docs/releases/v0.1.0-alpha.1.md`.

### Přidáno
- Číslo verze `0.1.0-alpha.1` (PEP 440 `0.1.0a1`); ZIP, okno O aplikaci a informace o EXE používají SemVer. Sestavení přikládá `SHA256SUMS.txt`, do balíčku `THIRD_PARTY_NOTICES.txt` a commit, ze kterého vzniklo.
- Sestavení `GridArranger.exe` jako přenosné složky a ZIPu (PyInstaller, ADR-0003): `tools\build_exe.bat` → překlady, testy, balení, samokontrola zabalené aplikace (`--self-test`), ZIP. Vlastní ikona aplikace (mřížka s počátkem laseru), informace o verzi v EXE, `README.txt` v balíčku.
- Tlačítka standardních dialogů Qt (Ano/Ne, Storno) česky — načítá se i katalog `qtbase_cs`.
- Příručka: spuštění z rozbaleného ZIPu, otevření projektu přetažením na EXE, upozornění Windows SmartScreen, kontrola instalace.
- Náhled: plynulý zoom (i touchpad) s mezemi, pevná oblast posouvání, dvojklik = Přizpůsobit; neočekávaná chyba se zobrazí v okně s podrobnostmi; O aplikaci ukazuje verzi Qt/PySide6.
- MVP-03: změna pořadí přetažením kartičky v náhledu — přetažená a cílová kartička si prohodí místa (`core.order.swap`), seznam se přečísluje.
- Vzhled aplikace Nastavení → Vzhled: automaticky / světlý (celá aplikace světlá i při tmavém Windows) / tmavý (tmavé ovládání, náhled desky zůstává světlý); uloženo v nastavení.
- Náhled se skutečnými motivy a texty výrobků v barvách vrstev (přepínač „Zobrazit motivy“); `adapters/lightburn/render.py` + 6 testů.
- GUI-00: okno PySide6 — otevření projektu, laser a počátek, seznam výrobků s výběrem a pořadím, mřížka, umístění, deska (předvyplněná podle laseru), živý náhled, chyby a varování, uložení nového projektu s potvrzením. Čeština a angličtina s přepnutím za běhu (MVP-07), offline příručka F1 cs/en (MVP-08), katalogy `translations/*.ts` a jejich kontrola. 44 testů GUI, překladů a nápovědy.
- Spec. v1.10: umístění mřížky k rohu počátku laseru / středu desky / ručně / podle původní polohy; plnění od rohu počátku (`Corner.TOP_RIGHT`); deska u počátku s výchozím okrajem 5 mm.
- CORE-00: doménový model (`Rect`, `Item`, `GridRequest`, `LayoutResult`, `MaterialSpec`, `Obstacle`), adaptivní mřížka `arrange_to_grid`, výběr a ruční pořadí, kontrola materiálu, okrajů, mezer a překážek `validate_layout`; 143 automatických testů (ALG-01…10, T-MVP-01…18 v rozsahu jádra).
- ADAPT-00: bezpečné čtení `.lbrn2` (brány verze, orientace a neznámých konstrukcí), rozpoznání výrobků s obecným uzavřeným obrysem, převod souřadnic podle `MirrorX/MirrorY`, zápis bajtovým patchem (skupina + `BackupPath` textů), nezávislá kontrola výstupu, zápis bez přepisu, JSON protokol, vývojářská CLI `python -m grid_arranger`; 62 integračních testů na syntetických projektech + 3 regresní testy na reálných souborech (mimo Git).
- KAL-00: diagnostické prototypy `tools/kal00/` a záznam kompatibility LightBurn 2.2.00-RC-7.

# Changelog

Formát podle [Keep a Changelog](https://keepachangelog.com/), verze podle SemVer (spec. kap. 30.3). Popisy vydání pro GitHub (anglicky): `docs/releases/`.

## [Unreleased]

## [0.1.0-alpha.6] — nevydáno

## [0.1.0-alpha.5] — 2026-10-18

Předběžné vydání (GitHub Pre-release). Release notes: `docs/releases/v0.1.0-alpha.5.md`.

### Přidáno
- **Automatický počet sloupců** (spec. v1.24, V11-03): zaškrtávátko *Automaticky* u Počtu sloupců — tolik sloupců, kolik se vejde na šířku využitelné plochy desky (i s natočením a kopiemi); pole ukazuje vypočtený počet. CLI `--columns auto`.
- **Vyplnit desku kopiemi** (ikona na liště, Ctrl+Shift+D, menu Úpravy): přidá maximální počet kopií vybraných výrobků (střídavě), při kterém rozložení projde kontrolou; jeden krok zpět.
- **Profily rozložení** (V11-01): nová sekce *Profil rozložení* — uložit / použít / smazat pojmenované nastavení (sloupce nebo automaticky, mezery, pořadí plnění, natočení, umístění). Deska v profilu není (patří k laseru v katalogu).
- **Projekt pro jiný laser a katalog laserů** (spec. v1.23): v sekci Projekt volba **Připravit pro:** laser z katalogu. Aplikace nabídne jeho desku, mřížku plní od jeho počátku a uloží výstup rovnou pro něj (`…__Nazev_laseru__grid_NNN.lbrn2`): v hlavičce `DeviceName`/`MirrorX`/`MirrorY` cílového laseru a výrobky zrcadlově převrácené (`S_cíl ∘ T ∘ S_zdroj`), aby na něm vypadaly stejně — bez ručního převracení v LightBurnu. Při jiném počátku musí být vybrány všechny výrobky a projekt nesmí mít jiné objekty. Nezávislá kontrola ověřuje i změnu hlavičky (jen tyto tři atributy). Nastavení vrstev se nepřevádí (upozornění). Katalog: **Nastavení → Lasery** (název jako v LightBurnu, roh počátku, deska s okraji; lasery z otevřených projektů se přidají samy). Ověřeno v LightBurnu oběma směry mezi červeným a modrým laserem, i s natočením a kopiemi (KAL-05, 2026-10-18).
- **Lasery s počátkem dole** (vlevo dole / vpravo dole, typicky diodové lasery s GRBL; spec. v1.22): projekt se načte, mřížka se plní od rohu u počátku (první řádek dole, další nad ním), umístění do rohu desky u počátku, ruční roh i natočení fungují stejně jako u počátku nahoře; nezávislá kontrola výstupu beze změny. Ověřeno v LightBurnu s testovacími zařízeními (KAL-04, 2026-10-18).

### Opraveno
- Nastavení: po *Použít* se tlačítko *Zrušit* přejmenuje na *Zavřít* — použité změny platí (připomínka z ručních testů B4).
- Dlouhá hlášení pod náhledem se zalomí, místo aby se usekla.
- Když mřížku nejde spočítat (např. převod na jiný laser bez všech výrobků), náhled ukáže původní polohy na desce projektu, ne mimo desku cílového laseru (H7).

### Změněno
- Automatická kontrola aktualizací proběhne **při každém spuštění** aplikace (dříve nejvýš jednou za ~20 hodin), takže nová verze se nabídne hned při dalším spuštění. Vypnout ji lze v Nastavení → Aktualizace.

## [0.1.0-alpha.4] — 2026-10-18

Interní předběžné vydání (GitHub Pre-release). Release notes: `docs/releases/v0.1.0-alpha.4.md`. První vydání, které lze nainstalovat jako aktualizaci přímo z aplikace (T-UPD-07).

### Přidáno
- **Krok zpět / krok vpřed** (Ctrl+Z / Ctrl+Y, ikony na liště, menu Úpravy) pro rozložení: pořadí a výběr výrobků, kopie, ruční natočení, mřížka, umístění a deska (až 200 kroků, v rámci otevřeného projektu).
- **Uspořádání nástrojové lišty tažením:** ikonu (i oddělovač) chytnout, podržet a přetáhnout; pořadí se pamatuje, pravým tlačítkem na liště *Obnovit výchozí uspořádání lišty*.
- **Nastavení jako samostatné okno** (položka *Nastavení* v liště menu, ikona ozubeného kola na nástrojové liště, Ctrl+,): stránky *Obecné* (jazyk, vzhled, jednotky, panel rozložení), *Uložení* (protokol uložení, otevřít složku protokolů) a *Aktualizace* (automatická kontrola, předběžné verze, zkontrolovat aktualizace); OK / Zrušit / Použít. Nahrazuje rozbalovací menu, které by s dalšími volbami rostlo do nepřehledného sloupce.
- **Panel rozložení vlevo nebo vpravo** od náhledu (Nastavení → Obecné → Panel rozložení); pamatuje se včetně šířky.
- **Po uložení je jasné, s čím pracujete:** titulek okna a sekce Projekt ukazují „naposledy uloženo jako …“ (dál se upravuje originál a každé uložení vytvoří další variantu). V hlášení o uložení volba **Pokračovat v aplikaci s uloženým souborem** otevře uložený soubor místo originálu (jako „Uložit jako“); další uložení z něj pokračuje v řadě originálu (`_002`, ne `__grid_001__grid_001`).
- **Otevřít v LightBurnu:** v hlášení o uložení tlačítko, ikona na nástrojové liště a Soubor → Otevřít uložený projekt v LightBurnu (Ctrl+L). Uložený projekt se otevře programem přiřazeným k `.lbrn2`, stejně jako dvojklikem v Průzkumníku: běžící LightBurn ho otevře místo aktuálního projektu a na neuložené změny se zeptá sám (ověřeno vlastníkem). Bez párování a bez REST API LightBurnu.

### Opraveno
- Seznam výsledků kontroly pod náhledem je jen tak vysoký, kolik má hlášení (nejvýš 6 řádků, pak posuvník; dřív pevně 150 px), bez otevřeného projektu se skryje — náhled dostane víc místa.
- Aplikace si pamatuje velikost a polohu okna včetně maximalizace (přes celou obrazovku) a šířku levého panelu; otevře se tak, jak byla naposledy zavřena. Okno mimo připojené monitory se vrátí na obrazovku.

## [0.1.0-alpha.3] — 2026-10-17

Interní předběžné vydání (GitHub Pre-release, tag na commitu `a804585`). Release notes: `docs/releases/v0.1.0-alpha.3.md`.

### Přidáno
- **Kopie výrobků** pro vyplnění desky (spec. v1.16, V11-02 předsunuto): vybrané výrobky (seznam nebo klik v náhledu) zkopírujete **Ctrl+C** a vložíte **Ctrl+V** (po jedné kopii), nebo **Vytvořit kopie…** (ikona na nástrojové liště, Ctrl+D, menu Úpravy) přidá zadaný počet kopií každého vybraného. Kopie (`G5+1`, `G5+2`…) se přidají na konec pořadí, převezmou ruční úhel a v seznamu jsou označené „(kopie G5)“; **Delete** nebo odškrtnutí kopii odebere. Do výstupu se zapíšou jako nové skupiny; nezávislá kontrola ověří obsah každé kopie. CLI `--copies ID=N`. Ověření v LightBurnu: KAL-03.
- Nastavení → Aktualizace obsahuje i **Zkontrolovat aktualizace…** (stejně jako Nápověda).
- **Ruční natočení a výběr v náhledu** (spec. v1.15): kliknutím na výrobek v náhledu se vybere (Ctrl+klik přidá další, Esc výběr zruší, oranžový rámeček, výběr propojený se seznamem). Vybraným výrobkům lze otočit o ↺ 90° / ↻ 90°, zadat libovolný *Úhel vybraných*, nastavit *Nenatáčet* nebo vrátit *Automaticky* — např. aby všechny klíčenky měly očko stejně. Ruční úhel má přednost před automatikou, platí i při volbě Nenatáčet a v seznamu je označen „(ručně)“. CLI `--angle ID=DEG`.
- **Tvary nakreslené přímo v LightBurnu** (spec. v1.14): kruh / elipsa (`Ellipse`), obdélník i se zaoblenými rohy (`Rect`) a mnohoúhelník s libovolným počtem stran (`Polygon`) jako obrys i obsah výrobku, včetně vnořených skupin (klíčenka = kruh s otvorem ve vlastní skupině + text). Přesný obdélník kolem tvaru, tvary v náhledu i při natočení. Ověřeno vlastníkem v LightBurnu pro oba lasery; přesun z aplikace je shodný s přesunem v LightBurnu a tvary se shodují s jejich převodem na křivky (kalibrace KAL-02, `tools/kal02`, odchylka 0,0000 mm).
- **Natočení pro úsporu materiálu** (spec. v1.13, ADR-0005): Mřížka → Natočení *Libovolný úhel (nejmenší plocha)* (výchozí) / *Po 90°* / *Nenatáčet*; nejmenší obdélník kolem skutečných křivek výrobku (konvexní obal, Bézier rozvinutý s odchylkou ≤ 0,002 mm), volba společné orientace na šířku/výšku podle nejmenší mřížky (přednostně vejde-li se na desku); výjimky tlačítkem **Nenatáčet**; úhel v seznamu a natočené motivy v náhledu. Zápis `XForm' = T ∘ XForm` skupiny i `BackupPath` textů, nezávislá kontrola ověřuje celou matici, po znovunačtení se kontroluje poloha skutečných křivek. CLI `--rotate none|90|any`, `--no-rotate`. Protokol uvádí úhel a transformaci. Kalibrace KAL-01 ověřena vlastníkem v LightBurnu (oba lasery).
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

### Opraveno
- Rozměr výrobku s oblým obrysem (Bézierovy křivky) se počítá přesně podle křivky, ne podle jejích řídicích bodů — natočená klíčenka měla rámeček 43,75 mm místo 40 mm a mřížka zbytečně rostla (nahlásil vlastník, Test_klicenky G5).
- Křivky s hladkými uzly (příznak `S` za vrcholem, např. upravené klíčenky) se už nehlásí jako „nečitelná křivka“.
- Natočení *Libovolný úhel* se použije jen tehdy, když mřížka opravdu vyjde menší (dříve mohlo natočení jednoho výrobku mřížku rozšířit); kulaté výrobky se neotáčí o 90°; úhel oblých tvarů se zaokrouhlí (30° místo 29,6°).

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

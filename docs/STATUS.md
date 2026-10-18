# Stav projektu

**Aktualizováno:** 2026-10-17
**Verze specifikace:** 1.18 (`docs/specification.md`)
**Verze aplikace:** `0.1.0-alpha.3` — zveřejněno 2026-10-17 jako GitHub Pre-release (tag `v0.1.0-alpha.3`, commit `a804585`; instalátor, ZIP, SHA256SUMS). Předchozí: `v0.1.0-alpha.2` (2026-10-17, `d8c0cc9`), `v0.1.0-alpha.1` (2026-10-16, `64a5d00`).

> Tento soubor je hlavní předávací dokument. Při navázání práce: přečíst tento soubor → `ROADMAP.md` → relevantní kapitolu specifikace. Nepředpokládat, že funkce funguje jen proto, že existuje kód.

## Přehled

| Hotovo | Probíhá | Blokováno | Další |
|---|---|---|---|
| GIT-00, DOC-00, KAL-00; CORE-00 a ADAPT-00 (T-MVP-26 ověřeno vlastníkem pro `__grid_001` i `__grid_002`); **GUI-00 ověřeno vlastníkem na Windows** (okno, motivy, prohození tažením, světlý/tmavý vzhled, zoom; 2026-10-16) | **EXE-00 / GH-05:** sestavení přenosné složky `GridArranger/` přes PyInstaller (`tools\build_exe.bat`) se samokontrolou; **sestaveno na Windows vlastníka** (samokontrola 5/5 v `GridArranger.exe`, ZIP 28 MB); 286 testů | — | Instalátor `v0.1.0-alpha.2` z GitHub Releases u laseru bez Pythonu (GH-05, T-I18N-16, HELP-01); ostrý provoz → MVP-ACCEPT; po PUB-01 ověřit aktualizaci z aplikace (T-UPD-07) |

## Implementováno / otestováno

| Požadavek | Implementováno | Otestováno | Akceptováno |
|---|---|---|---|
| MVP-01 mřížka (jádro, adaptivní) | ano (`core/grid_layout.py`) | ano — ALG-01…10, T-MVP-01…04 | ne (chybí adaptér a ověření v LightBurnu) |
| MVP-02/03 výběr a pořadí | ano (`core/order.py`, GUI: zaškrtávání, Nahoru/Dolů, přetažení v náhledu) | ano — T-MVP-05, 06, 08…10, testy GUI | ne (ruční test na Windows) |
| MVP-04 materiál a kolize | ano (`core/collision.py`, překážky z adaptéru) | ano — T-MVP-11…18, LB-05 | ne (chybí GUI) |
| MVP-06 okno (GUI) | ano (`gui/`); balení `packaging/`, `tools/build_exe.py` | ano — `tests/gui` (offscreen), samokontrola sestavení | ne (okno ověřeno vlastníkem; čeká EXE na PC bez Pythonu) |
| MVP-07 jazyk cs/en | ano (`gui/i18n.py`, `translations/`) | ano — T-I18N-01…04, 07…15 | ne (T-I18N-05, 06, 16 ruční / EXE) |
| MVP-08 příručka F1 cs/en | ano (`gui/help.py`, `gui/help/`) | ano — T-HELP-01…04, 09 | ne (T-HELP-05…08, 10 / EXE) |
| MVP-05 bezpečné uložení a validace | ano (`adapters/lightburn/write.py`, `safety/verify.py`, `application/arrange_job.py`) | ano — T-MVP-19…25, T-FMT-01…05, 07 | ne (čeká T-MVP-26 ruční kontrola v LightBurnu) |
| Formát `.lbrn2` (čtení, orientace) | ano (`adapters/lightburn/read.py`, `coords.py`) | ano — LB-01…06, 08, 10, 11 | částečně (V-001 ověřen v LightBurnu přes prototyp) |
| Nativní tvary `Ellipse` / `Rect` / `Polygon`, vnořené skupiny (v1.14) | ano (`adapters/lightburn/shapes.py`) | ano — `test_shapes.py`, `test_native_shapes.py`, vzorky C | ano (vzorky C a KAL-02 ověřeny vlastníkem v LightBurnu) |

## Otevřená rozhodnutí

- Žádná. Rozhodnutí z 16. 10. 2026 zapsána ve specifikaci v1.8 (kap. 28).
- Balicí nástroj: PyInstaller (ADR-0003) — potvrzen úspěšným GH-05 (PC bez Pythonu, 2026-10-17).

## Poslední ověřený stav / co zkusit dál

- Ověřeno: čtení struktury `.lbrn2` 2.2.00; převod souřadnic pro `MirrorX/MirrorY` True/True i False/True (přepnutí laseru mění jen příznak, ne souřadnice); přesun skupiny bajtovým patchem (2 řádky) odpovídá LightBurnu a výsledek se v LightBurnu otevřel správně.
- Prototypové skripty KAL-00 jsou v `tools/kal00/` (jen diagnostika, nejsou součástí aplikace); čistá implementace vznikne v ADAPT-00.
- CORE-00: testy prošly v pracovním prostředí (Linux, Python 3.12 a 3.13); kontrolní mutace výpočtu (poloviční mezery) byla testy zachycena (114 selhání). Na Windows zatím nespuštěno — postup v `docs/DEVELOPMENT.md`.
- ADAPT-00: `…__grid_001.lbrn2` (umístění podle původní polohy) ověřen vlastníkem v LightBurnu — vše sedí; připomínka: zarovnávat k počátku laseru → spec. v1.10. Vlastníkův ruční vzor `…__grid_001-zarovnani.lbrn2` (mřížka posunuta na desku 700 × 500).
- Desky vlastníka: červený laser (počátek vpravo nahoře) 700 × 500 mm, modrý (vlevo nahoře) 500 × 400 mm.
- `…__grid_002.lbrn2` (deska 700 × 500, okraj 5, roh počátku, plnění od počátku) ověřen vlastníkem v LightBurnu — sedí.
- Python 3.13.6 nainstalován na Windows vlastníka; `.venv` založen; testy jádra a adaptéru prošly na Windows (221 passed, 1 skipped — test jen pro POSIX).
- GUI-00: okno ověřeno automaticky (offscreen) a na snímcích (cs/en, blokace při přesahu desky, příručka). Na Windows: 268 testů prošlo, okno spuštěno vlastníkem. Podle jeho připomínek doplněno: náhled se skutečnými motivy v barvách vrstev, přeskládání kartiček tažením v náhledu.
- Podle připomínek doplněno a vlastníkem ověřeno na Windows: prohození dvou kartiček tažením, vzhled Nastavení → Vzhled (světlý = celá aplikace světlá; tmavý = tmavé ovládání, náhled světlý), plynulý zoom s mezemi.
- EXE-00: `tools\build_exe.bat` → překlady, testy, PyInstaller, samokontrola `GridArranger --self-test` (příručka, překlady vč. tlačítek Qt, ikona, okno, načtení → rozložení → zápis → kontrola na syntetickém projektu), ZIP. Zkušebně sestaveno na Linuxu (Qt 6.12, Python 3.13): samokontrola 5/5, aplikace se spustí. Na Windows sestaveno 2026-10-16 (Windows 11, Python 3.13.6, PySide6 6.12.0): samokontrola 5/5, ZIP `GridArranger-v0.1.0.dev0-win-x64.zip` 28 MB.
- **GH-05 splněno 2026-10-17:** vlastník ověřil, že sestavená aplikace funguje na PC u laseru bez Pythonu.
- Vydání `v0.1.0-alpha.1`: číslo verze, `SHA256SUMS.txt`, `THIRD_PARTY_NOTICES.txt` a commit v balíčku, release notes `docs/releases/v0.1.0-alpha.1.md` (anglicky), postup `docs/RELEASE_CHECKLIST.md`. Zveřejněno vlastníkem 2026-10-16: tag `v0.1.0-alpha.1` na commitu `64a5d00`, Pre-release se ZIPem a `SHA256SUMS.txt` (https://github.com/Knapis522/lightburn-grid-arranger/releases). Předběžné verze se nezobrazují v pravém sloupci repozitáře — odkaz Releases nebo nadpis „Releases“.
- 2026-10-17 — spec. v1.11, ADR-0004 (požadavek vlastníka): **instalátor** Inno Setup (per-user, bez práv správce, ZIP jako záloha) a **aktualizace z GitHub Releases** — Nastavení → Aktualizace (automaticky, předběžné verze), Nápověda → Zkontrolovat aktualizace; vždy nejnovější verze, Přeskočit / Později / Nainstalovat, ověření SHA-256, tichá instalace jen po souhlasu a znovuspuštění. Verze `0.1.0-alpha.2` (nevydaná). 340 testů (logika bez sítě, GUI s falešným GitHubem, end-to-end přes lokální HTTP server). Instalátor sestaven na Windows vlastníka 2026-10-17; instalace i odinstalace ověřena vlastníkem. Kontrola aktualizací začne fungovat po zveřejnění repozitáře; do té doby hlásí „žádná veřejná vydání“.
- 2026-10-17 — podle připomínky vlastníka: nástrojová lišta s ikonami (Otevřít, Uložit jako nový, Příručka; vlastní SVG ikony podle vzhledu) a název projektu v titulku okna jako v LightBurnu. Rozpracovaná verze `0.1.0-alpha.3` (nevydaná); 343 testů.
- 2026-10-17 — spec. v1.12: při ukládání volba složky a názvu (návrh `__grid_NNN` vedle originálu; nikdy nepřepsat existující soubor, protokol ani originál — vyžádá jiný název); tlačítka Otevřít/Uložit v okně odstraněna (lišta, menu, Ctrl+O/S). 347 testů.
- 2026-10-17 — protokol uložení `.json` volitelný: Nastavení → Protokol uložení (Neukládat — výchozí / Vedle projektu / Složka aplikace). 350 testů.
- 2026-10-17 — levý panel: sbalitelné sekce s výraznější hlavičkou, úzká pole, dvojice hodnot vedle sebe; jednotky mm/palce (Nastavení → Jednotky, jen zobrazení). 353 testů.
- 2026-10-17 — spec. v1.13, ADR-0005: **natočení pro úsporu materiálu** (Libovolný úhel — výchozí / Po 90° / Nenatáčet, výjimky, orientace podle nejmenší mřížky). Implementováno a automaticky otestováno (373 testů, oba typy laseru); **KAL-01 čeká na ověření v LightBurnu** (soubory `…__kal01_rot.lbrn2` v datové složce). Kruh/elipsa/obdélník přímo z LightBurnu čekají na testovací soubor od vlastníka.
- 2026-10-17 — vlastník otestoval celý soupis B (nové funkce okna, uložení, protokol, jednotky, sekce, natočení včetně výstupu s natočením otevřeného v LightBurnu). Čeká: soupis A (kalibrační soubory KAL-01, směr natočení) a testovací soubory C (kruh/elipsa/obdélník, klíčenky, `Kalibrace_A_rot30`).
- 2026-10-17 — **KAL-01 splněno** (soupis A ověřen vlastníkem v LightBurnu pro oba lasery): natočení skupin i textů funguje. Zbývá: testovací soubory C (tvary přímo z LightBurnu, klíčenky), vydání `v0.1.0-alpha.3`, zkouška u laseru.
- 2026-10-17 — spec. v1.14 (**SHAPES-00**): tvary nakreslené přímo v LightBurnu — `Ellipse`, `Rect` bez zaoblení, `Polygon` se 6 stranami — jako obrys i obsah, vnořené skupiny (klíčenky); příznak hladkého uzlu `S`. Ověřeno automaticky na vzorcích C (oba lasery, všech 8 + 8 + 8 výrobků podporováno; náš posun shodný s přesunem v LightBurnu). Natočení: použije se jen při menší mřížce, kulaté výrobky bez otočení o 90°, hezký úhel. Jiné mnohoúhelníky a zaoblené rohy blokovány do KAL-02 (`tools/kal02`). 411 testů. Čeká: kontrola výstupů vzorků C v LightBurnu, KAL-02.
- 2026-10-17 — vlastník ověřil výstupy vzorků C v LightBurnu (v pořádku) a dodal tvary z KAL-02 převedené na křivky: vzorec vrcholů mnohoúhelníku opraven (`90° + 180°/N + k·360°/N`; dřívější platil jen pro N = 6), poloměr rohu = mm s omezením na polovinu kratší strany. Všech 12 tvarů shodných s LightBurnem (0,0000 mm) → **KAL-02 splněno**, povoleny všechny mnohoúhelníky a zaoblené rohy. 419 testů. Další krok: vydání `v0.1.0-alpha.3`.
- 2026-10-17 — vlastník nahlásil příliš velký rámeček klíčenky G5 (Test_klicenky): AABB cest byl obal řídicích bodů Bézierových křivek (u šikmo nakreslených kruhů až o 1,9 mm na každé straně). Nyní přesně podle extrémů křivky (spec. kap. 5 bod 2); G5 40 × 40 mm místo 43,75 × 43,75; ostatní vzorky beze změny (kartičky V-001, KAL-01). 423 testů.
- 2026-10-17 — spec. v1.15 (přání vlastníka): **výběr výrobku kliknutím v náhledu** (Ctrl+klik přidá, oranžový rámeček, propojeno se seznamem) a **ruční natočení** vybraných výrobků — Úhel vybraných, ↺ 90° / ↻ 90°, Nenatáčet (= 0°), Automaticky; ruční úhel má přednost a platí i v režimu Nenatáčet; CLI `--angle`. 430 testů. Čeká ruční vyzkoušení vlastníkem.
- 2026-10-17 — spec. v1.16 (přání vlastníka): **kopie výrobků** (V11-02 předsunuto) — Ctrl+C / Ctrl+V, Vytvořit kopie… (ikona na liště, Ctrl+D, počet kopií), Odebrat kopie (Delete), menu Úpravy; zápis kopií jako nových skupin se sdílenou geometrií, nezávislá kontrola kopií; CLI `--copies`. 440 testů. **Čeká KAL-03** (kalibrační výstupy `…__kal03_kopie.lbrn2` v datové složce otevřít v LightBurnu).
- 2026-10-17 — **GH-05 splněno:** vlastník ověřil běh sestavené aplikace na PC bez Pythonu (u laseru).
- 2026-10-17 — **KAL-03 splněno** (kopie výrobků ověřeny vlastníkem v LightBurnu). Připraveno vydání `v0.1.0-alpha.3` (CHANGELOG, release notes).
- 2026-10-17 — **Vydáno `v0.1.0-alpha.3`** (GitHub Pre-release, tag na commitu `a804585`): natočení, tvary z LightBurnu, ruční natočení a výběr v náhledu, kopie výrobků, nástrojová lišta, dialog uložení, volitelný protokol, jednotky, nový levý panel. Další číslo pro vývoj: `0.1.0a4`.
- 2026-10-18 — spec. v1.17, brána **PUB-00** (rozhodnutí vlastníka: zveřejnit repozitář s předběžnými verzemi kvůli aktualizacím). Splněno: audit celé historie (124 souborů, žádné projekty `.lbrn2`, zákaznická data, tokeny ani cizí grafika), MIT `LICENSE`, `THIRD_PARTY_NOTICES.md`, anglický `README`, `SECURITY.md`, licence přibalená k sestavení. Zbývá: commit a přepnutí viditelnosti vlastníkem, zapnout *Private vulnerability reporting*, ověřit kontrolu aktualizací (T-UPD-07).
- 2026-10-18 — **PUB-00 splněno:** repozitář přepnut na veřejný (Pre-release alpha.1–alpha.3 dostupné bez přihlášení), zapnuto soukromé hlášení zranitelností, další commity s anonymním e-mailem GitHubu. Kontrola aktualizací v aplikaci na PC u laseru funguje (ohlásí aktuální verzi). Ověření instalace aktualizace ze starší verze proběhne s příštím vydáním (T-UPD-07).
- 2026-10-18 — rozpracováno `0.1.0-alpha.4` (spec. v1.18): okno si pamatuje velikost a maximalizaci; **Otevřít v LightBurnu** (přiřazení `.lbrn2`, chování LightBurnu ověřeno vlastníkem: nahradí projekt, na neuložené změny se zeptá). 442 testů.
- 2026-10-18 — `0.1.0-alpha.4` (spec. v1.19): krok zpět / vpřed a lišta uspořádatelná tažením; po uložení titulek a sekce Projekt ukazují „naposledy uloženo jako …“, volba pokračovat s uloženým souborem místo originálu, návrh názvu ze `__grid_NNN` pokračuje v řadě originálu. 447 testů.
- 2026-10-18 — spec. v1.20: **okno Nastavení** (modální, stránky Obecné / Uložení / Aktualizace, OK / Zrušit / Použít) místo rozbalovacího menu; **panel rozložení vlevo / vpravo** od náhledu. 449 testů.
- 2026-10-18 — **alpha.4 připravena k vydání:** změny ověřeny vlastníkem na Windows a commitnuty; CHANGELOG a release notes s datem. Zbývá sestavení (`tools\build_exe.bat`), tag `v0.1.0-alpha.4`, Pre-release a ověření aktualizace z alpha.3 na PC u laseru (T-UPD-07). 450 testů.

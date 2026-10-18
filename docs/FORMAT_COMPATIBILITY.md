# Kompatibilita formátu `.lbrn2`

Živá matice ověřených verzí a konstrukcí (spec. kap. 41.4). Stavy: `ověřeno` / `částečně` / `neověřeno` / `nepodporováno`.

## Matice

| LightBurn | FormatVersion | Konstrukce | Čtení | Přesun | Round-trip | Preview | Poznámka |
|---|---|---|---|---|---|---|---|
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | Top-level `Group` s `Path` + `Text` (BackupPath); `MirrorX=True, MirrorY=True` | ověřeno | ověřeno | ověřeno (prototyp) | ověřeno (File → Open) | V-001, V-002 |
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | totéž; `MirrorX=False, MirrorY=True` | ověřeno | ověřeno (LightBurn) | neověřeno | neověřeno | V-003 |
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | Nativní tvary `Ellipse`, `Rect` (i se zaoblením `Cr`), `Polygon` (libovolné N) ve skupině, i ve vnořené skupině (klíčenky); oba lasery | ověřeno | ověřeno (shoda s přesunem v LightBurnu) | ověřeno | ověřeno (výstupy otevřeny vlastníkem) | Test_tvary_A / L_A / _posun, Test_klicenky, KAL-02 |
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | Kopie výrobků jako nové skupiny (sdílená geometrie přes `VertID`/`PrimID`); oba lasery | ověřeno | ověřeno | ověřeno | ověřeno (KAL-03) | `KAL03\` |
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | `MirrorY=False` (počátek vlevo dole / vpravo dole, např. diodové lasery) | implementováno (spec. v1.22) | testy syntetické | — | — | **čeká na KAL-04**; aplikace zobrazí upozornění |

## Vzorek V-001 (KAL-00, pouze čtení)

- **Datum:** 2026-10-16. Soubor uložen mimo Git (`..\lightburn-grid-arranger-data\`), SHA-256 `d83c49cd535960af12dffd767ac3bb3b42ba10374aea8fe87ecbb2529780b951`, 911 165 B.
- **Stroj:** Ruida 6445S; v projektu `MirrorX="True" MirrorY="True"`.
- **Kódování:** XML 1.0, UTF-8, konce řádků **CRLF**, velmi dlouhé řádky (až ~31 kB). Zápis musí zachovat CRLF i všechny ostatní bajty.

### Struktura kořene

```text
LightBurnProject  AppVersion="2.2.00" FormatVersion="1" MirrorX MirrorY DeviceName …
  Thumbnail Source="<base64 PNG>"
  VariableText (Start, End, Current, Increment, AutoAdvance)
  UIPrefs (Optimize_* …)
  CutSetting type="Cut" ×3     (index 1–3, name C01–C03; hodnoty v atributech Value)
  Shape Type="Group" CutIndex="0" ×9   ← kandidáti na výrobky
    XForm  "a b c d e f"
    Children
      Shape Type="Path" CutIndex VertID PrimID
        XForm
        VertList  "V x y c0x… c0y… c1x… c1y…"   (c0x1 / c1x1 = bez řídicího bodu)
        PrimList  "B0 1B1 2…" | "L…" | "LineClosed"
      Shape Type="Text" Font Str H Ah Av Weld HasBackupPath="1" …
        BackupPath Type="Path" (XForm, VertList, PrimList)
        XForm
  Notes
```

### Zjištění

1. **Transformace skupin:** všech 9 skupin má čistou translaci `1 0 0 1 e f`. Potomci mají vlastní `XForm`; složení `XForm(skupina) ∘ XForm(potomek)` dává konzistentní geometrii (veškerý obsah leží uvnitř obrysu). Model kap. 8 platí.
2. **Sdílené seznamy vrcholů:** `VertID`/`PrimID` jsou identifikátory sdílených seznamů. 3 cesty nemají vlastní `VertList` a odkazují na seznam definovaný u jiného tvaru se stejným `VertID`. Čtečka musí ID rozlišovat; pro v1.1 (kopie) je to zásadní.
3. **Obrys výrobku není `Rect`:** v souboru není žádný `Rect`. Každá skupina má jako vnější obrys **zaoblený obdélník převedený na uzavřenou lomenou čáru se 132 vrcholy** (rohy aproximované úsečkami; `PrimList="LineClosed"`, jen přímé úseky) na vrstvě `C02` (řez: 40 %, 65 mm/s, 3 průchody). Obrys obsahuje veškerý ostatní obsah skupiny. Rozměry AABB: 187,500 × 143,050 mm (5×), 196,798 × 143,050, 200,210 × 143,050 (2×), 213,533 × 143,050 mm → **různé rozměry**. Podle pravidla v1.8 (Rect nebo 4bodová cesta) by byly odmítnuty **všechny** výrobky → nutné rozhodnutí o rozšíření pravidla.
4. **Text má uloženou geometrii:** každý `Text` má `HasBackupPath="1"` a `BackupPath` s úplnou křivkou písma → hranice textu **lze spočítat**. Všechny texty leží uvnitř obrysu.
5. **⚠ `BackupPath/XForm` je uložen ve světových souřadnicích:** u všech 9 textů platí `XForm(BackupPath) = XForm(skupina) ∘ XForm(text)` (shoda na 10⁻³ mm). Pokud se změní jen `XForm` skupiny, záložní křivka zůstane na **staré pozici**. Riziko: při chybějícím fontu by LightBurn mohl vykreslit text mimo kartičku. Nutno ověřit kalibračním párem A/B, zda LightBurn při přesunu skupiny `BackupPath/XForm` přepisuje.
6. **Přesnost čísel:** LightBurn zapisuje cca 8 platných číslic (např. `1320.3398`, `469.89063`), desetinná tečka.
7. **Neseskupené objekty:** ve vzorku žádné; všech 9 tvarů nejvyšší úrovně jsou skupiny.
8. **Thumbnail:** přítomen (PNG v base64); po přesunu bude neaktuální (povolená výjimka v1.8).

9. **Orientace zobrazení (hypotéza H1, vizuálně potvrzena vlastníkem 2026-10-16):** při `MirrorX="True" MirrorY="True"` zobrazuje LightBurn soubor jako `obrazovka_x = −x_souboru`, `obrazovka_y (dolů) = +y_souboru`. Vykreslení podle H1 odpovídá obrazovce LightBurnu (nápisy nahoře, motivy svisle správně). Z toho plyne pro mřížku „zleva doprava, shora dolů“: sloupce postupují ke **klesajícímu X souboru**, řádky k **rostoucímu Y souboru**. Zobecnění pro ostatní kombinace (`obrazovka_x = ±x`, `obrazovka_y = ∓y` podle příznaků Mirror) je **neověřené** → v MVP podporovat jen ověřené kombinace, ostatní odmítnout (T-MVP-25 / LB-06).

## Vzorek V-002 — kalibrační pár A/B (2026-10-16)

Laser s počátkem **vpravo nahoře** (`MirrorX="True" MirrorY="True"`). A = V-001 znovu uložený, B = skupina „kachna“ (9. skupina, index 8) posunuta v UI LightBurnu o X +50, Y +30.

1. **Deterministické ukládání:** A je bajtově shodný s V-001 (SHA-256 `d83c49cd…b951`) → opakované uložení bez změny nemění ani bajt.
2. **Rozdíl A → B = přesně 3 řádky:** `Thumbnail`; `XForm` skupiny `1312 -641.83984` → `1362 -611.83997`; `BackupPath/XForm` textu ve skupině `950.99646 -412.24298` → `1000.9965 -382.2431`. Nic jiného se nezměnilo.
3. **Hodnoty X/Y v UI = souřadnice souboru** (posun +50/+30 v UI = +50/+30 v souboru). Spolu s H1: u tohoto laseru roste X doleva a Y dolů, počátek vpravo nahoře.
4. **LightBurn při přesunu skupiny posouvá i `BackupPath/XForm` všech textů ve skupině** → povolená změna pro náš zápis (spec. v1.9).
5. **Formát čísel:** 8 platných číslic (`format(v, '.8g')`); LightBurn při přesunu vnáší šum ~1,3·10⁻⁴ mm.

### Důkaz vlastního zápisu (prototyp `tools/kal00/patch_poc.py`)

Z A vytvořen `Kalibrace_C__grid_poc.lbrn2` posunem skupiny 8 o (+50, +30) metodou bajtových úseků (`expat` → pozice `<XForm>`), zápis s příznakem „nikdy nepřepsat“:

- A → C: změněny **právě 2 řádky** (XForm skupiny, XForm BackupPath); CRLF a všechny ostatní bajty zachovány; A beze změny.
- C vs. B (LightBurn): rozdíl jen v `Thumbnail` (povolená výjimka) a v zaokrouhlení 1,3·10⁻⁴ mm (náš výsledek je přesný součet).
- **Ověřeno vlastníkem 2026-10-16:** C otevřen v LightBurnu přes File → Open; poloha, text, vrstvy i Preview v pořádku.

## Vzorek V-003 — druhý laser, počátek vlevo nahoře (2026-10-16)

`Kalibrace_L_A` = V-001 po přepnutí zařízení na laser s počátkem vlevo nahoře; `Kalibrace_L_B` = kachna posunuta v UI o X +50, Y +30.

1. **Přepnutí zařízení nemění souřadnice.** A → L_A: změna hlavičky (`DeviceName`, `MirrorX="True"` → `"False"`, `MirrorY` zůstává `"True"`), `Thumbnail` a přečíslování `VertID`/`PrimID` (1 636 řádků, jen čísla ID). Všechny `XForm` a geometrie beze změny. Vlastník pozoroval, že se projekt po přepnutí zobrazí zrcadlově → příznaky Mirror určují jen zobrazení.
2. **UI = soubor i zde:** L_A → L_B posun skupiny +50/+30 v souboru (stejné hodnoty jako u V-002).
3. **Převod potvrzen pro obě kombinace:** `screen_x = MirrorX ? −x : +x`, `screen_y = MirrorY ? +y : −y` (spec. kap. 8).
4. LightBurn v L_B navíc **přegeneroval** `BackupPath` textu (jiné body, šířka 140,716 místo 140,663 mm). Pro náš zápis bez významu — u V-002 se BackupPath jen posunul, což děláme i my.
5. **`VertID`/`PrimID` nejsou stabilní** mezi uloženími → nepoužívat jako identitu výrobků mezi soubory.

## Bézierovy úseky (ověřeno vykreslením V-001, 2026-10-16)

Úsek `B i j` v `PrimList` = kubická Bézierova křivka z vrcholu *i* do *j* s řídicími body **`c0` vrcholu *i*** (odchozí) a **`c1` vrcholu *j*** (příchozí); `c0x1` / `c1x1` = řídicí bod chybí (= vrchol). Ověřeno na textu „SESTAV SI SÁM“ (`BackupPath`): s tímto přiřazením je písmo hladké, s opačným lomené. Používá se pro náhled a od 2026-10-17 i pro AABB: rozměr výrobku podle skutečných extrémů křivky (dříve obal řídicích bodů — u natočené klíčenky Test_klicenky G5 o 3,75 mm větší rámeček); obal řídicích bodů jen u nečitelného `PrimList`.

### Otevřené body KAL-00

- [x] Číselné potvrzení H1 a vztahu UI ↔ soubor (laser s počátkem vpravo nahoře).
- [x] Chování `BackupPath/XForm` při přesunu skupiny.
- [x] Pravidlo pro neobdélníkové uzavřené obrysy — schváleno vlastníkem 2026-10-16 (spec. v1.9).
- [x] Otevření `Kalibrace_C__grid_poc.lbrn2` v LightBurnu (File → Open, Preview) — v pořádku.
- [x] Druhý laser s počátkem vlevo nahoře: `MirrorX=False, MirrorY=True`, souřadnice beze změny.
- [ ] Negativní testy (poškozený / neznámý soubor, `.lbrn`, nepodporované Mirror) → přesunuto do automatických testů ADAPT-00 (T-FMT-02, 03, 05; T-MVP-25).

**Stav brány KAL-00: SPLNĚNO 2026-10-16** pro LightBurn 2.2.00-RC-7 a kombinace Mirror True/True a False/True; negativní testy jsou podmínkou dokončení ADAPT-00.

## KAL-01 — natočení skupin (2026-10-17, ověřeno vlastníkem)

Zápis natočení: `XForm' = T ∘ XForm` u nejvyšší skupiny i u `BackupPath` každého textu v ní (BackupPath je ve světových souřadnicích, KAL-00), kde `T` je natočení kolem středu obrysu (+ posun). Nástroj `tools/kal01/rotate_calibration.py` vytvořil z V-001 / V-003:

- `Kalibrace_A__kal01_rot.lbrn2`, `Kalibrace_L_A__kal01_rot.lbrn2` — G1 90°, G2 30°, G3 180°, G4 −15° (v souřadnicích souboru); změněno přesně 8 `XForm` (4 skupiny + 4 BackupPath), nezávislá kontrola OK, po znovunačtení všechny výrobky podporované (BackupPath odpovídá složené transformaci textu).
- `Kalibrace_A__kal01_rot__grid_001.lbrn2` — výstup aplikace s volbou *Libovolný úhel*: natočené kartičky srovnány zpět (G1 90°, G2 30°, G4 −15° v souřadnicích obrazovky), G3 (180°) ponechána — plochu nezmenší.

### Otevřené body KAL-01

- [x] Otevření kalibračních souborů v LightBurnu (File → Open): kartičky celé, text na kartičce a natočený s ní, Preview v pořádku — ověřeno vlastníkem 2026-10-17 pro oba lasery.
- [x] Konzistence směru natočení: výstup aplikace `__grid_001` (srovnání šikmých kartiček zpět) vypadá v LightBurnu jako původní kalibrace → převod jádro ↔ soubor (`S∘T∘S`) odpovídá zobrazení LightBurnu. Absolutní směr (po/proti hodinám) vlastník nezapisoval — pro funkci není potřeba.
- [x] Srovnaný výstup `__grid_001` vypadá jako původní kalibrace (kromě G3 vzhůru nohama) — ověřeno; vlastník navíc uložil z aplikace `__grid_002` s natočením a otevřel ho v LightBurnu.

**Stav brány KAL-01: SPLNĚNO 2026-10-17** (LightBurn 2.2.00-RC-7, Mirror True/True a False/True). Doplňující porovnání s natočením provedeným přímo v LightBurnu: `Kalibrace_A_rot30.lbrn2` (soupis C4) — volitelné.


## Vzorky C — nativní tvary a klíčenky (2026-10-17)

Soubory od vlastníka (mimo Git, `lightburn-grid-arranger-data`): `Test_tvary_A.lbrn2` (vpravo nahoře), `Test_tvary_L_A.lbrn2` (vlevo nahoře), `Test_tvary_A_posun.lbrn2` (klíčenka K1 posunutá v LightBurnu o +50 / +30 mm), `Test_klicenky.lbrn2` (8 skutečných klíčenek), `Kalibrace_A_rot30.lbrn2` (natočení o 30° provedené v LightBurnu).

### Zjištění

1. **Nativní tvary nemají `VertList`** — jen rozměry v atributech a `XForm`, jehož posun je **střed** tvaru:
   - `<Shape Type="Ellipse" Rx="20" Ry="20">` — elipsa s poloosami Rx, Ry;
   - `<Shape Type="Rect" W="59.999996" H="40" Cr="0">` — obdélník se středem v počátku (ověřeno podle středu textu na něm);
   - `<Shape Type="Polygon" Rx="30.5" Ry="30.5" N="6">` s `XForm` `-1 0 0 1 …` — šestiúhelník: podle náhledu v souboru hrot vlevo a vpravo, rovná strana nahoře. Obecné pravidlo pro vrcholy určila až KAL-02 (níže).
2. **Klíčenky** = nejvyšší skupina bez `CutIndex` → vnořená skupina (`Ellipse` Rx 20 = obrys + `Ellipse` Rx 2,5 = otvor) + `Text`. Čtení prochází vnořené skupiny; obrysem je velký kruh.
3. **Elipsa natočená v LightBurnu** (E2): natočení je v `XForm` skupiny, `BackupPath` textu = skupina ∘ text (stejně jako KAL-01). AABB 54,08 × 39,69 mm = elipsa 60 × 30 natočená o 30°.
4. **Přesun v LightBurnu** (`_posun`): změnily se přesně dva řádky — `XForm` nejvyšší skupiny (`1 0 0 1 50.000076 30.000229`) a `XForm` v `BackupPath` textu. Náš zápis stejného posunu dá **tytéž dva řádky**; liší se jen poslední řád (`254.68969` vs `254.68968`, LightBurn počítá v jednoduché přesnosti) a náhled (`Thumbnail`). Vnitřní kruhy se nemění — potvrzuje pravidlo „měnit jen nejvyšší skupinu a BackupPath“ i pro vnořené skupiny.
5. **Příznak `S` za vrcholem** (`…c1y168.51593SV327 198…`, Test_klicenky): hladký uzel pro úpravy v LightBurnu; geometrii nemění. Dříve způsoboval „nečitelný vrchol“.
6. **Zaoblený obdélník převedený na křivky** („Obdéln“, 80 × 50, poloměr 5): 8 vrcholů, `PrimList` `B0 1L1 2B2 3L3 4B4 5L5 6B6 7L7 0`, řídicí body ve vzdálenosti 0,5523 · r (kubická aproximace čtvrtkruhu) — aplikace vytváří z `Rect` s `Cr` stejnou cestu (test `test_rounded_rect_path_matches_lightburn_conversion`).
7. **Natočení o 30° v LightBurnu** (`Kalibrace_A_rot30`): `XForm` skupiny `0.86602539 -0.5 0.5 0.86602539 …`; náš kalibrační soubor KAL-01 měl pro „+30°“ opačné znaménko `b` — jde jen o konvenci směru úhlu, aplikace je vnitřně konzistentní (KAL-01). Soubor se načte, všechny výrobky podporované.

### Zpracování v aplikaci (spec. v1.14 kap. 5)

- Obrys z nativního tvaru: AABB **přesně** (elipsa analyticky `hx = √((a·Rx)² + (c·Ry)²)`, mnohoúhelník z vrcholů, zaoblený obdélník z rohů vnitřního obdélníku + elipsy rohu).
- Náhled a výpočet natočení: tvar převedený na ekvivalentní cestu (elipsa 4 Bézierovy úseky, `Rect` s `Cr` jako výše, mnohoúhelník lomená čára).
- Neznámé atributy nebo prvky v nativním tvaru, nečitelné rozměry → výrobek blokován.
- Výsledky na vzorcích: Test_tvary_A / L_A — všech 8 výrobků podporováno; Test_klicenky — 8/8 podporováno, s natočením *Libovolný úhel* (4 sloupce, mezera 3 mm) mřížka 174,8 × 86,8 mm místo 187,5 × 99,2 mm (**−18,5 % plochy**).

### KAL-02 — ověření dalších nativních tvarů (2026-10-17, ověřeno vlastníkem)

Nástroj `tools/kal02/native_shapes_calibration.py <šablona.lbrn2>` vytvořil `Test_tvary_A__kal02_tvary.lbrn2`: 12 skupin, v každé nativní tvar (vrstva 0) a výpočet aplikace jako křivka (vrstva 1) — mnohoúhelníky N = 3, 4, 5, 5 zrcadlený, 7, 8, 5 eliptický (25 × 14), 6; obdélníky 50 × 34 s poloměrem 5, 12 a 30; elipsa natočená o 30°.

- [x] Otevřeno v LightBurnu — v pořádku (vlastník).
- [x] Vlastník převedl tvary na vrstvě 0 na křivky (Convert to Path) a uložil `Test_tvary_A__kal02_tvary_prevedeno.lbrn2`. Zjištění:
  - **Mnohoúhelník:** vrcholy v úhlech `90° + 180°/N + k·360°/N` na elipse Rx, Ry (lichý N: vrchol v `(0, −Ry)`; N = 6 → vrchol na ose X, shodně s Test_tvary_A). Původní předpoklad `2πk/N` platil jen pro N = 6 — blokace neověřených N byla oprávněná (odchylka až 15 mm u N = 4).
  - **Zaoblený obdélník:** `Cr` = poloměr rohu v mm, roh = čtvrtkruh z kubické Bézierovy křivky (0,5523 · r); poloměr větší než polovina kratší strany LightBurn omezí (Cr 30 u výšky 34 → 17).
  - **Elipsa:** 4 Bézierovy úseky (opačný směr než naše cesta — geometrie shodná).
  - Convert to Path rozpustí skupiny, sdílí `VertID`/`PrimID` u stejných tvarů a přidá příznak `S`.
- [x] `--compare` (výpočet aplikace proti tvarům z LightBurnu): **všech 12 tvarů odchylka 0,0000 mm**.
- [x] Povoleny všechny počty stran a zaoblené rohy; testy s čísly z LightBurnu (`test_polygon_vertices_match_lightburn`, `test_rounded_rect_matches_lightburn_including_clamped_radius`).

**Stav brány KAL-02: SPLNĚNO 2026-10-17** (LightBurn 2.2.00-RC-7).

## KAL-03 — kopie výrobků (2026-10-17, ověřeno vlastníkem)

Kopie se zapisují jako nové nejvyšší skupiny za poslední původní tvar (spec. v1.16 kap. 22.2). Cesty se sdíleným `VertID`/`PrimID` v kopii nemají `VertList`/`PrimList` — odkazují na definici v originálu (stejný zápis použil LightBurn v souboru z KAL-02 pro opakované tvary). Texty mají `BackupPath` přímo v kopii, nativní tvary nemají ID.

Kalibrační výstupy (datová složka, `KAL03\`):
- `Test_klicenky__kal03_kopie.lbrn2` — 4 kopie G5 (jedna o 90°, jedna o 180°), kopie G2 a G8, natočení *Libovolný úhel*;
- `Test_tvary_A__kal03_kopie.lbrn2` — 2 kopie klíčenky K1 (vnořená skupina), kopie E2 (natočená elipsa, ručně 0°), šestiúhelníku a zaobleného obdélníku; vpravo nahoře;
- `Test_tvary_L_A__kal03_kopie.lbrn2` — totéž pro laser vlevo nahoře.

- [x] Otevřít v LightBurnu (File → Open): kopie celé (obrysy, otvory, texty, motivy), na správných vrstvách, Preview v pořádku.
- [x] Kopii vybrat, posunout a upravit (editovatelnost); uložit a znovu otevřít — LightBurn sdílená ID přečísluje sám.
- [x] Ověřeno vlastníkem 2026-10-17 — v pořádku.

**Stav brány KAL-03: SPLNĚNO 2026-10-17** (LightBurn 2.2.00-RC-7, oba lasery).

## KAL-04 — počátek dole (spec. v1.22, čeká na ověření)

Podle V-003 příznaky `MirrorX/MirrorY` mění jen zobrazení, souřadnice souboru zůstávají (X/Y v UI = soubor). Pro `MirrorY=False` z toho plyne osa Y souboru nahoru: `screen_y = −y` (stejný vzorec, kap. 8). Transformace natočení `S ∘ T ∘ S` je pro determinant ±1 už ověřena (vlevo nahoře det +1, vpravo nahoře det −1; vlevo dole −1, vpravo dole +1).

**Postup ověření (vlastník, bez stroje):** v LightBurnu vytvořit testovací zařízení (Devices → Create Manually → GRBL, počátek *Front Left* / *Front Right*, libovolná plocha), s ním znovu uložit kalibrační projekt (`Kalibrace_A__BL.lbrn2`, `Kalibrace_A__BR.lbrn2`), v aplikaci rozložit (deska, roh u počátku, natočení, kopie) a výstup otevřít v LightBurnu se stejným zařízením: mřížka v rohu u počátku s okrajem, souřadnice prvního výrobku X 5 / Y 5, natočení a texty, Preview. Potom vrátit skutečný laser.

- [ ] vlevo dole (`MirrorX=False, MirrorY=False`)
- [ ] vpravo dole (`MirrorX=True, MirrorY=False`)

## KAL-05 — převod projektu na jiný laser (spec. v1.23, čeká na ověření)

Výstup pro cílový laser mění v hlavičce jen `DeviceName`, `MirrorX`, `MirrorY` (jako přepnutí zařízení v LightBurnu podle V-003; `Thumbnail` a přečíslování `VertID`/`PrimID` aplikace nedělá) a výrobky dostanou `XForm' = S_cíl ∘ T ∘ S_zdroj ∘ XForm` — při jiné orientaci se zrcadlením (záporný determinant), stejně jako po *Flip Horizontal/Vertical* v LightBurnu.

**Postup ověření (vlastník):** projekt pro červený laser (vpravo nahoře) → v aplikaci *Připravit pro:* modrý laser (vlevo nahoře) → uložit → otevřít v LightBurnu s modrým laserem: texty a motivy nejsou zrcadlově, mřížka v rohu u počátku, Preview v pořádku; porovnat s ručním postupem (přepnutí zařízení + Flip). Totéž s natočeným výrobkem, kopiemi a s textem; případně i diodový laser (vlevo dole).

- [ ] vpravo nahoře → vlevo nahoře (červený → modrý)
- [ ] vlevo nahoře → vpravo nahoře (modrý → červený)
- [ ] na laser s počátkem dole (testovací zařízení)

# Kompatibilita formátu `.lbrn2`

Živá matice ověřených verzí a konstrukcí (spec. kap. 41.4). Stavy: `ověřeno` / `částečně` / `neověřeno` / `nepodporováno`.

## Matice

| LightBurn | FormatVersion | Konstrukce | Čtení | Přesun | Round-trip | Preview | Poznámka |
|---|---|---|---|---|---|---|---|
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | Top-level `Group` s `Path` + `Text` (BackupPath); `MirrorX=True, MirrorY=True` | ověřeno | ověřeno | ověřeno (prototyp) | ověřeno (File → Open) | V-001, V-002 |
| Pro 2.2.00-RC-7 (Qt 6.11.2) | 1 | totéž; `MirrorX=False, MirrorY=True` | ověřeno | ověřeno (LightBurn) | neověřeno | neověřeno | V-003 |
| — | — | `MirrorY=False` (jakékoli `MirrorX`) | — | — | — | — | **nepodporováno v MVP** (neověřeno) |

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

Úsek `B i j` v `PrimList` = kubická Bézierova křivka z vrcholu *i* do *j* s řídicími body **`c0` vrcholu *i*** (odchozí) a **`c1` vrcholu *j*** (příchozí); `c0x1` / `c1x1` = řídicí bod chybí (= vrchol). Ověřeno na textu „SESTAV SI SÁM“ (`BackupPath`): s tímto přiřazením je písmo hladké, s opačným lomené. Používá se jen pro náhled; AABB zůstává konzervativní (obal řídicích bodů).

### Otevřené body KAL-00

- [x] Číselné potvrzení H1 a vztahu UI ↔ soubor (laser s počátkem vpravo nahoře).
- [x] Chování `BackupPath/XForm` při přesunu skupiny.
- [x] Pravidlo pro neobdélníkové uzavřené obrysy — schváleno vlastníkem 2026-10-16 (spec. v1.9).
- [x] Otevření `Kalibrace_C__grid_poc.lbrn2` v LightBurnu (File → Open, Preview) — v pořádku.
- [x] Druhý laser s počátkem vlevo nahoře: `MirrorX=False, MirrorY=True`, souřadnice beze změny.
- [ ] Negativní testy (poškozený / neznámý soubor, `.lbrn`, nepodporované Mirror) → přesunuto do automatických testů ADAPT-00 (T-FMT-02, 03, 05; T-MVP-25).

**Stav brány KAL-00: SPLNĚNO 2026-10-16** pro LightBurn 2.2.00-RC-7 a kombinace Mirror True/True a False/True; negativní testy jsou podmínkou dokončení ADAPT-00.

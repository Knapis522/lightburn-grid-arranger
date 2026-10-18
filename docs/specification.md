# Grid Arranger for LightBurn — technická specifikace

**Verze dokumentu:** 1.26 (osm jazyků rozhraní a příručky — strojový návrh; viz kap. 36.5)  
**Datum:** 17. 10. 2026  
**Název produktu:** Grid Arranger for LightBurn; spustitelný soubor `GridArranger.exe`; Python balíček `grid_arranger`; repozitář `lightburn-grid-arranger`. Neoficiální nástroj, nikoli produkt LightBurn Software.  
**Stav:** Interní pracovní podklad; nikoli hotový nebo otestovaný plugin  
**Záměr:** Nejprve funkční soukromý prototyp, následně ověřování v reálné výrobě; teprve potom případně zveřejnění.  
**Cílová forma aplikace:** offline desktopová aplikace pro Windows 10/11, dodávaná jako `.exe`; webová aplikace ani plugin přímo v LightBurnu nejsou součástí první verze.

**Závazný projektový formát (rozhodnutí FMT-00):** **pouze `.lbrn2` pro vstup i výstup**. Starší `.lbrn` nebude načítán, zapisován, konvertován ani používán jako alternativní implementační cesta. Rozhodnutí nevylučuje zachování odděleného interního výpočetního jádra. Viz kapitola 41.

**Publikační strategie:** Od zahájení implementace soukromý GitHub repozitář. Veřejné zveřejnění a kontaktování LightBurnu pouze po interním schválení; nejsou automatickým výsledkem dokončení MVP. Podrobnosti v kapitolách 29–35.

**Řízení rozsahu:** Funkce jsou závazně rozděleny na **MVP**, **funkční verzi aplikace 1.1**, **verzi 2.0** a **nezávazný výhled**. Podrobnosti, závislosti, testy a akceptace funkcí jsou v kapitolách 20–26; publikační proces je v kapitolách 29–35; lokalizace v kapitole 36; průběžná dokumentace, vestavěná nápověda, harmonogram a dokončovací brány v kapitolách 37–40. Číslo verze dokumentu (1.10) není číslo vydané aplikace.

> **Hlavní princip:** Oddělit obecný algoritmus rozmístění od adaptérů, které čtou a upravují projekty LightBurnu. Do původního souboru nikdy nezapisovat. Při jakékoli nejednoznačnosti skončit bezpečnou chybou, nikoli tichou úpravou výroby.

## 1. Zadání a cílový stav

### 1.1 Konkrétní problém

Uživatel má například 10 dřevěných kartiček o rozměrech 100 × 60 mm. Každá má vlastní nápis, případně jinou vnitřní grafiku, a vlastní seskupené čáry pro řezání a gravírování. Kartičky jsou v projektu LightBurn rozházené. Běžný **Grid Array** vytváří kopie výběru; požadovaná funkce musí naopak **přesunout 10 již existujících, navzájem odlišných kartiček** do mřížky s přesnou mezerou, aniž cokoli kopíruje nebo mění uvnitř skupin.

### 1.2 Definice úspěchu

Uživatel otevře kopii existujícího projektu `.lbrn2`, vybere kartičky nebo použije připravené samostatné skupiny, nastaví počet sloupců a mezery v mm, uvidí náhled, získá **nový projekt** se správným rozmístěním a zkontroluje jej v LightBurnu. Všechny geometrie, texty, nastavení vrstev, skupiny a ostatní vlastnosti zůstanou zachovány; změní se pouze transformační posun vybraných skupin.

### 1.3 Dlouhodobý cíl

Získat malé, srozumitelné a nezávislé referenční jádro (ideálně s možností portu do C++), které by mohl tým LightBurnu případně integrovat nativně. Není cílem psát nový editor ani nahradit LightBurn.

## 2. Ověřené skutečnosti a neověřené předpoklady

| Zjištění | Stav | Dopad |
|---|---|---|
| LightBurn Grid Array duplikuje objekty do řad a sloupců | Ověřeno v dokumentaci | Neřeší tento požadavek |
| Quick Nest je optimalizační rozmístění do plochy | Ověřeno | Nezaručuje požadovaný počet sloupců a pořadí |
| Veřejně popsané příklady `.lbrn2` používají hierarchii `Shape`, včetně `Group`, a transformační položky `XForm`; aktuální soubory nutno ověřit | Doloženo veřejně popsaným příkladem (2021) | Východisko pro prototyp; **současnou verzi ověřit na vlastních souborech** |
| `XForm` tvoří šest parametrů afinní matice; skupinová transformace se uplatní na potomky | Doloženo veřejným příkladem | Při čistém posunu lze zpravidla zachovat vnitřní geometrii |
| LightBurn REST API má veřejné endpointy pro stav, metadata, vrstvy, řezací parametry a import/otevření souborů | Ověřeno v oficiálním API | Volitelně lze později otevřít výsledný soubor |
| REST API má endpoint pro získání označených objektů a jejich jednotlivý přesun | **Nepotvrzeno; ve veřejném API chybí** | Na přímou úpravu výběru v otevřeném projektu nelze spoléhat |
| Výběr objektů v otevřeném LightBurnu se po uložení projeví jako jednoznačný seznam vybraných skupin | **Neověřeno** | První verze musí mít vlastní výběr položek |
| Libovolný `.lbrn2` z aktuální verze půjde bezpečně zapsat naším nástrojem | **Neověřeno** | Zavést úzký rozsah podporovaných projektů, version gate a round-trip testy |

Zdrojové materiály jsou na konci dokumentu. Všechny technické závěry o zápisu souborů jsou zatím hypotézy k testování, ne garance.

## 3. Hranice první verze aplikace — MVP

**MVP není pouze matematická ukázka.** Před označením za dokončenou první použitelnou verzi musí mít možnost výběru a ručního seřazení skupin, kontrolu materiálu i kolizí a bezpečné uložení. Předběžný laboratorní prototyp může tyto části dočasně postrádat, ale není splněným MVP.

### 3.1 Závazný rozsah MVP

- **MVP-01 Přesná mřížka:** načíst podporovaný místní `.lbrn2`; rozmístit právě jednou každou vybranou, již existující skupinu; nastavit počet sloupců, mezeru X/Y (mm), počátek mřížky a zobrazit výsledné rozměry.
- **MVP-02 Výběr skupin:** zobrazit identifikovatelné nejvyšší skupiny, jejich rozměry a stav, umožnit uživateli vybrat jen některé z nich; nevybrané prvky nikdy nepřesunovat.
- **MVP-03 Ruční pořadí:** zobrazit číslovaný seznam vybraných skupin, měnit pořadí pomocí ovládání Nahoru/Dolů (drag-and-drop navíc volitelně), vrátit výchozí pořadí. Výpočet musí použít právě zobrazené pořadí.
- **MVP-04 Materiál a kolize:** umožnit nastavit obdélník materiálu v souřadnicích projektu a bezpečnostní okraje; ověřit, že veškeré cílové výrobky leží v použitelné ploše, nekolidují mezi sebou **ani s ponechanými objekty**. Nevyhodnotitelné překážky vedou k blokaci výstupu, nikoli k tichému souhlasu.
- **MVP-05 Bezpečné uložení a validace:** zapsat pouze nové `.lbrn2`, provést diff s pravidlem pouze povolených translací vybraných skupin; kontrola verze projektu, identity a nastavení; podle nastavení vytvořit auditní protokol (kap. 9.4) a místo nebezpečného výstupu vrátit chybu.
- **MVP-06 Obsluha:** offline Windows aplikace `.exe` s PySide6/Qt; volba projektu, výběr a pořadí výrobků, parametry, kontrolní náhled a export; není nutné instalovat Python.
- **MVP-07 Jazyk rozhraní:** od prvního interního použitelného MVP úplná **čeština (`cs`) a angličtina (`en`)** a připravená lokalizační architektura; **před prvním veřejným stabilním vydáním v1.0.0** navíc povinně **němčina (`de`), slovenština (`sk`), polština (`pl`), francouzština (`fr`), španělština (`es`) a italština (`it`)** — celkem osm jazyků. Volba `Automaticky (dle systému)` nebo konkrétního jazyka, zapamatování volby a bezpečný fallback do angličtiny. Povinné jsou i chyby a bezpečnostní varování. Viz kap. 36; veřejné vydání navíc podléhá bráně `L10N-PUBLIC-01`.

- **MVP-08 Vestavěná nápověda a uživatelská dokumentace:** dostupná offline přes `F1` a `Nápověda → Uživatelská příručka`, nejprve kompletně `cs/en`, pro veřejné vydání všech osm jazyků, se shodou s implementovaným stavem; specifikace v kap. 38.

**Omezení podporovaných geometrií:** první verze vyžaduje samostatné nejvyšší `Group` s jednoznačným vnějším uzavřeným řezným obrysem, uvnitř kterého leží veškerý ostatní obsah skupiny; rozměr výrobku je AABB tohoto obrysu (kap. 5). Výrobky ve skupině mohou mít různé rozměry; mřížka je adaptivní (kap. 7.3). Pokud požadovaný projekt nesplňuje podmínky, zobrazit konkrétní důvod a neprovést export. Původní objekt nesmí být měněn mimo translaci; podrobné podmínky v kap. 5, 8–9.

### 3.2 Výslovně mimo MVP

- Formát `.lbrn`, převody `.lbrn` ↔ `.lbrn2`, export do staršího formátu a automatický fallback na jiný projektový formát. Platí také po MVP, dokud nebude schválená změna zadání.

- Násobení jednotlivých variant v různých množstvích, automatický výběr počtu řad/sloupců a ukládání uživatelských profilů (verze aplikace 1.1).
- Rozdělení zakázky na více desek a kombinování výrobků z více `.lbrn2` (verze aplikace 2.0).
- Přímý výběr či přesun objektů v otevřeném LightBurnu (pouze výhled, závislý na veřejném API).
- Řízení laseru, generování strojových souborů, pokročilý nesting libovolných obrysů, rotace kvůli úspoře materiálu, sdílené řezy a automatické opravy vadného projektu.
- Neověřené verze souborového formátu a nejednoznačné, zamčené nebo jinak nepodporované skupiny.

### 3.3 Bezpečný způsob použití

Před spuštěním uživatel uloží projekt v LightBurnu. Po vytvoření nového souboru jej otevře přes **Open**, zkontroluje vrstvy, Preview a polohu na stroji. Kontrola materiálu v naší aplikaci **nenahrazuje** kontrolu skutečné pracovní plochy, nájezdu a přesahů při gravírování.

## 4. Důležité definice

- **Výrobek (item):** jedna nejvyšší skupina LightBurnu, obsahující řezný obrys i všechny její vnitřní motivy/texty.
- **Obrys výrobku:** jedna ověřená uzavřená řezná geometrie uvnitř skupiny, která obsahuje veškerý ostatní obsah skupiny (např. obdélník, zaoblený obdélník, libovolný uzavřený tvar); výrobní rozměry a pozici určuje její AABB. Ostatní obsah skupiny (texty, motivy) rozměr výrobku neurčuje.
- **Bounding box / AABB:** nejmenší osově rovnoběžný obdélník obklopující obrys **po všech transformacích**.
- **Mezera:** vzdálenost mezi výrobními obrysy (nikoli mezi středovými body, nikoli rozteč gravírovacích textů).
- **Pořadí:** explicitní uspořádaný seznam identifikátorů výrobků. **Document order** je dostupný fallback, ale před uložením musí být zřejmý.
- **Přesun:** výhradně změna translace položky `XForm` nejvyšší skupiny; vnořené objekty zůstávají nedotčené.
- **Source project:** původní soubor na disku, který nástroj nikdy neupravuje.

## 5. Pravidla pro rozpoznání výrobků

**MVP – režim `strict_rectangular_group`:**

1. Skupina musí být nejvyšším samostatným přesouvaným objektem projektu; nevybírat zároveň ji i jejího potomka.
2. Musí obsahovat přesně jeden jednoznačně určený **vnější uzavřený obrys** (rozhodnutí 16. 10. 2026 po KAL-00, nahrazuje omezení v1.8 na `Rect`/čtyřúhelník):
   - typ `Rect`, `Ellipse` nebo uzavřená `Path` (`PrimList="LineClosed"`, nebo seznam primitiv, jehož konec navazuje na začátek); úseky mohou být přímé i Bézierovy;
   - AABB obrysu (po všech transformacích, u Bézierových úseků přesně podle extrémů křivky, nikoli jen vrcholů) **obsahuje AABB veškerého ostatního obsahu skupiny** v toleranci `epsilon`, včetně textů měřených přes `BackupPath`;
   - je jediný takový kandidát; pokud je jich více, zvolí se ten s největší plochou AABB a ostatní musí ležet uvnitř; jinak skupinu odmítnout a požádat o ruční volbu;
   - řezná vrstva obrysu se zobrazí u výrobku; mají-li vybrané výrobky obrys na různých vrstvách, zobrazit varování.
   Rozměr a poloha výrobku = AABB obrysu. U neobdélníkových obrysů (např. zaoblené rohy) je skutečná vzdálenost obrysů v rozích **větší nebo rovna** zadané mezeře, nikdy menší; GUI to uvede.
3. Vnější obrys musí být ve výsledném souřadném systému osově zarovnaný; pro počáteční prototyp není dovolena rotace ani smyk obrysů. Případné transformace celého obrázku musí být detekovány a validovány.
4. Každá skupina je uzamčena ve svém vnitřním uspořádání (bez úpravy vnitřních tvarů).
5. Obsah mimo tento obrys: geometrii s **ověřitelnými** hranicemi (cesty, `Rect`, `Ellipse`, bitmapy se známým rozměrem), která přesahuje obrys, skupinu **odmítnout** — mohla by narušit bezpečný odstup. Obsah, jehož hranice nelze spolehlivě spočítat (např. `Text` bez `BackupPath`), **neblokuje**, ale vyvolá viditelné **varování** u výrobku a připomenutí kontroly v LightBurn Preview (rozhodnutí 16. 10. 2026). KAL-00 prokázal, že LightBurn 2.2 ukládá u textu `HasBackupPath="1"` a úplnou geometrii v `BackupPath` → pro takové texty se použije ověřitelná kontrola.
6. Zamčené skupiny, nevysvětlené odkazy a neznámé vlastnosti, které by se mohly změnit přesunem, odmítnout.
7. Neseskupené výrobky neidentifikovat heuristikou; nabídnout uživateli jejich seskupení v LightBurnu.
8. **Nativní tvary LightBurnu** (v1.14, ověřeno na vzorcích C a branou KAL-02, `docs/FORMAT_COMPATIBILITY.md`): `Ellipse` (`Rx`, `Ry`), `Rect` (`W`, `H`, `Cr` = poloměr rohu v mm, nejvýš polovina kratší strany) a `Polygon` (`Rx`, `Ry`, `N`; vrcholy v úhlech `90° + 180°/N + k·360°/N` na elipse Rx, Ry) nemají seznam vrcholů; posun v `XForm` je střed tvaru. Jsou uzavřené, mohou být obrysem i vnitřním obsahem (např. otvor klíčenky) a mohou ležet ve vnořených skupinách. AABB se počítá přesně (elipsa analyticky, mnohoúhelník z vrcholů, zaoblený obdélník z vnitřního obdélníku a elipsy rohu); pro náhled a natočení se tvar převede na ekvivalentní cestu, shodnou s Convert to Path v LightBurnu. Neznámé atributy či prvky tvaru a nečitelné rozměry výrobek blokují.
9. Za vrcholem ve `VertList` může stát příznak `S` (hladký uzel); geometrii nemění. Jiné neznámé znaky → nečitelná křivka.

**Výrobní zásada:** pokud nelze hranici výrobku spolehlivě vypočítat, nástroj nesmí předstírat přesnost ani tiše použít hranici textu. V budoucnu přidat další „bounding strategie“ (libovolná uzavřená cesta, explicitní reference, úplný vizuální obrys).

## 6. Výběr a pořadí výrobků — povinné již v MVP

Samotná geometrie neurčuje požadované výrobní pořadí. Uložení pořadí v XML navíc nemusí odpovídat poloze kartiček v náhledu.

1. Po načtení zobrazit seznam všech nalezených podporovaných kořenových skupin (`source_order`, uživatelský název, rozměry, stav kompatibility). Skupiny se nesmějí automaticky označit jen proto, že leží vedle sebe.
2. Výběr musí být explicitní: zaškrtávací seznam nebo obdobný ovládací prvek. Nulový výběr blokuje výpočet a uložení.
3. První výchozí pořadí je `document_order`; pro uživatele se zobrazí jednoznačné číslování. V MVP musí fungovat **ruční přesun v seznamu Nahoru/Dolů** včetně opakovaných operací, odznačení a znovuoznačení; přetažení myší je vhodná, nikoli povinná alternativa.
4. Při každé změně výběru nebo pořadí okamžitě přepočítat náhled a validaci. V nevybraných skupinách neměnit ani `XForm`, ani pořadí ve zdrojovém XML.
5. Výpočet dostane `ordered_item_ids`, které musí tvořit **přesně permutaci** `selected_item_ids` bez duplicit. Pokud se položka ztratí, duplikuje nebo je nepodporovaná, výpočet skončí chybou.
6. Třídění podle vizuální polohy, názvu, textu nebo data lze přidat později; pokud bude dostupné, vždy nabídne obnovení ručního pořadí.
7. Položky se rozmísťují po řádcích shora dolů, **od rohu počátku laseru** (rozhodnutí 16. 10. 2026, v1.10): u laseru s počátkem vpravo nahoře je 1. výrobek vpravo nahoře a řádky se plní doleva; u počátku vlevo nahoře zleva doprava. Alternativní volba „čtení“ plní vždy zleva doprava. Poslední neúplný řádek začíná u strany počátku (resp. vlevo při „čtení“); nevznikají žádné nové objekty ani prázdné kopie. Menší výrobek v adaptivní buňce přiléhá ke straně počátku.

**MVP: výběr + ruční přeřazení nejsou volitelné rozšíření.** Přesná funkční pravidla a testy jsou v kap. 21 (MVP-02/03).

## 7. Rozmisťovací algoritmus

### 7.1 Model vstupů

Pro každý výrobek je znám `id`, jeho hranice `[minX, minY, maxX, maxY]`, rozměry `w`, `h` a přesunovatelný odkaz na nejvyšší skupinu. Veškeré jednotky **mm**.

**Souřadný systém jádra (rozhodnutí 16. 10. 2026):** `GridEngine` pracuje výhradně v abstraktním „obrazovkovém“ systému: osa X doprava, **osa Y dolů**, `min_y` = horní hrana, řádky se plní shora dolů. Soubory `.lbrn2` mohou ukládat souřadnice s osou Y nahoru a projekt může mít zrcadlení či jiný počátek; převod mezi souřadnicemi souboru a souřadnicemi jádra provádí **výhradně adaptér** podle výsledku kalibrace KAL-00 (kap. 8). Jádro o LightBurnu ani o orientaci souboru nic neví.

Parametry: `columns` (1–N), `gap_x >= 0`, `gap_y >= 0`, `start_x`, `start_y`, `order[]`, `horizontal_alignment`, `vertical_alignment`.

### 7.2 Režim A – všechny výrobky stejných rozměrů (priorita MVP)

Pro výrobky o šířce `W` a výšce `H`:

- `row = index // columns`
- `col = index % columns`
- `target_left = start_x + col × (W + gap_x)`
- `target_top = start_y + row × (H + gap_y)`
- `delta_x = target_left − old_bounds.min_x`
- `delta_y = target_top − old_bounds.min_y`

Počet řad `R = ceil(N / C)`. Celková šířka `C×W + (C−1)×gapX`, výška `R×H + (R−1)×gapY`. Při `N < C` použít pro šířku skutečný počet obsazených sloupců nebo v UI jasně označit rezervované prázdné buňky. V MVP: šířka se počítá podle skutečně obsazených sloupců.

**Konkrétní ověřovací příklad:** N = 10, `W=100`, `H=60`, `C=5`, `gapX=3`, `gapY=3`, `start=(10,20)`:

- Levé hrany sloupců: `10, 113, 216, 319, 422 mm`.
- Horní hrany řádků: `20, 83 mm`.
- Vnější rozměr mřížky: `512 × 123 mm`.
- Spodní pravý roh: `(522,143) mm`.
- Počet položek po aplikaci = **10**, nikoli 20.

### 7.3 Režim B – různé rozměry (povinně v MVP, adaptivní mřížka — rozhodnutí 16. 10. 2026)

Režim A je zvláštním případem režimu B (všechny šířky i výšky shodné); implementuje se jediný algoritmus dle pseudokódu 7.5, který pro shodné rozměry dává přesně výsledky kap. 7.2. Režim pevné buňky podle největšího výrobku se v MVP neimplementuje.

Pro každý sloupec `j` vypočítat `columnWidth[j] = max(width položek ve sloupci j)`; pro řádek `r` vypočítat `rowHeight[r] = max(height položek v řádku r)`.

Začátky buněk se počítají kumulativně: `columnStart[j] = start_x + Σ_{k<j}(columnWidth[k]+gapX)`; obdobně pro řádky.

Položku lze zarovnat na levý horní roh buňky, nebo vystředit. Vystředění: `itemX = columnStart[j] + (columnWidth[j]−itemWidth)/2`, obdobně pro Y.

**Důležitá přesnost formulace:** Při různých rozměrech a společně zarovnaných sloupcích/řádcích nelze obecně zaručit přesně stejnou mezeru mezi každou dvojicí sousedních výrobků; algoritmus garantuje **minimální požadovanou mezeru**, nikoli všude přesně stejné číslo. V GUI to nesmí být označeno jako „přesná mezera“ bez vysvětlení.

### 7.4 Numerika

- Výpočty v `float64` v mm, žádná aproximace celými pixely.
- Serializace `XForm` s dostatečnou přesností (doporučené až 6 desetinných míst; nejdříve ověřit kompatibilitu), používat desetinnou tečku.
- Geometrická validační tolerance `epsilon=0,001 mm` pro laboratorní porovnání; pravidla pro zaokrouhlení zdokumentovat.
- Výsledek musí být deterministický: stejný vstup + stejné parametry = stejné polohy.
- Opakované použití na již poskládaný projekt musí být idempotentní v rámci definované tolerance.
- Nula skupin, záporná mezera, počet sloupců `<=0`, `NaN`, nekonečno nebo deformovaná data = chyba před zápisem.

### 7.5 Pseudokód výpočetního jádra

```python
def arrange_to_grid(items, request):
    validate_items_and_request(items, request)
    ordered = apply_explicit_order(items, request.order)
    cols = min(request.columns, len(ordered))
    rows = ceil(len(ordered) / cols)

    column_widths = [max_width_in_column(ordered, j, cols) for j in range(cols)]
    row_heights = [max_height_in_row(ordered, r, cols) for r in range(rows)]
    xs = cumulative_positions(request.start_x, column_widths, request.gap_x)
    ys = cumulative_positions(request.start_y, row_heights, request.gap_y)

    result = []
    for i, item in enumerate(ordered):
        r, c = divmod(i, cols)
        target_x = xs[c] + alignment_offset(column_widths[c], item.width,
                                             request.horizontal_alignment)
        target_y = ys[r] + alignment_offset(row_heights[r], item.height,
                                             request.vertical_alignment)
        result.append(Placement(item.id,
                                dx=target_x - item.bounds.min_x,
                                dy=target_y - item.bounds.min_y))
    assert_no_bounding_box_overlaps(ordered, result, request)
    return Layout(result, compute_total_bounds(ordered, result))
```

Tento algoritmus nesmí importovat žádnou knihovnu LightBurnu ani upravovat soubory; vstup i výstup jsou čistá data.

### 7.6 Natočení pro úsporu materiálu (v1.13, ADR-0005)

- **Režimy** (společná volba v sekci Mřížka, uložená v nastavení): *Libovolný úhel (nejmenší plocha)* — **výchozí** (rozhodnutí vlastníka 2026-10-17), *Po 90°*, *Nenatáčet*. Jednotlivé výrobky lze z natáčení vyjmout (výjimky v seznamu).
- **Úhel výrobku:** nejmenší osový obdélník kolem konvexního obalu všech křivek výrobku (obrys, motivy, `BackupPath` textů; Bézierovy úseky rozvinuté s odchylkou ≤ 0,002 mm, obdélník o tuto odchylku zvětšen). Natočit jen při úspoře plochy obdélníku ≥ 0,5 %. Úhel v (−45°, 45°].
- **Společná orientace:** vyzkoušet „nenatáčet nic“, „beze změny“ (nejmenší obdélník každého výrobku), „vše na šířku“, „vše na výšku“ (o 90° navíc menším celkovým úhlem); vybrat variantu, která se vejde na využitelnou plochu desky, z nich s nejmenší plochou mřížky; jiná než „nenatáčet nic“ jen při úspoře ≥ 0,5 % (v1.14: natočení se nepoužije, když by mřížka nevyšla menší). Výrobky se čtvercovým obdélníkem (rozdíl stran ≤ 0,01 mm, např. kruhové klíčenky) se o 90° navíc neotáčí. V režimu *Po 90°* je výchozí úhel 0.
- **Hezký úhel (v1.14):** u oblých tvarů je minimum ploché a hrany rozvinuté křivky dají např. 29,6° místo 30°; úhel se proto zaokrouhlí na celé stupně, půlstupně nebo desetiny, pokud obdélník naroste nejvýš o 0,01 %.
- **Ruční úhel (v1.15, přání vlastníka):** výrobky lze vybrat kliknutím v náhledu (Ctrl+klik přidá / odebere, Esc výběr zruší; výběr se zvýrazní a je propojený se seznamem) nebo v seznamu; vybraným lze zadat úhel ve stupních (kladně po směru hodin, od polohy v původním projektu), otočit o ±90° nebo ruční úhel zrušit (*Automaticky*). *Nenatáčet* = ruční úhel 0. Ruční úhel má přednost před automatikou i před volbou společné orientace, platí i v režimu *Nenatáčet*, normalizuje se do (−180°, 180°], neplatný úhel → `invalid_rotation`. V seznamu je označen „(ručně)“, v protokolu `rotation_manual`. Ruční úhly platí do otevření jiného projektu. CLI `--angle ID=DEG`. Kliknutí bez posunu myši (< 4 px) = výběr; tažení dál prohazuje výrobky.
- **Střed natočení** = střed obrysu v původní poloze; potom posun do mřížky. Transformace jádra `T` → soubor `S ∘ T ∘ S`, `S = diag(±1, ±1)` podle `MirrorX/MirrorY` (kap. 8). Násobky 90° zapisovat s přesnými 0/±1.
- **Zápis a invarianty:** mění se jen `XForm` nejvyšší skupiny a `BackupPath` textů v ní: `XForm' = T ∘ XForm` (rozšíření pravidla „pouze translace“ z MVP; bez natočení zůstává čistý posun s bajtově nezměněnou lineární částí). Nezávislá kontrola ověří celou matici; po znovunačtení výstupu musí skutečné křivky natočeného výrobku ležet v cílovém obdélníku.
- **Ověření:** brána KAL-01 — kalibrační soubory s natočením otevřené v LightBurnu (texty, Preview, srovnání výstupem aplikace) pro oba typy laseru — **splněno 2026-10-17** (`docs/FORMAT_COMPATIBILITY.md`).

## 8. Přesun přes `XForm` ve formátu LightBurnu

Ve veřejném příkladu má transformace šest parametrů:

```xml
<XForm>a b c d e f</XForm>
```

Matematická reprezentace (sloupcové vektory):

```text
| x' |   | a  c  e | | x |
| y' | = | b  d  f | | y |
| 1  |   | 0  0  1 | | 1 |
```

**Pro nejvyšší skupinu v souřadnicích projektu** a čistou translaci `(dx,dy)` se při nepřítomnosti další rodičovské transformace očekává:

```text
původní: a b c d e f
nové:    a b c d (e+dx) (f+dy)
```

Tím se nezmění rotace, měřítko, smyk ani lokální údaje jednotlivých potomků. Pokud je však nad skupinou další transformace, požadovaný posun v globálních souřadnicích **není** obecně roven jednoduchému přičtení k `e,f`; musí se přepočítat do souřadnic rodiče. Matematicky `Δlocal = inv(Aparent) × Δworld` pro lineární část rodičovské transformace. Proto MVP podporuje pouze ověřené nejvyšší skupiny.

Další zásadní riziko: parametry projektu `MirrorX`, `MirrorY` a nastavení počátku mohou ovlivnit vztah mezi uloženými souřadnicemi a vizuálním směrem v LightBurnu. Přepočet zobrazené mřížky do souřadnic souboru **nesmíme natvrdo odhadnout**. V etapě 0 vytvořit kalibrační test se dvěma obdélníky, jedním posunem vpravo a jedním dolů, a ověřit chování v aktuální verzi LightBurnu.

**Výsledek kalibrace KAL-00 (16. 10. 2026, LightBurn 2.2.00):** souřadnice v souboru jsou souřadnice stroje a shodují se s hodnotami X/Y v UI LightBurnu. Příznaky `MirrorX`/`MirrorY` v hlavičce určují **jen zobrazení**: přepnutí zařízení v LightBurnu změní příznak, ale žádnou souřadnici v souboru. Převod do souřadnic jádra (osa X doprava, osa Y dolů):

```text
screen_x = −x_souboru  když MirrorX="True",   jinak  +x_souboru
screen_y = +y_souboru  když MirrorY="True",   jinak  −y_souboru
```

Ověřené kombinace: `MirrorX=True, MirrorY=True` (počátek vpravo nahoře) a `MirrorX=False, MirrorY=True` (počátek vlevo nahoře). Ostatní kombinace (`MirrorY=False`) jsou v MVP **nepodporované** a projekt se odmítne s vysvětlením, dokud nebudou ověřeny stejným kalibračním párem. Adaptér převádí posuny zpět: `dx_souboru = −dx_screen` při `MirrorX=True`, jinak `+dx_screen`; `dy_souboru = +dy_screen` při `MirrorY=True`, jinak `−dy_screen`.

**Poznámka:** Ukázka formátu vychází z veřejné diskuse z roku 2021, nikoli z garantovaného veřejného schématu pro rok 2026. Podpora konkrétního `AppVersion` a `FormatVersion` je předmětem ověřovacího testu.

## 9. Čtení a bezpečný zápis projektu

### 9.1 Načtení

1. Otevřít výhradně uživatelem zvolený soubor.
2. Ověřit příponu, limit velikosti, syntaxi XML, kořen projektu, hlavičku verze a očekávané prvky.
3. XML parser nastavit bezpečně: žádné externí entity, žádné síťové požadavky, DTD zakázat, nepokoušet se „opravovat“ poškozený dokument.
4. Zapsat SHA-256 původního souboru a spočítat počty všech objektů/skupin/řezných nastavení.
4a. **Laser a počátek (MVP, rozhodnutí 16. 10. 2026):** z hlavičky načíst `DeviceName`, `MirrorX`, `MirrorY` a odvodit počátek: True/True = vpravo nahoře, False/True = vlevo nahoře (ověřeno), False/False = vlevo dole, True/False = vpravo dole (od v1.22 podporováno se stejným převodem — osa Y souboru nahoru; ověřeno KAL-04; kap. 8). Uživatel počátek **nezadává**. GUI trvale zobrazí „Projekt uložen pro: {DeviceName}, počátek {roh}“ a upozorní, že po přepnutí laseru v LightBurnu je nutné projekt znovu uložit. Velikost pracovní plochy laseru v souboru není; materiál se zadává ručně (profily ve v1.1).
4b. **Cílový laser (v1.23):** uživatel může zvolit jiný laser z katalogu (Nastavení → Lasery). Výstup pak dostane v hlavičce `DeviceName`/`MirrorX`/`MirrorY` cílového laseru a každý výrobek transformaci `S_cíl ∘ T ∘ S_zdroj` (`S = diag(±1, ±1)` podle orientace), takže na cílovém laseru vypadá stejně jako na původním (podle V-003 přepnutí zařízení mění jen zobrazení, ne souřadnice — bez převrácení by se řezalo zrcadlově). Deska, roh plnění a ruční roh se řídí cílovým laserem. Liší-li se orientace, musí být vybrány všechny výrobky a projekt nesmí obsahovat volné ani nepodporované objekty (jinak `convert_needs_whole_project`). Nastavení vrstev (výkon, rychlost) se nepřevádí — GUI upozorní. Název výstupu `puvodni__Nazev_laseru__grid_NNN.lbrn2`.
5. Načíst hierarchii skupin a zjistit, které lze bezpečně přesunout.
6. Nepodporované či nejednoznačné struktury označit; při riziku ukončit bez výstupního projektu.

### 9.2 Zápis

**Tato původní kapitola specifikuje zápis pro MVP s přesuny bez kopírování.** Pro v1.1 s množstvími a v2.0 platí navíc rozšířená pravidla verzovaných invariancí a exportu v kap. 22–25.

**Povinná doprovodná změna (KAL-00, 16. 10. 2026):** `XForm` uvnitř `BackupPath` u textů je uložen ve **světových souřadnicích** (`XForm(BackupPath) = XForm(skupina) ∘ XForm(text)`). LightBurn jej při přesunu skupiny posouvá o stejný vektor. Náš zápis proto u přesouvané skupiny mění translaci `XForm` skupiny **a** translaci `XForm` každého `Text/BackupPath` v jejím podstromu o stejné `(dx, dy)`. Před zápisem ověřit, že `XForm(BackupPath) ≈ XForm(skupina) ∘ XForm(text)` v toleranci; při nesouladu skupinu odmítnout.

**Formát čísel:** zapisovat jako `format(v, '.8g')` (8 platných číslic, desetinná tečka), stejně jako LightBurn 2.2.

**Povolená výjimka (rozhodnutí 16. 10. 2026):** případný uložený náhledový obrázek projektu (thumbnail) se neaktualizuje a po přesunu nemusí odpovídat obsahu; validátor jej porovnává jako nezměněný. Vlastní náhled si LightBurn obnoví při dalším uložení.

Preferovat **minimální úpravu** konkrétních textových obsahů `XForm` ověřených nejvyšších skupin. **Doporučená technika:** při čtení použít streamový parser `xml.parsers.expat` (standardní knihovna), který poskytuje bajtovou pozici každého prvku (`CurrentByteIndex`); z ní určit přesný bajtový rozsah textového obsahu cílového `XForm` (resp. atributu) a ve výstupní kopii nahradit pouze tento rozsah. Všechny ostatní bajty souboru zůstanou identické, což zjednoduší diff (kap. 9.3) na porovnání „vše kromě seznamu povolených úseků je bajtově shodné“. Ověřit v KAL-00, zda transformace skupiny je uložena jako prvek nebo atribut. Nerozbalovat a neexportovat vnitřní geometrie, nepřevádět fonty ani bitmapy. Ostatní části souboru by měly zůstat obsahově shodné.

První laboratorní provedení může použít XML knihovnu pro parsování a serializaci, pokud round-trip testy jednoznačně ověří, že nezměnila význam jiných prvků. Pro důvěryhodnější výrobní provedení se doporučuje cílené přepsání původního textového úseku odpovídajícího `XForm` (se strukturálním ověřením), bez reserializace celého XML. Pouhé nahrazování řetězců regulárním výrazem bez kontextu skupiny není přijatelné.

### 9.3 Kontrola před potvrzením

- Vstupní zdrojový soubor stále odpovídá načtenému SHA-256.
- V MVP počet skupin, objektů, cest, obrázků, textů a řezných nastavení souhlasí; ve v1.1/2.0 musí počet objektů přesně odpovídat schválenému plánu instancí dle kap. 25.
- Všechny referenční `CutIndex` a nastavení `CutSetting` zůstávají stejné.
- V MVP obsah každého přesouvaného objektu je zachován, pouze očekávaná translace příslušné skupiny se změnila; u nových kopií nebo sloučených zdrojů se ověřuje i mapování zdrojů, referencí a identit.
- Žádná neselektovaná skupina ani jiný objekt nebyl upraven.
- Nově vypočtené obrysy odpovídají plánovaným cílovým pozicím.
- Výstup je znovu čitelný stejným parserem.
- Volitelně, je-li dostupný, porovnat strojově čitelný souhrn nastavení před/po.

### 9.4 Zápis na disk

- Originál nikdy nepřepisovat; dočasný soubor vytvořit v cílové složce.
- Výstup má nové jedinečné jméno; jako návrh se nabízí `puvodni__grid_001.lbrn2` (další výstupy `_002`, …) ve složce originálu. **Od v1.12 může uživatel v dialogu uložení změnit složku i název** (přípona `.lbrn2` se doplní). Zvolený cíl nesmí být originál ani existující soubor a nesmí existovat ani jeho protokol `<název>.json`; jinak aplikace nic nezapíše a vyžádá jiný název (žádné potvrzení přepsání).
- Po úspěšné validaci provést atomické přejmenování do cílové cesty; nikdy nepřepsat existující soubor. Implementační poznámka: na Windows použít `os.rename` (při existujícím cíli selže výjimkou `FileExistsError`), **nikoli `os.replace`**, který existující soubor přepíše.
- Při výjimce odstranit jen dočasný soubor a zachovat původní data.
- **Protokol uložení** (`.json`: zdroj a jeho SHA-256, výstup a jeho SHA-256, laser, parametry, posuny, výsledek kontroly) je od v1.12 **volitelný** podle nastavení uživatele: *neukládat* (výchozí, rozhodnutí vlastníka), *vedle výstupu* (`<název>.json`), *do složky protokolů aplikace* v profilu uživatele. Protokol nikdy nepřepíše existující soubor. Vývojářská CLI jej ukládá vedle výstupu.
- Pokud je zdroj otevřený a obsahuje neuložené změny v LightBurnu, nástroj je **nemůže poznat**; uživatel musí před načtením použít Save As a načíst výslednou kopii.

### 9.5 Proč nepoužít prostý export/import SVG

SVG by bylo snadné na přesun grafiky, ale při převodu by mohlo dojít ke ztrátě nastavení řezacích vrstev, částí textové editovatelnosti a dalších interních informací. LightBurn sám uvádí, že **Import `.lbrn2` načítá jen grafiku, zatímco Open načítá také projektová nastavení**. Proto validovat výsledek pomocí **Open**, nikoli pouhého Import. Odeslání výsledného projektu přes veřejné API `POST /api/file/open` je pozdější *volitelná* integrace vyžadující zvláštní potvrzení uživatele; nahrazuje otevřený projekt, tudíž se nemá spouštět automaticky.

**Po uložení (v1.19, přání vlastníka):** aplikace dál pracuje s **otevřeným originálem** (každé uložení vytvoří další variantu); titulek okna a sekce Projekt ukazují „naposledy uloženo jako …“. Hlášení o uložení nabízí volbu *Pokračovat v aplikaci s uloženým souborem* — uložený výstup se otevře místo originálu (jako „Uložit jako“; kopie a natočení jsou v něm napevno, historie kroků začíná znovu). Návrh názvu z již uloženého výstupu `puvodni__grid_NNN` pokračuje v řadě originálu (`puvodni__grid_002`), přípona se nezdvojuje.

**Otevřít v LightBurnu (v1.18, přání vlastníka):** po uložení tlačítko v hlášení, ikona a Soubor → Otevřít uložený projekt v LightBurnu (Ctrl+L) otevřou **uložený výstup** programem přiřazeným k `.lbrn2` (jako dvojklik v Průzkumníku) — bez párování a bez REST API. Ověřeno vlastníkem: běžící LightBurn otevře soubor místo aktuálního projektu (File → Open) a na neuložené změny se zeptá sám; do nového okna to nejde (ani REST API takovou funkci nemá). Spouští se jen kliknutím uživatele, nikdy automaticky; úlohu na laser nikdy neodesílá. REST API (párování, kontrola `modified` předem) zůstává možným rozšířením.

## 10. Koncept interního datového modelu

```text
ProjectInfo
  source_path, source_sha256, app_version, format_version
  project_units, orientation, workspace_width, workspace_height
  original_object_counts, cut_settings_digest

Item
  id (interní, stabilní jen v rámci vstupního souboru)
  source_group_path / XPath or equivalent reference
  source_order
  label
  outline_bounds_mm = (left, top, right, bottom)
  current_group_transform = (a, b, c, d, e, f)
  warnings[]

GridRequest
  selected_item_ids[]
  ordered_item_ids[]
  columns
  gap_x_mm, gap_y_mm
  anchor_x_mm, anchor_y_mm
  alignment_x (left|center|right)
  alignment_y (top|center|bottom)
  workspace_check (warn|strict)

Placement
  item_id
  old_bounds
  target_bounds
  delta_x_mm, delta_y_mm
  source_xform, target_xform

LayoutResult
  placements[]
  grid_bounds
  warnings[]
  validation_report
```

Rozhraní `GridEngine` musí fungovat i nad umělými obdélníky bez jakékoliv závislosti na LightBurnu.

## 11. Navržená architektura

```text
┌────────────────────────────────────────────────────┐
│                  Desktop UI / CLI                  │
│ výběr souboru, skupin, pořadí, parametry, náhled    │
└───────────────┬───────────────────────┬────────────┘
                │                       │
       ┌────────▼────────┐     ┌────────▼──────────┐
       │ LBRN2 Adapter   │     │ Grid Engine       │
       │ čtení/protokol  │────►│ čistá matematika  │
       │ zápis XForm     │◄────│ validace rozložení│
       └────────┬────────┘     └───────────────────┘
                │
       ┌────────▼────────┐
       │ Safety Validator│
       │ diff, kontrola  │
       │ vrstev, hash    │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │ nový .lbrn2    │
       │ + protokol      │
       └─────────────────┘
```

**Doporučený programovací jazyk:** Python 3.12+ pro rychlý prototyp, s čistými typovanými datovými třídami a testy. **Výpočetní jádro:** standardní knihovna, žádná GUI závislost. **XML:** nejprve standardní parser nebo pečlivě konfigurované `lxml`, ale zápis jen s validací. **Testy:** pytest. **Ovládání při vývoji:** nejprve malá příkazová řádka (CLI) pro testy a diagnostiku. **Cílové grafické rozhraní:** PySide6 (Qt), nikoli Tkinter nebo webová aplikace. **Lokalizace UI:** PySide6 `QTranslator`/`QLocale` a Qt Linguist (`.ts` zdroje, `.qm` v distribučním balíčku), s oddělením překladů od matematiky a `.lbrn2` adaptéru. **Distribuce:** 64bitová offline aplikace pro Windows 10/11 jako `.exe` (nejprve přenosná složka s EXE a potřebnými knihovnami; později případně jediný EXE nebo instalátor po ověření spolehlivosti balení). Způsob balení zvolit podle praktických testů, přednostně PyInstaller nebo `pyside6-deploy`. Před veřejnou distribucí ověřit licenční povinnosti PySide6/Qt a ostatních knihoven; žádná závislost na lokální instalaci Pythonu u uživatele.

Navržené členění:

```text
arrange-to-grid/
  README.md
  docs/
    specification.md
    FORMAT_COMPATIBILITY.md
    TEST_PLAN.md
  src/grid_arranger/
    domain/models.py
    core/layout.py
    core/validate.py
    adapters/lbrn2_reader.py
    adapters/lbrn2_writer.py
    adapters/geometry.py
    safety/diff.py
    safety/project_checks.py
    cli.py
    gui.py               # až později
    i18n/                 # translatable UI texty a kontrola překladů
    settings/             # lokální preferovaný jazyk a uživatelská nastavení
  translations/
    gridarranger_cs.ts    # české překlady, verzované v Git
    gridarranger_en.ts    # povinné: anglické tvary množného čísla (Qt numerus), viz kap. 36.1
  tests/
    unit/test_layout.py
    unit/test_transforms.py
    unit/test_ordering.py
    integration/test_roundtrip.py
    integration/test_lbrn2_fixtures.py
    fixtures/            # pouze vlastní testovací soubory
```

Závislosti směrem dovnitř: `UI -> adaptér -> domain/grid engine`, nikdy opačně. Adaptér nesmí diktovat datový model rozmisťovacímu jádru.

## 12. Uživatelské rozhraní — závazný cílový způsob použití, po ověření adaptéru

### 12.1 Forma aplikace a životní cyklus

- **Typ:** běžná **Windows desktopová aplikace (`.exe`)**, bez potřeby prohlížeče, serveru, registrace, cloudu a internetového připojení; grafické rozhraní v **PySide6/Qt**. **Interní MVP:** čeština a angličtina. **První veřejné vydání:** osm jazyků `cs/en/de/sk/pl/fr/es/it`; všechny přidatelné překladovými katalogy bez úprav výpočetního jádra (kap. 36).
- **Oddělení od LightBurnu:** v první verzi běží jako samostatný proces. Nenabízí položku v menu LightBurnu, nepřijímá aktuální výběr jeho objektů a nemění otevřený projekt za běhu.
- **Uživatel nepotřebuje Python ani příkazovou řádku.** CLI existuje jen jako vývojářská pomůcka a pro automatické testování.
- **Distribuce (v1.11):** hlavní podoba je **instalátor** `GridArranger-Setup-v<verze>-win-x64.exe` (instalace pro aktuálního uživatele bez práv správce, nabídka Start, odinstalace, nová verze se instaluje přes starou); záložní podoba je přenosný ZIP se složkou `GridArranger/`. Jednosouborové `.exe` se nepoužívá (rozbaluje se při každém spuštění, častější plané poplachy antiviru). Cílit na Windows 10/11 x64. Aktualizace viz kap. 32.
- **Jednotky (v1.12):** uživatel volí milimetry nebo palce (jako v LightBurnu); jde jen o zobrazení a zadávání, všechny výpočty, uložená nastavení a soubor `.lbrn2` jsou v mm, přepínání nesmí hodnoty posunout.
- **Bezpečnost:** zapisovat výhradně nový `.lbrn2`, nikdy originál. Nemanipulovat se strojem, negenerovat ani neposílat laserové úlohy.

### 12.2 Uživatelský průchod aplikací (happy path)

1. V LightBurnu **seskupit jednotlivé výrobky samostatně** a uložit aktuální projekt (`Save As`) na disk, aby byly zahrnuty všechny změny.
2. Spustit `GridArranger.exe`; při prvním spuštění se nastaví jazyk podle systému (nejbližší podporovaný jazyk `cs/en/de/sk/pl/fr/es/it`, u interního MVP pouze `cs/en`, jinak fallback do angličtiny). Uživatel může kdykoli přepnout jazyk v **Nastavení → Jazyk** (automaticky nebo konkrétní dostupný jazyk). Poté vybrat `.lbrn2` přes **Otevřít projekt** (alternativně později drag-and-drop souboru na okno).
3. Aplikace zobrazí nalezené nejvyšší skupiny. Uživatel vidí **číslovaný seznam, rozměr a případné varování**; ručně zaškrtne skupiny určené k přesunutí. Nejednoznačně rozpoznané skupiny nelze uložit, dokud nejsou vyřešeny.
4. Uživatel nastaví **počet sloupců**, **mezeru X/Y v mm**, **výchozí souřadnice**, **obdélník materiálu včetně okrajů** a **ručně upraví pořadí položek**. Výchozí mřížka zleva doprava a shora dolů, bez kopírování; žádná změna natočení.
5. Aplikace **v reálném čase aktualizuje náhled** přesných obrysových obdélníků (MVP nemusí vykreslovat vnitřní motivy), celkové rozměry mřížky, materiál a upozornění na přesahy/kolize mezi výrobky i vůči nepřesouvaným objektům.
6. Po úspěšné validaci uživatel vybere **Uložit nový projekt**. Dialog navrhne nový název `puvodni__grid_001.lbrn2`. Uložení ověří, že původní soubor nebyl změněn, a podle nastavení uloží protokol (kap. 9.4).
7. Uživatel výstup otevře v LightBurnu přes **File → Open** a před výrobou zkontroluje vrstvy, náhled dráhy (Preview) a polohu na stroji.

### 12.3 Uspořádání okna a interakce

Cílové jediné hlavní okno obsahuje nabídku **Nastavení → Jazyk** dostupnou i bez načteného projektu a skládá se z horního panelu projektu, **levého panelu s výběrem výrobků a nastavením mřížky**, **pravého panelu s přibližovatelným náhledem**, spodního stavového řádku s výslednými rozměry a tlačítka pro uložení. Náhled musí odpovídat skutečným souřadnicím; ilustrativní dlaždice nejsou dostatečná výrobní verifikace. Prvky GUI se během chyby zabarví/označí a zobrazí konkrétní vysvětlení. Tlačítko Uložit nový projekt zůstane neaktivní, dokud není projekt validní.

**Okno Nastavení (v1.20, přání vlastníka):** nastavení aplikace se nepřidávají do rozbalovacího menu, ale do modálního okna **Nastavení** (položka v liště menu, ikona ozubeného kola, Ctrl+,) se stránkami vlevo: *Obecné* (Jazyk, Vzhled, Jednotky, Panel rozložení), *Uložení* (Protokol uložení, Otevřít složku protokolů), *Aktualizace* (automatická kontrola, předběžné verze, Zkontrolovat aktualizace). Změny se použijí tlačítkem OK nebo Použít, Zrušit nic nemění. **Panel rozložení** (sekce Projekt, Výrobky, Mřížka, Umístění, Deska) může být vlevo (výchozí) nebo vpravo od náhledu; volba i šířka panelu se pamatují. Odkazy „Nastavení → Jazyk“ apod. v této specifikaci znamenají příslušnou volbu v tomto okně.

**Předběžný textový wireframe:**

```text
Arrange to Grid for LightBurn
Nastavení → Jazyk: [Automaticky / Čeština / English / Deutsch / Slovenčina / Polski / Français / Español / Italiano ▼] (plná nabídka nejpozději při veřejném v1.0.0)

Soubor: [karticky.lbrn2]  [Otevřít]
Projekt uložen pro: Červený Ruida 6445S, počátek vpravo nahoře
Výrobky: 10 nalezeno / 8 vybráno
Pořadí vybraných: [↑] [↓] [obnovit výchozí]

Počet sloupců: [5]
Mezera X:       [3,00] mm
Mezera Y:       [3,00] mm
Plnění:         [od počátku laseru ▼]   (/ čtení zleva)
Umístění:       [roh počátku laseru ▼]  (/ střed desky / ručně / původní poloha)
Roh u počátku:  X [5,00]  Y [5,00] mm   (jen při „ručně“, jinak vypočteno)
Deska Š,V:      [700,00] [500,00] mm    (předvyplněno podle laseru)
Deska X,Y:      [0,00] [0,00] mm        (roh desky u počátku)
Okraje:         [5,00] mm (L/P/H/D)

Výsledná mřížka: 512 × 123 mm
Kontrola plochy/kolizí: vyhovuje / blokováno (s důvodem)

[ Náhled ]       [ Uložit jako nový projekt ]
```

- Náhled musí barevně nebo čísly odlišit výrobky i při stejném rozměru. Nemusí vykreslovat skutečné motivy: pro MVP stačí spolehlivé vnější obrysy.
- Při chybě náhled uvede konkrétní skupinu a důvod, ne pouze „invalid file“.
- **Umístění mřížky (MVP, rozhodnutí 16. 10. 2026, v1.10 — nahrazuje dřívější „levý horní roh výběru“):** přepínač
  1. **Roh počátku laseru** (výchozí) — roh mřížky nejbližší počátku leží v rohu využitelné plochy desky u počátku (deska u počátku + okraj);
  2. **Střed desky** — mřížka vycentrovaná ve využitelné ploše;
  3. **Ručně** — souřadnice LightBurnu (vzdálenost od počátku) rohu mřížky u počátku;
  4. **Podle původní polohy** — levý horní roh (na obrazovce) vybraných výrobků.
  Všechny souřadnice v GUI jsou hodnoty X/Y LightBurnu, aby je uživatel mohl přímo porovnat.
- **Deska a okraje (MVP, v1.10):** deska leží u počátku laseru (roh desky = X 0, Y 0, lze změnit). Výchozí okraj **5 mm** na všech stranách. Rozměr desky se **předvyplní podle laseru** z hlavičky projektu (`DeviceName`) z uživatelského nastavení; hodnoty jsou vždy viditelné a přepsatelné, změna pro aktuální zakázku nepřepíše uložené nastavení bez potvrzení. Výchozí hodnoty vlastníka: „Červený Ruida 6445S“ (počátek vpravo nahoře) 700 × 500 mm, „Modrý Ruida 643XG“ (počátek vlevo nahoře) 500 × 400 mm. Neznámý laser → rozměr desky musí uživatel zadat. Jde o minimální předběžnou část V11-01 (profily); plné profily zůstávají ve v1.1.
- Zapamatování posledních voleb parametrů rozmístění je volitelné, nikdy nesmí automaticky převzít špatné rozměry jiné zakázky. **Zapamatování výslovně zvoleného jazyka je však povinné** a nezávislé na projektu.
- Uložení smí být povoleno až po kontrole výsledku a explicitním potvrzení.

## 13. Zásadní technická rizika a omezení

| Riziko | Závažnost | Opatření |
|---|---|---|
| Změna souborového formátu v nové verzi LightBurnu | Vysoká | Podpora po testovaných verzích; odmítnout neznámé schéma |
| Poškození jiných XML prvků při serializaci | Vysoká | Minimální zásah do XForm; diff a round-trip test |
| Nesprávné rozměry kvůli textu nebo komplexní křivce | Vysoká | Jednoznačný vnější obdélník; odmítnout bez obrysu |
| Chybný směr souřadnic kvůli MirrorX/MirrorY | Vysoká | Kalibrace a test každé podporované orientace |
| Chybně rozpoznané výrobky / vnořené skupiny | Vysoká | Jen ověřené nejvyšší Group, vlastní kontrolní seznam |
| Ztráta parametrů laseru nebo vrstev | Kritická | Neměnit CutSetting a CutIndex; strukturální diff; před výrobou Preview |
| Uživateli zůstanou neuložené změny v LightBurnu | Střední | Výslovně vyžadovat Save As před načtením |
| Nekontrolované přesuny mimo pracovní plochu | Vysoká | Kontrola hranic, rozsahu a varování/blokace |
| Kolize s neseskupenými objekty / pozadím | Vysoká | Kontrolovat cílové obrysy proti všem spolehlivě změřeným nepřesouvaným překážkám; při nemožnosti bezpečné kontroly zablokovat uložení |
| Text s proměnným obsahem, fontem nebo vně obrysu | Střední až vysoká | Nesahejte na text; upozornit na chybějící font/variable text; kontrola v LightBurn Preview |
| Laserový přesah při rastrování / kompenzace řezu | Střední | Přesný odstup řezných obrysů není automaticky bezpečný odstup pohybu; kontrola Preview |
| Právní omezení formátu a integrace | Střední | Nepoužívat dekompilaci, respektovat EULA; před veřejnou distribucí právní revize |

**Konzervativní pravidlo:** Veškeré neznámé případy jsou `unsupported`, nikoli „asi to bude fungovat“.

## 14. Testovací strategie

### 14.1 Jednotkové testy algoritmu (bez LightBurnu)

| ID | Vstup | Očekávaný výsledek |
|---|---|---|
| ALG-01 | 10 × 100×60, C=5, gap=3, start=(10,20) | 5×2, přesně 512×123 mm, 10 identit |
| ALG-02 | 1 × 100×60, C=5 | Jeden výrobek, žádná kopie |
| ALG-03 | 7 × 100×60, C=3 | 3 řady, poslední jen 1 výrobek vlevo |
| ALG-04 | Různé šířky a výšky | Žádné překrytí AABB, mezery minimálně zadané |
| ALG-05 | C=0, záporná mezera, NaN | Validace odmítne, bez výsledku |
| ALG-06 | Záměna pořadí ID | Stejná množina ID, změněné jen pořadí umístění |
| ALG-07 | Opakované spuštění na výsledek | Stejné cílové polohy (idempotence) |
| ALG-08 | N=1000, různý počet sloupců | Výpočet dokončen, žádné duplicity |
| ALG-09 | Desetinné mezery 0,125 mm | Chyba souřadnic nejvýše určená tolerance |
| ALG-10 | Duplikovaný/nezadaný identifikátor | Výpočet odmítnut |

### 14.2 Integrační testy se skutečným `.lbrn2`

| ID | Projekt | Co ověřit |
|---|---|---|
| LB-01 | Dvě jednoduché skupiny s Rect | Nové pozice odpovídají plánu |
| LB-02 | Rect + různý text v každé skupině | Text zůstává beze změny a pohybuje se se skupinou |
| LB-03 | Rect + gravírovaný motiv na jiné vrstvě | Vnitřní geometrie i CutIndex zůstávají stejné |
| LB-04 | Vnořená podskupina uvnitř výrobku | Vše se přesouvá jako celek, bez relativního posunu |
| LB-05 | Neseskupený objekt mimo výrobky | Bez změny pozice; případná kolize označena |
| LB-06 | Zrcadlení/orientace počátku | Kontrolovaná poloha vpravo/dole; neověřená orientace odmítnuta |
| LB-07 | Projekt s více CutSetting | Úplná shoda parametrů před/po |
| LB-08 | Zamčená skupina / chybějící obrys | Korektní a vysvětlená chyba |
| LB-09 | Projekt s obrázkem | Jen při prokázaném zachování obrázku; jinak odmítnout |
| LB-10 | Projekt uložený novou verzí | Neznámý Formát/AppVersion odmítnout nebo vést přes nové kompatibilitní testy |
| LB-11 | Přerušení při ukládání | Originál existuje beze změny |
| LB-12 | Stejný projekt otevřený pro změny | Nástroj nikdy sám nepřepíše originál, hlásí práci s kopií |
| LB-13 | Validní výstup znovu otevřený v LightBurnu | Geometrie v přesné mřížce, vrstvy i náhled výroby odpovídají |

### 14.3 Testy invariancí

**Následující pravidla platí pro MVP (pouhý přesun), nikoliv automaticky pro rozšíření vytvářející kopie nebo slučující zdroje.** Pro v1.1/2.0 viz normativní tabulka v kap. 25.2. Po uložení MVP musí platit:

- `count(before.Shape) == count(after.Shape)`; počet skupin a textů rovněž stejný.
- `count/contents(before.CutSetting) == count/contents(after.CutSetting)`.
- Pro všechny přesouvané skupiny: `XForm[0:4]` nezměněno, jen přepočtená translace `XForm[4:6]`; totéž a o stejný vektor pro `BackupPath/XForm` textů v podstromu skupiny.
- Pro všechny vnitřní objekty: žádná změna obsahu elementů ani jejich lokálních transformací.
- Pro všechny nevybrané objekty: žádná změna.
- Množina ID před/po je totožná, pořadí podle uživatele zachováno.
- Vnější rozměry každého jednotlivého výrobku před/po se nezmění.
- Původní hash souboru před a po běhu programu beze změny.

### 14.4 Základní fyzická verifikace

Než program použít pro ostrý laser:
1. Ve skutečném LightBurnu otevřít **nový výstup** a zkontrolovat 10 různých motivů.
2. Přeměřit pozice několika kartiček pomocí pozic ve vlastnostech objektů (včetně posledního sloupce/řady).
3. Ověřit řezné a gravírovací vrstvy, výkony, rychlosti a počet průchodů.
4. Spustit **Preview**, vizuálně prohlédnout dráhy, pořadí, přídavky a přehled neseskupených objektů.
5. Ověřit `Frame`/polohu na konkrétním stroji, teprve potom případně zkušební řez s přímým dohledem.

Program nikdy nebude náhradou kontrolních kroků obsluhy stroje.

## 15. Etapy implementace a rozhodovací brány

### Etapa GIT-00 — příprava soukromého vývojového prostředí (před etapou 0)

**Tento krok patří k zahájení programování, není odkládán až na zveřejnění projektu.** Založit účet GitHub (pokud neexistuje), zapnout dvoufaktorové ověření, nainstalovat GitHub Desktop, vytvořit lokální repozitář a bezpečně jej publikovat jako **Private**. Přidat základní `README.md`, `.gitignore` a aktuální technickou specifikaci. Ověřit provedení `Commit` a `Push origin` na nezávadném testovacím souboru; z webového rozhraní ověřit soukromý stav a shodu změn. Konkrétní postup v kap. 29.2, kontrolní testy v kap. 34.

**Výstup / brána GIT-00:** soukromý funkční repozitář, historie prvního commitu viditelná na GitHubu, žádné výrobní nebo zákaznické projekty v úložišti. **Dokud GIT-00 neprojde, nezačínat pravidelnou implementaci zdrojového kódu.** Lokální ověření `.lbrn2` lze připravit předem mimo Git.

### Etapa 0 — ověřit kompatibilitu formátu (nejdůležitější)

**Vstup:** Soukromý ukázkový soubor z aktuální verze LightBurnu: alespoň dvě samostatné skupiny, obdélník a text, dva řezací indexy/vrstvy. 

**Výstup:** Popis reálné hierarchie souboru, ověření `Group`, `Rect`, `XForm`, orientace souřadnic a bezpečného otevření upravené kopie. **STOP**, pokud nelze obnovit správnou pozici bez vedlejších změn. Nepokračovat rovnou do GUI.

### Etapa 1 — čistý algoritmus

Datové třídy, přesná mřížka, nezávislé výpočty, jednotkové testy a numerický příklad `512×123 mm`. Žádná práce s `.lbrn2`.

### Etapa 2 — minimální adaptér projektu

Načíst pouze podporované skupiny s obrysem `Rect`, vypočítat hranice, přepsat přesně vybrané `XForm` ve výstupní kopii, opět načíst a porovnat kontrolní údaje.

### Etapa 3 — praktická použitelnost

Implementovat GUI v **PySide6**, dialog výběru souboru a položek, změnu pořadí, zadání parametrů, náhled, kontrolu pracovní plochy, automatické nové názvy a auditní log. Zabalit nejprve jako přenosnou Windows aplikaci s `.exe`, otestovat na čistém Windows bez Pythonu.

### Etapa 4 — skutečná výrobní validace

Testovat vlastní různé zakázky a nepoužívat ostrý řez, dokud zkušební série nepotvrdí přesnost a zachování parametrů. Vést tabulku podporovaných verzí a známých omezení.

### Etapa 5 — případné zveřejnění (jen když se osvědčí)

Oddělit čistý algoritmus s testy, dokumentací a vhodnou liberální licencí (např. MIT) od nepodporovaného `.lbrn2` adaptéru. Teprve zde řešit nabídku funkce vývojářům a případné vyjádření k právním otázkám. Nic předem neslibovat.

## 16. Přijímací kritéria před výrobním použitím

**Nutné všechny současně:**

1. Otevřít a znovu uložit podporovaný vlastní projekt bez změn jiných než výslovně povolených.
2. V režimu MVP uspořádat nejméně 10 různých skupin na správné souřadnice a mezery; počet výrobků zůstane stejný. V rozšířeních se musí shodovat počty výrobních instancí s plánem (kap. 25).
3. Zachovat oddělené texty, tvary, řezací a gravírovací vrstvy v původní podobě.
4. Přesvědčivě projít integračními a negativními testy v kapitole 14 a příslušnými testy vydání z kapitoly 26.
5. Při jakékoli chybě nikdy nepoškodit ani nepřepsat původní soubor.
6. Uvést uživateli podporovanou verzi LightBurnu, co přesně bylo posunuto a co je třeba ověřit v Preview.
7. Prokázat výběr podmnožiny skupin, opakované ruční přeuspořádání a ověřit, že nevybrané skupiny se vůbec nezměnily.
8. Otestovat platný i neplatný obdélník materiálu a kolize se skupinou mimo výběr; neplatné uložení musí být zablokováno.
9. Výsledek ověřit otevřením **v LightBurnu** (nikoli jen vlastním parserem).

## 17. Právní a licenční rámec

LightBurn je proprietární software a jeho EULA obsahuje omezení zásahů, reverzního inženýrství a odvozování kódu s výhradami pro relevantní zákonné výjimky. Tento projekt **nemá dekompilovat LightBurn**, měnit jeho binární soubory nebo obcházet licenci. Navržená práce je založená na nezávislém algoritmu, veřejně dostupných informacích a na uživatelem vytvořených projektech. Kompatibilitní zásahy do souborového formátu však nejsou oficiálně podporované rozhraní, proto jejich smluvní/právní posouzení není tímto dokumentem vyřešeno. Před veřejnou distribucí adaptéru požádat o právní konzultaci nebo vyjádření držitele práv. 

Oficiální API má navíc vlastní EULA (aktualizace 30. 9. 2026) a výslovně označuje neveřejná rozhraní za nepodporovaná. Proto je vhodné nedělat z referenční implementace závislý uzavřený nástroj bez alternativy. Samotné oddělené matematické jádro lze vydat pod MIT, pokud neobsahuje cizí chráněné součásti a splňuje podmínky použitých knihoven.

Tato část není právním stanoviskem.

## 18. Otevřené otázky pro první programátorskou iteraci

Tyto otázky se řeší **analýzou konkrétního vlastního projektu**, bez nutnosti cokoli slibovat venku:

1. Jaká je skutečná hlavička `AppVersion`/`FormatVersion` aktuálního projektu?
2. Kde se v něm přesně nachází kořenové skupiny a jak se projevuje jejich vnitřní struktura?
3. Které `CutIndex` a tvary představují spolehlivý řezný obrys?
4. Jak se zobrazují transformace u původu a zrcadlení daného stroje?
5. Jak často se objevují neuzavřené křivky, bitmapy a výrobky jiného než obdélníkového tvaru?
6. Jak přesně rozlišit a stabilně zobrazit kořenové skupiny pro povinný výběr a ruční seřazení v MVP?
7. Podaří se round-trip při úpravě jediné skupiny bez změny ostatních nastavení?

Na základě výsledků se teprve zmrazí `MVP` a začne implementace GUI.

## 19. Nejbližší konkrétní krok

V aktuálním LightBurnu vytvořit **testovací, nekritický projekt**: 5–10 samostatných obdélníkových kartiček, každá jako jedna skupina s jedním vnějším řezným obdélníkem a jiným textem, případně kombinací dvou vrstev. Uložit jako nový `.lbrn2` soubor a současně vytvořit kontrolní kopii. Nejdřív pouze prověřit formát a udělat jednu bezpečnou změnu pozice na kopii. Bez této verifikace by jakýkoli hotový program byl jen domněnkou.

---

## 20. Řízení verzí, priority a sledovatelnost požadavků

Tato kapitola je **normativní**: při konfliktu s obecným popisem starších etap mají přednost zdejší výslovné požadavky a verzi odpovídající přijímací kritéria. Rozšíření nesmí zpětně oslabit bezpečnost již funkčních verzí.

| ID / priorita | Funkce | První vydání | Závisí na | Hlavní ověření |
|---|---|---|---|---|
| MVP-01 | Přesná mřížka a nastavitelné mezery | MVP | KAL-00, parser, rozměry | T-MVP-01 až 04 |
| MVP-02 | Výběr skupin | MVP | rozpoznání skupin | T-MVP-05 až 07 |
| MVP-03 | Ruční změna pořadí | MVP | MVP-02, stabilní ID | T-MVP-08 až 10 |
| MVP-04 | Kontrola materiálu a kolizí | MVP | výpočet obrysů, MVP-01 | T-MVP-11 až 18 |
| MVP-05 | Bezpečné uložení a validace projektu | MVP | KAL-00, MVP-01 až 04 | T-MVP-19 až 26 |
| MVP-06 | Windows desktopové GUI / používání bez Pythonu | MVP | MVP-01 až 05, PySide6 | manuální GUI scénáře + GH-05 |
| MVP-07 | Lokalizace GUI: interní MVP CS/EN; pro první veřejné v1.0.0 povinně CS/EN/DE/SK/PL/FR/ES/IT | MVP + public gate | MVP-06 (PySide6 UI), modul i18n | T-I18N-01 až 16 (MVP), T-I18N-17 až 22 + L10N-PUBLIC-01 (public) |
| V11-01 | Profily materiálů a nastavení | 1.1 | MVP-04, verze schématu profilu | T-11-01 až 05 |
| V11-02 | Různá množství variant | 1.1 | MVP-02/03/05, klonování skupin, nové identity | T-11-06 až 13 |
| V11-03 | Automatický výběr řad a sloupců | 1.1 | MVP-01/04, pravidla řazení | T-11-14 až 20 |
| V20-01 | Rozdělení zakázky na více desek | 2.0 | V11-02/03, manifest, vícenásobný export | T-20-01 až 09 |
| V20-02 | Import výrobků z více projektů | 2.0 | KAL-00, mapování vrstev, zdrojů a ID | T-20-10 až 19 |
| FUT-01 | Přímá integrace s LightBurnem | Výhled | veřejné podporované API pro konkrétní operace | T-FUT-01 až 05, podmíněně |

**KAL-00 = kompatibilitní brána:** ověřit na aktuálním vlastním `.lbrn2` čtení geometrie, přesun jedné skupiny, minimální zápis, znovunačtení a správné zobrazení v LightBurnu. Dokud neprojde, samotné algoritmické testy neznamenají použitelný projekt.

**Výklad pojmů:** „MVP“ je první použitelná verze aplikace, „1.1“ a „2.0“ jsou zamýšlené verze aplikace; „verze dokumentu 1.4“ je vydání této specifikace. „Musí“ znamená blokující požadavek daného vydání. „Může“ znamená neblokující rozšíření.

### 20.1 Funkční hranice a důležitá omezení

- V MVP je **přesně jedna instance** každé vybrané skupiny; počet všech objektů se nemění. Od verze 1.1 s V11-02 toto pravidlo přestává platit pro nové instance, ale jejich vznik musí být **výslovně doložen požadovaným množstvím**. Kontrolu invariancí proto verzovat (kap. 25).
- Nevybrané položky se nesmějí pohybovat. Pokud leží v cílové ploše, mají přednost před nově rozmísťovanými výrobky; nelze je automaticky odstranit ani přesunout.
- „Materiál“ znamená uživatelsky definovaný obdélník v souřadnicích projektu. **Nezaměňovat** se skutečnou pracovní plochou laseru; její znalost a shodu je nutné ověřit zvlášť.
- Žádná z verzí nesmí sama posílat úlohy do laseru. Přímá integrace FUT-01 se má týkat výhradně práce s projektem/objekty, nikoli ovládání stroje.

## 21. Detailní funkční požadavky MVP

### 21.1 MVP-01 — přesná mřížka a nastavitelné mezery

**Vstupy:** jednoznačně vybrané a seřazené skupiny, `columns` (celé ≥ 1), `gap_x_mm` a `gap_y_mm` (konečná čísla ≥ 0), počátek `(start_x_mm, start_y_mm)`, zarovnání vlevo/nahoře. Zadání řad je odvozené: `ceil(N / min(columns,N))`; pokud `columns > N`, nesmí vzniknout kopie ani fiktivní prázdné výrobky.

**Výstup:** seznam posunů `(item_id, dx, dy)` a globální AABB výsledné mřížky; žádné změny obsahu skupin. Podporovaný režim shodných obdélníkových obrysů musí mít přesně definované mezerové vzdálenosti. U rozdílných rozměrů se v MVP použije **adaptivní mřížka** (kap. 7.3): šířka sloupce = největší šířka ve sloupci, výška řádku = největší výška v řádku, zarovnání v buňce vlevo nahoře. Garantuje **minimální**, nikoli vždy přesně stejnou skutečnou mezeru; GUI to při rozdílných rozměrech výslovně uvede.

**Toleranci** pro výpočty nastavit na laboratorní `±0,001 mm` a potvrdit proti serializaci a otevření v LightBurnu. `NaN`, `Inf`, záporné mezery, nula sloupců, nejednoznačné AABB → chyba. Nulová mezera je matematicky přípustná, ale GUI upozorní na riziko při řezání.

**Přijímací důkaz:** T-MVP-01 až 04 a ALG-01 až 10; **ALG-04 je od v1.8 povinný**, protože MVP podporuje rozdílné rozměry. Vždy nezávisle porovnat číselné pozice a výsledek v LightBurnu.

### 21.2 MVP-02 — výběr výrobků a ochrana ostatního obsahu

**Ovládání:** seznam kořenových skupin se stavem `podporováno / blokováno`, identifikátorem, pořadím ze souboru, rozměry a případným důvodem odmítnutí. Zaškrtávání po položkách, hromadný výběr jen pro podporované skupiny a možnost vše zrušit. Výběr potomka společně s rodičem nepovolit. Uživatel musí před uložením vidět počet vybraných a nevybraných skupin.

**Pravidla:** při zrušení výběru se položka stává nehybnou překážkou, pokud leží ve výsledné oblasti. Každý `item_id` musí být jednoznačný v rámci načteného projektu a během relace stabilní. Seznam není odvozen ze selekce běžícího LightBurnu.

**Přijímací důkaz:** T-MVP-05 až 07 včetně testu nevybrané skupiny mezi výrobky.

### 21.3 MVP-03 — ruční pořadí výrobků

**Ovládání:** dvě tlačítka Nahoru/Dolů pro právě označenou položku (drag-and-drop volitelně), návrat k výchozímu pořadí. Číslování 1..N musí odpovídat skutečně připravované mřížce. Výběr a pořadí jsou dva různé údaje: odebrání výrobku nemaže jeho identitu a jeho opětovné přidání má předem deterministické pravidlo (např. přidat na konec).

**Pravidla:** žádné přeuspořádávání pořadí elementů XML; mění se pouze seznam pozic při výpočtu. Sérii přesunů doprovází aktualizace náhledu a kontrol. Toto je povinné už v MVP, nikoli odložená funkce.

**Přijímací důkaz:** T-MVP-08 až 10: přesun poslední položky na první místo, opakované změny, zrušení a obnovení pořadí.

### 21.4 MVP-04 — materiál, bezpečnostní okraje a kolize

**Materiál:** uživatel zadá `board_left_mm`, `board_top_mm`, `board_width_mm`, `board_height_mm`, dále nezáporné okraje `margin_left/right/top/bottom_mm`. Počátek mřížky může být nezávislý; výsledná mřížka musí být uvnitř použitelného obdélníku:

```text
usable_left   = board_left + margin_left
usable_top    = board_top + margin_top
usable_right  = board_left + board_width - margin_right
usable_bottom = board_top + board_height - margin_bottom

for each placed_item:
    require item.left   >= usable_left   - epsilon
    require item.top    >= usable_top    - epsilon
    require item.right  <= usable_right  + epsilon
    require item.bottom <= usable_bottom + epsilon
```

**Kolize:** nad ověřenými AABB posoudit: (1) každý pár přesouvaných výrobků; (2) každý přesouvaný výrobek proti všem nevybraným skupinám i samostatným objektům v relevantní oblasti. **Pravidlo odstupu (v1.9):** dvojice je v pořádku, pokud vodorovná vzdálenost jejich AABB ≥ `gap_x − epsilon` nebo svislá vzdálenost ≥ `gap_y − epsilon`; jinak jde o porušení mezery (případně překryv, jsou-li obě vzdálenosti záporné). Stejné pravidlo platí vůči překážkám. Dotek hran je dovolený jen při nastavené nulové mezeře (s varováním). Pro kladné mezery použít přesné geometrické porovnání AABB v toleranci. Pro nevybrané objekty je nutné zohlednit **celou jejich výrobně relevantní geometrii**, nikoliv jen střed. Pokud jejich rozsah nedokážeme bezpečně určit, výstup je blokován; žádné tiché ignorování neznámých tvarů, uzamčených objektů nebo bitmap v cílové oblasti.

**Režim odmítnutí:** překročení materiálu, kolize, nezáporné okraje zabírající celou desku, nemožnost určit obrys překážky → **Uložit zakázáno** s konkrétním důvodem a identifikátorem položky. K dispozici může být čistě informační náhled neplatného rozložení. Nikdy automaticky nepřizpůsobovat měřítko, nenatáčet ani nepřesouvat překážky.

**Pozor:** kontrola AABB řeší geometrický odstup v projektu, nikoliv skutečné přesahy při rastrování, kompenzaci šířky řezu, pohyb hlavy nebo skutečné umístění materiálu. Před výrobou zůstává povinný Preview a kontrola obsluhou.

**Přijímací důkaz:** T-MVP-11 až 18; žádné neplatné umístění nelze uložit.

### 21.5 MVP-05 — bezpečné uložení a validace

**Předpoklady:** úspěšná kompatibilitní brána, všechna položková pravidla, validní materiál/kolize. Uživatelské soubory a protokoly lokální; originál se nikdy nepřepíše. Doporučené jméno `puvodni__grid_001.lbrn2`, bez přepsání existujících souborů.

**Transakce:** načtení + SHA-256 → plán přesunů → vyloučení nepodporovaných struktur → patch translací nejvyšších skupin v dočasném souboru → strukturální a sémantický diff → validace zdrojového SHA-256 → znovunačtení výstupu → atomické zveřejnění nového výstupu → protokol (je-li zapnutý). Pokud některý krok selže, nevznikne žádný výstup prezentovaný jako platný. Nemanipulovat s binárkami LightBurnu.

**Povolené změny MVP:** pouze přesně specifikovaná `XForm` translace každé vybrané nejvyšší skupiny a stejná translace `XForm` v `BackupPath` textů v jejím podstromu (kap. 9.2); počet a identita všech objektů, vrstvy `CutIndex`, `CutSetting`, texty, obrázky a nevybrané objekty beze změny. Při nemožnosti průkazného porovnání blokovat. Přidat zprávu, že samotné strukturální porovnání nenahrazuje otevření v LightBurnu.

**Přijímací důkaz:** T-MVP-19 až 26 a integrační LB-01 až LB-13.

### 21.6 Souhrnná akceptace MVP

MVP je **splněné až po současném úspěchu** testů MVP-01 až MVP-07 (včetně MVP-06 ovládání a MVP-07 jazyků), odpovídajících T-I18N-01 až 16, běžného používání přes PySide6 GUI na čistém Windows bez Pythonu a ruční kontrole alespoň tří různých reálných podporovaných projektů v LightBurnu (včetně odlišných textů a dvou vrstev). Případné nepodporované případy musí být výslovně zaznamenané v matici kompatibility. Žádný známý nebezpečný výstup nesmí projít automatickou validací.

## 22. Funkce aplikace verze 1.1

### 22.1 V11-01 — profily materiálů a nastavení

**Cíl:** jedním výběrem načíst přednastavené parametry rozmístění, **nikoliv** měnit nastavení výkonu/rychlosti laseru.

**Data profilu:** `profile_id`, `name`, `schema_version`, `board_width/height_mm`, okraje L/P/H/D, výchozí `gap_x/y_mm`, výchozí počet sloupců nebo volba `auto_columns`, volitelný počátek a zarovnání. Materiálové vlastnosti, výrobce či poznámky mohou být textové; **nepovažovat je za kalibraci laseru**.

**Chování:** vytvořit/upravit/duplikovat/přejmenovat/smazat profil; aktivní profil do formuláře *předvyplní* hodnoty, ale uživatel může parametry aktuální zakázky změnit bez přepsání profilu. Před exportem zobrazit skutečné hodnoty pro danou zakázku. Profily uložit odděleně do lokálního verzovaného JSON; chybný profil nezpůsobí ztrátu ostatních. Neexportovat profily do `.lbrn2` a nesměšovat s `CutSetting`.

**Implementace (v1.24, 18. 10. 2026, přání vlastníka):** sekce *Profil rozložení* v levém panelu; profil = název + `columns`, `auto_columns`, `gap_x/y`, `fill`, `rotation`, `anchor` (JSON v uživatelském nastavení, `profiles/<název>`). **Deska a okraje v profilu nejsou** — patří k laseru v katalogu laserů (v1.23). Výběr profilu hodnoty nastaví (jeden krok zpět); změna hodnot profil nemění, výběr se přepne na „bez profilu“; Uložit… (stejný název = přepsat po potvrzení), Smazat. Poškozený záznam se ignoruje, ostatní profily zůstávají.

**Testy T-11-01 až 05:** načtení přesných rozměrů, uložení a znovunačtení, přepsání lokálních hodnot bez modifikace profilu, odmítnutí chybného schématu, zachování funkce bez uloženého profilu.

### 22.2 V11-02 — různé množství každé varianty

**Cíl:** pro každou identifikovanou zdrojovou skupinu nastavit celočíselnou položkovou `quantity >= 0` (v přiměřeně zdokumentovaném horním limitu), následně vytvořit přesně požadovaný počet výrobních **instancí**. Hodnota 0 znamená vynechat, nikoli smazat původní skupinu ze zdrojového projektu.

**Klíčová změna modelu:** rozlišit **`SourceItem`** (vzorový výrobek v dokumentu) a **`PlacementInstance`** (konkrétní výrobní kus). Instance mají `instance_id`, `source_item_id`, `copy_index` (1..quantity), pozici, původní parametry a vazbu na zdroj. Výchozí pořadí instancí musí být deterministické (např. varianty v uživatelském pořadí, jejich kopie za sebou); budoucí míchání lze přidat samostatnou volbou.

**Zachování originálu:** po zvýšení množství je **povolené a očekávané** přidávání identických kopií skupin do výstupního `.lbrn2`; nelze tedy nadále kontrolovat invarianci `count(before.Shape)==count(after.Shape)`. Místo toho validovat přesné plánované počty, nezměněný obsah každé kopie, zachování zdrojových skupin uvnitř výstupního projektu podle výslovně definované exportní strategie a žádné neplánované prvky. Soubor s původním projektem zůstane nedotčený. Vygenerované kopie musí mít korektní případné interní identifikátory/reference; nelze jen slepě naklonovat XML uzly s duplicitními ID.

**Bezpečnostní brána:** nejprve vytvořit test s jednou zdrojovou skupinou a dvěma kopiemi, otevřít v LightBurnu, ověřit editovatelnost, vrstvy i Preview. Pokud nelze bezpečně prokázat identitu kopií nebo interní odkazy, funkci neoznačit za hotovou a zůstat u MVP bez násobení.

**Implementace (v1.16, 17. 10. 2026 — na přání vlastníka předsunuto do `0.1.0-alpha.3`, brána KAL-03):**
- *Model:* kopie = `PlacementInstance` s id `G5+1`, `G5+2`… a vazbou na zdroj (`ArrangeParams.copies`); rozmisťuje se jako samostatný výrobek (vlastní pořadí, ruční úhel, automatické natočení podle zdroje). Kopie, která není vybraná k rozmístění, se nezapíše.
- *Ovládání:* výběr v seznamu nebo kliknutím v náhledu; **Ctrl+C** zapamatuje vybrané, **Ctrl+V** přidá po jedné kopii, **Vytvořit kopie…** (ikona na liště, Ctrl+D, menu Úpravy) přidá zadaný počet kopií každého vybraného (1–999), **Delete** / odškrtnutí kopii odebere. Kopie se přidávají na konec pořadí a převezmou ruční úhel kopírovaného výrobku. Kopie platí do otevření jiného projektu.
- *Zápis:* bajtová kopie elementu nejvyšší skupiny vložená za poslední nejvyšší `Shape` (pořadí a identita původních výrobků se nemění); v kopii se mění jen `XForm` skupiny a `BackupPath` textů (`T ∘ XForm`) a vynechá se `VertList`/`PrimList` tvarů se sdíleným `VertID`/`PrimID` — kopie odkazuje na ID definované v originálu, stejně jako to LightBurn dělá sám u opakovaných tvarů (KAL-02). Tím nevznikají duplicitní ID.
- *Kontrola:* nezávislý ověřovač: počet nových nejvyšších tvarů = počet kopií; každá kopie bajtově shodná se zdrojem mimo `XForm` a vynechanou sdílenou geometrii, odkazovaná ID existují, `XForm` = `T ∘ původní`; po odebrání kopií musí výstup splnit všechny dosavadní kontroly přesunu; po znovunačtení leží obrysy kopií v cílových obdélnících.
- *Brána KAL-03:* výstupy s kopiemi (klíčenky, nativní tvary, natočené kopie, oba lasery) otevřít v LightBurnu — kopie celé, editovatelné, správné vrstvy, Preview; do splnění neoznačovat za výrobně ověřené.

**Počet kusů (v1.25, 18. 10. 2026):** pole *Počet kusů* v sekci Výrobky nastaví `quantity` vybraných výrobků (vybraná kopie = její originál): `quantity − 1` kopií se vloží **hned za poslední kus** daného výrobku (výchozí pořadí „varianty v uživatelském pořadí, jejich kopie za sebou“), snížení odebere nejnovější kopie, `0` výrobek nerozmístí (zdrojová skupina v projektu zůstává). Seznam ukazuje „×N“. CLI `--quantity ID=N` (kopie `ID+q1…`). Protokol: `pieces_per_item`. Zápis a kontrola kopií beze změny (v1.16, KAL-03).

**Testy T-11-06 až 13:** např. A=4, B=2, C=0 → 6 výrobních instancí; přesná multiplicita, správné zachování textu každé varianty, žádné neplánované kopie, determinismus, maximální limit, bezpečné odmítnutí nepodporovaných interních odkazů, validace vrstev po uložení.

### 22.3 V11-03 — automatický výběr počtu řad a sloupců

**Cíl:** pro zadanou sadu (případně už expandované instance) vyzkoušet `columns = 1..N` a vypočítat mřížku pro každý počet sloupců. Počet řad je vždy odvozen od počtu instancí. Volbu ponechat **výhradně pravidelnou mřížkou**, neprovádět volný nesting.

**Omezení:** každého kandidáta ověřit proti rozměru materiálu, okrajům, zadaným mezerám, kolizím s nevybranými objekty, orientaci a kompatibilitě. Kandidáty se stejnými položkami a stejným pořadím srovnávat deterministicky podle **nejmenší plochy výsledného AABB**, při shodě podle obvodu a dále podle menšího počtu řad a sloupců. Neprohlašovat za globální optimální využití materiálu a nepoužívat imaginární skóre „úspory“ u pevné velikosti desky.

**Chování UI:** přepínač `Počet sloupců ručně / Automatický návrh`; v automatickém režimu nabídnout vítězný výsledek s počtem řad/sloupců a rozměry, případně 2–3 další platné alternativy; uživatel může výsledek převzít či vrátit ruční režim. Při žádném validním kandidátu blokovat export a uvést proč.

**Implementace (v1.24, 18. 10. 2026, přání vlastníka — zjednodušené kritérium):** zaškrtávátko *Automaticky* u Počtu sloupců (`ArrangeParams.columns = AUTO_COLUMNS`). Vybere se **největší počet sloupců, při kterém je mřížka nejvýš tak široká jako využitelná plocha desky** (mřížka se rozloží po šířce desky od počátku, nejméně řádků); kandidáti se počítají celým plánem včetně natočení a kopií, horní mez odhadem z nejmenšího rozměru výrobku. Nevejde-li se ani jeden sloupec, použije se 1 a kontrola ohlásí přesah. Kritérium nejmenší plochy AABB z původního návrhu se nepoužívá (u pevné desky je cílem zaplnit šířku). CLI `--columns auto`. Navazuje **Vyplnit desku kopiemi**: přidá největší počet kopií vybraných výrobků (střídavě), při kterém plán nemá žádnou chybu (zdvojování + půlení intervalu, limit 999 kopií).

**Testy T-11-14 až 20:** různá N, obdélníky 100×60, úzká/široká deska, nevybrané překážky, žádné validní řešení, přesně shodné skóre, stabilní opakovaný výsledek.

### 22.4 Přejímka verze 1.1

Povinně projdou **veškeré testy MVP (regrese)** a T-11-01 až 20. Kopie výrobků a automatický výběr nesmějí obcházet MVP validátor plochy a kolizí. Migrace profilů je otestována alespoň mezi dvěma verzemi schématu nebo je v prototypu odmítnuta s jasným upozorněním.

## 23. Funkce aplikace verze 2.0

### 23.1 V20-01 — automatické rozdělení zakázky na více desek

**Vstup:** definované výrobní instance (`quantity` z v1.1), parametrický materiál/okraje/mezery, omezení výsledných souborů a řazení. **Výstup:** seznam desek, každá jako samostatný ověřený `.lbrn2` projekt a společný manifest ve formátu JSON/CSV: `board_index`, `file_name`, `instance_ids`, počty podle variant, použitý profil, SHA-256 výstupu, status ověření.

**Pravidla:** rozdělovat deterministicky na desky při zachování předem zvoleného pořadí instancí, bez otočení nebo změny velikosti. První realizace může používat jednoduché postupné plnění desek a pro každou desku nejlepší *validní* počet sloupců; nemusí jít o optimální nesting. Pokud jedna instance nevyhoví na žádné desce, vypsat chybu a zabránit označení celé sady za hotovou. Každá instance musí být na právě jedné desce. **Nevolit implicitně více stránek uvnitř jednoho LightBurn projektu**: použití jednotlivých nezávislých `.lbrn2` je ověřitelnější.

**Ukládání:** export do nové složky transakčně (nejprve připravit a validovat všechny desky); při selhání nesmí vzniknout částečná série prezentovaná jako úspěšná. Když složka již obsahuje soubory, vytvořit nový jednoznačný podadresář; nikdy nepřepisovat staré výsledky.

**Testy T-20-01 až 09:** 43 instancí / kapacita 20 → 3 desky pouze v testovacím fixture s takto ověřenou kapacitou; součet položek=43, každá přesně jednou, pořadí a počty správně; příliš velká položka, přerušení exportu, neopakování jména souboru, shoda manifestu s výstupy.

### 23.2 V20-02 — import výrobků z více projektů

**Cíl:** vybrat dva nebo více lokálních `.lbrn2` jako zdroje skupin a sestavit **nový společný** výstup bez změny originálů.

**Konflikty, které MUSÍ být vyřešeny před implementací výroby:**

- Identita: jednoznačný klíč `(source_document_id, source_group_path, instance_index)`; interní ID v cílovém projektu nesmějí kolidovat.
- Vrstvy a řezné parametry: při shodě se musí prokázat úplná kompatibilita příslušných `CutSetting`, `CutIndex`, režimů, subvrstev a strojního nastavení. **Neshodné parametry nelze potichu přemapovat na stejnou barvu nebo číslo vrstvy.** Nejprve režim „všechny zdroje mají kompatibilní nastavení“, později výslovné potvrzené mapování, pokud bude ověřitelné.
- Jednotky, souřadnice, `MirrorX/MirrorY`, formát a verze souboru, fonty, bitmapy, externí reference a případné knihovní objekty musí být ověřeny. Při nekompatibilitě výstup odmítnout a uvést konfliktní zdroj.
- Zachovat editovatelnost textů a podskupin, jejich vazby i nastavení. Nespoléhat na „Export SVG → Import SVG“ jako bezpečný převod vrstev.

**Bezpečnostní brána:** nejprve dvě jednoduché projekty se shodnými CutSetting; fyzicky otevřít výsledný kombinovaný soubor a ověřit Preview. Teprve pak přidat širší množinu schémat.

**Testy T-20-10 až 19:** shodná nastavení, rozdílné nastavení výkonu na stejně označené vrstvě (blokace), duplicitní interní ID, chybějící bitmapový zdroj, nepodporované formátové verze, prokázání zachování textu, přesný počet instancí ze všech zdrojů, nezměněné originály.

### 23.3 Přejímka verze 2.0

Současně projde plná regrese MVP a v1.1, T-20-01 až 19 a minimálně jedna kompletní zkušební zakázka s více deskami otevřenými jednotlivě v LightBurnu. Žádný import z více projektů nesmí tiše měnit laserové parametry.

## 24. Výhled FUT-01 — přímá integrace s LightBurnem

**Záměr:** uživatel v LightBurnu označí různé skupiny, spustí funkci rozmístění a výsledek se promítne do aktuálního dokumentu bez ručního exportu/importu. Toto **není potvrzená schopnost** současného veřejného API a nemá být příslibem dodání.

**Technická podmínka:** teprve po doložení veřejně podporovaného mechanismu pro (a) načtení skutečně vybraných objektů a jejich identit, (b) získání geometrií/transformací, (c) aplikaci změn poloh se zachováním Undo/Redo a (d) jednoznačné potvrzení výsledku lze připravit nativní adaptér. Alternativní oficiální pluginové rozhraní je rovněž podmíněno jeho skutečnou dostupností.

**Nepřijatelné cesty pro oficiální řešení:** injektování kódu do procesu, patchování binárky, spoléhání na vnitřní nezdokumentované funkce a vydávání klávesového makra za plnohodnotné API. Externí otevření výsledného souboru není totéž co přímá editace aktivního výběru.

**Podmíněné testy T-FUT-01 až 05:** přenos aktivní selekce beze ztráty, Undo/Redo jednou operací, nevybrané objekty beze změn, bezpečné zrušení změny, stejné výsledné souřadnice jako referenční GridEngine. Před jejich definováním do konkrétního integračního testovacího harnessu musí existovat oficiální vhodné rozhraní.

## 25. Rozšířený datový model, verze invariantů a modulární architektura

### 25.1 Model připravený na následující verze

```text
SourceProject:
    document_id, path, sha256, format_version, app_version, coordinate_system
    cutting_settings_digest, resources_digest, compatibility_status

SourceItem:
    source_item_id, document_id, source_group_path, source_order, label
    outline_bounds_mm, geometry_digest, xform, cutting_references
    supported, validation_errors[]

PlacementInstance:
    instance_id, source_item_id, copy_index, requested_quantity
    ordered_index, planned_bounds_mm, delta_x_mm, delta_y_mm

MaterialProfile:
    profile_id, schema_version, name, board_size_mm, margins_mm
    default_gap_x_mm, default_gap_y_mm, column_mode, default_columns

BoardPlan:
    board_index, usable_rect_mm, ordered_instance_ids[]
    columns, rows, planned_grid_bounds, collisions[], valid

JobPlan:
    job_id, version_policy, source_projects[], sources[], instances[]
    board_plans[], applied_profile_snapshot, validation_report

ExportManifest:
    job_id, board_outputs[], per_source_counts, hashes, warnings[]
```

**Pravidlo vrstev:** `GridEngine` rozumí jen rozměrům, pořadí a validaci rozmístění. `ProjectAdapter` odpovídá za přenos/přesun/skupiny a verzovanou kompatibilitu LightBurnu. `JobPlanner` řeší množství, desky a zdrojové projekty. `ProfilesRepository` spravuje externí nastavení. UI nad nimi nemá vlastní druhou implementaci mřížky.

### 25.2 Invariance po verzích

| Vydání | Co se smí změnit v novém `.lbrn2` | Co zůstává neměnné | Jak se validuje |
|---|---|---|---|
| MVP | Pouze translace vybraných kořenových skupin | Počet/identita všech objektů, jejich obsah, vrstvy, nevybrané polohy | Strukturální diff + plán posunů + kontrola LightBurn |
| 1.1 s V11-01/03 | Stejné změny jako MVP | Profily ani algoritmus nesmějí změnit řezné parametry | Regrese MVP + shoda výsledných parametrů |
| 1.1 s V11-02 | Navíc **přesně naplánované nové kopie skupin** a potřebná nová ID | Sémantický obsah každého vzoru/kopie, parametry vrstev, originální zdrojový soubor | Mapování `source_item_id → instance_ids`, přesné počty, validace referencí |
| 2.0 V20-01 | Nové ověřené výstupní projekty pro jednotlivé desky | Souhrnný počet instancí, parametry všech kusů, originály | Manifest + součet + nezávislá validace každého souboru |
| 2.0 V20-02 | Nový sloučený projekt z několika zdrojů | Kompatibilní nebo výslovně odmítnuté vrstvy a další zdroje | Mapování identity a vrstev + otevírací test v LightBurn |

Při přidání duplicit je **nesprávné** trvat na původní invarianci shodného počtu skupin; naopak je **nesprávné** u MVP tolerovat libovolný růst počtu objektů. Každý release musí definovat přesnou množinu povolených změn. Při neznámém typu dokumentu se soubor neexportuje.

### 25.3 Struktura projektu pro programování

```text
src/grid_arranger/
  domain/models.py               # čisté datové typy, žádný import Qt
  core/grid_layout.py            # deterministické cílové pozice
  core/collision.py              # průniky, materiál, bezpečné odmítnutí
  core/order.py                  # permutace vybraných ID
  adapters/lightburn/read.py     # pouze čtení podporovaných formátů
  adapters/lightburn/write.py    # minimální bezpečný patch
  adapters/lightburn/geometry.py # světo-vztažné obrysy, nepřesouvat nemožné
  safety/verify.py               # verzované invariance / semantický diff
  ui/main_window.py              # PySide6; bez geometrické logiky
  ui/i18n.py                     # QTranslator, QLocale, runtime volba jazyka
  ui/translatable_messages.py    # centrální veřejné hlášky + formátování
  settings/user_settings.py      # bezpečné uložení jazykové preference
  application/arrange_job.py     # orchestrace MVP
  application/job_planner.py     # 1.1 a 2.0, zatím rozhraní bez implementace
  application/profiles.py        # 1.1 JSON, zatím rozhraní bez implementace
  application/export_manifest.py # 2.0, zatím rozhraní bez implementace
  integration/lightburn_api.py   # výhled: pouze když bude dokumentované API
translations/
  gridarranger_cs.ts             # český překlad (interní MVP)
  gridarranger_de.ts             # němčina (povinná před veřejným v1.0.0)
  gridarranger_sk.ts             # slovenština (povinná před veřejným v1.0.0)
  gridarranger_pl.ts             # polština (povinná před veřejným v1.0.0)
  gridarranger_fr.ts             # francouzština (povinná před veřejným v1.0.0)
  gridarranger_es.ts             # španělština (povinná před veřejným v1.0.0)
  gridarranger_it.ts             # italština (povinná před veřejným v1.0.0)
  gridarranger_en.ts             # povinné: anglické tvary množného čísla (Qt numerus)
tests/i18n/
  test_language_settings.py
  test_translation_catalog.py
  test_numeric_locale.py
```

**Architektonické pravidlo:** nerealizovat budoucí funkcionalitu předem. V MVP stačí stabilní typy a rozhraní s možností rozšíření; moduly pro verze 1.1 a 2.0 mohou vzniknout až při jejich implementaci. To zabrání zbytečné složitosti.

## 26. Testovací matice, závislosti a výstupní brány

### 26.1 Příklady závazných automatických testů MVP

| Test | Scénář | Očekávané chování |
|---|---|---|
| T-MVP-01 | 10 různých skupin 100×60, 5 sloupců, mezera 3/3, počátek 10/20 | Souřadnice přesně dle kap. 7; mřížka 512×123 mm |
| T-MVP-02 | 7 skupin, 3 sloupce | 3 řady, poslední má jen 1 kus, nic se nekopíruje |
| T-MVP-03 | Sloupce=0, mezera=-1, NaN/Inf | Před výpočtem i exportem chyba |
| T-MVP-04 | Opakovat stejný výpočet na již rozmístěném projektu | Stejná konečná pozice a počet položek (idempotence) |
| T-MVP-05 | Vybrat 3 z 8 skupin | Posunuty právě 3; ostatních 5 zcela beze změny |
| T-MVP-06 | Nulový výběr | Výpočet a uložení zablokovány |
| T-MVP-07 | Nepodporovaná/zamčená skupina | Jasné vysvětlení, nepřesouvat |
| T-MVP-08 | Manuálně prohodit první a poslední kartičku | Náhled a výsledek odpovídá novému seznamu |
| T-MVP-09 | Odebrat/vrátit položku | Pořadí deterministické, bez duplicit/ztrát |
| T-MVP-10 | Obnovit výchozí pořadí | Návrat na `document_order` |
| T-MVP-11 | Mřížka přesahuje okraj materiálu o 0,1 mm | Blokace exportu, identifikace přesahu |
| T-MVP-12 | Plocha 600×400, okraj 5, mřížka 512×123 na pozici 10/20 | Vhodné umístění, pokud souřadnice spadají do využitelné plochy |
| T-MVP-13 | Materiál 0×400 nebo okraje přesahují šířku | Blokace exportu |
| T-MVP-14 | Překryv dvou cílových výrobků | Blokace, identifikovat konfliktní dvojici |
| T-MVP-15 | Nevybraná skupina v cílové mřížce | Blokace exportu, nevybraná skupina beze změny |
| T-MVP-16 | Neseskupený objekt kříží cílovou mřížku | Blokace exportu |
| T-MVP-17 | Neznámá geometrie nepřesouvaného objektu v oblasti | Bez ověřitelných hranic nelze potvrdit bezpečnost → blokace |
| T-MVP-18 | 0mm mezera | Bez matematického překrytí, ale výslovné varování o řezání |
| T-MVP-19 | Výstup obsahuje stejný počet skupin jako vstup | Nutné pro MVP; přesné očekávané `XForm` translace |
| T-MVP-20 | Změnit `CutSetting` simulovaným vadným writerem | Validátor odmítne i formálně čitelný soubor |
| T-MVP-21 | Writer změní lokální text jedné kartičky | Validátor odmítne |
| T-MVP-22 | Selže ukládání uprostřed zápisu | Originál zůstane byte-identický, nevznikne platný výstup |
| T-MVP-23 | Výstupní soubor se stejným názvem existuje | Návrh dalšího názvu, nikdy přepis |
| T-MVP-24 | Původní soubor se od načtení změnil | SHA-256 mismatch blokuje uložení |
| T-MVP-25 | Neznámá verze formátu XML | Bez zápisu odmítnout a označit nepodporovanou verzi |
| T-MVP-26 | Otevřít výstup v aktuálním LightBurnu | Správná editace, vrstvy a Preview; ručně zdokumentováno |

### 26.2 Závazné testy v1.1

| Test | Scénář | Očekávané chování |
|---|---|---|
| T-11-01 | Uložit profil s rozměry a mezerami | Po restartu stejné hodnoty |
| T-11-02 | Změnit lokální parametry oproti profilu | Profil se bez explicitního uložení nemění |
| T-11-03 | Nahrát profil s nesprávným typem dat | Validace odmítne |
| T-11-04 | Bez profilů spustit běžný režim | Výpočet je funkční |
| T-11-05 | Neznámá verze schématu profilu | Řízené odmítnutí, ostatní profily nepoškozeny |
| T-11-06 | A=4, B=2, C=0 | Přesně 6 výrobních instancí |
| T-11-07 | A/B mají odlišný text | Každá kopie obsahuje svůj zdrojový text |
| T-11-08 | Interní ID kopií | Žádná kolize a všechny odkazy platné |
| T-11-09 | Množství záporné/necelé/limit překročen | Zabránit exportu |
| T-11-10 | Množství všude 1 | Chování stejné jako MVP |
| T-11-11 | Požadovaná množství po exportu | Přesná multiplicita ve výsledném projektu |
| T-11-12 | Nepodporovaná bitmapová/reference struktura u kopie | Bezpečné odmítnutí, žádný částečný soubor |
| T-11-13 | Opakovaný export se stejným zadáním | Stejný plán a smysluplně ekvivalentní projekty |
| T-11-14 | Automatické sloupce pro 10 stejných výrobků | Projít všechny kandidáty 1..10, vybrat platný dle skóre |
| T-11-15 | Úzká deska | Nevybrat rozložení, které přesahuje |
| T-11-16 | Široká deska | Deterministický návrh platné mřížky |
| T-11-17 | Nevybraná překážka v ploše | Překážka eliminuje kolidující kandidáty |
| T-11-18 | Žádné možné rozložení | Jasná blokace, bez exportu |
| T-11-19 | Shodné hodnoty skóre | Definované tie-break rozhodnutí |
| T-11-20 | Stejný vstup opakovaně | Stejné pořadí kandidátů a souřadnice |

### 26.3 Závazné testy v2.0 a výhled

| Test | Scénář | Očekávané chování |
|---|---|---|
| T-20-01 | 43 instancí, ověřená kapacita jedné desky 20 | Právě 3 soubory desek; žádná instance se neztratí |
| T-20-02 | Zkontrolovat položky mezi deskami | Každé `instance_id` právě jednou; pořadí podle specifikované strategie |
| T-20-03 | Srovnat manifest a soubory | Součty variant, názvy a kontrolní součty odpovídají |
| T-20-04 | Jedna instance se na desku nevejde | Blokace celé zakázky a konkrétní důvod |
| T-20-05 | Simulované přerušení zápisu třetí desky | Žádná rozpracovaná sada není označena za hotovou |
| T-20-06 | Opakovat export téže zakázky | Nová složka a názvy, žádné přepsání |
| T-20-07 | Vstup se třemi variantami a různými počty | Součet počtů pro každou variantu na všech deskách souhlasí |
| T-20-08 | Kompletní zakázka se 2+ deskami | Všechny soubory samostatně projdou validátorem |
| T-20-09 | Otevření každé desky v LightBurnu | Vrstvy, texty a Preview odpovídají manifestu |
| T-20-10 | Sloučit dva jednoduché projekty se shodnými CutSetting | Vznikne jeden správný nový projekt se všemi vybranými výrobky |
| T-20-11 | Dva zdroje se stejným interním ID | Identita bezpečně přemapovaná nebo blokace, nikdy tiché zdvojení |
| T-20-12 | Různé texty v původních projektech | Všechny texty zachovány a správně přiřazené |
| T-20-13 | Stejná barva vrstvy, odlišné řezné parametry | Blokace bez tichého mapování |
| T-20-14 | Konflikt výkonu/rychlosti na stejné vrstvě | Export odmítnut a konflikt konkrétně popsán |
| T-20-15 | Chybějící bitmapový/fontový/externí zdroj | Bezpečné odmítnutí, není-li prokazatelně zachován |
| T-20-16 | Nepodporovaná formátová verze druhého projektu | Blokace celé kombinace, žádný částečný výstup |
| T-20-17 | Dva zdroje s množstvími variant | Součty instance IDs a variant odpovídají plánu |
| T-20-18 | Hash obou originálních souborů před/po exportu | Oba soubory jsou byte-identické |
| T-20-19 | Výsledný sloučený projekt otevřený v LightBurnu | Editovatelné skupiny, zachované CutSetting/CutIndex a správný Preview |

**Podmíněná integrační sada FUT-01:** T-FUT-01 = převzetí aktivního výběru; T-FUT-02 = jedna vratná akce Undo/Redo; T-FUT-03 = nevybrané prvky nezměněny; T-FUT-04 = bezpečné zrušení/selhání; T-FUT-05 = přesná shoda souřadnic s referenčním výpočtem. Testy se aktivují až po doložení použitelného oficiálního API.

### 26.4 Závislosti a pořadí implementace

```text
KAL-00: kompatibilita .lbrn2 a bezpečný přesun 1 Group
    ↓
Čisté typované doménové objekty + jednotkové testy
    ↓
MVP-01 mřížka ──► MVP-02 výběr ──► MVP-03 ruční pořadí
    ↓                             │
MVP-04 materiál a kolize ◄────────┘
    ↓
MVP-05 bezpečný zápis + validace + PySide6 GUI
    + MVP-07 lokalizace CS/EN od prvních obrazovek
    ↓  [Gate MVP: všechny T-MVP + T-I18N + LB integrační testy]
V11-01 profily ─┐
V11-02 množství ├─► V11-03 automatický výběr řad/sloupců
                 ↓
        [Gate 1.1: regresní MVP + T-11]
                 ↓
V20-01 více desek ─► V20-02 více zdrojových projektů
                 ↓
        [Gate 2.0: regresní MVP+1.1 + T-20]
                 ↓
FUT-01 integrace: pouze při dostupnosti veřejného API
```

**Vývojový princip:** v případě selhání brány nedeklarovat release jako dokončený; opravit základní závadu a znovu spustit regresní testy. Publikace a kontaktování LightBurnu nejsou součástí žádné povinné brány.

### 26.5 Definice dokončení (Definition of Done)

Každý požadavek má při implementaci záznam `ID → modul → automatický test → integrační fixture → výsledek`. Vydání je připraveno teprve když:

1. Funkční kritéria příslušné verze jsou splněna; výstupy jsou deterministické a reprodukovatelné.
2. Bezpečnostní a negativní testy pro danou verzi prošly, včetně testu původních souborů.
3. Pro verze vytvářející/zkombinující objekty prošly přesné kontroly identit, počtů, CutSetting/CutIndex a zdrojů.
4. Všechny testované verze LightBurnu jsou uvedeny v `COMPATIBILITY.md`, neznámé kombinace se bezpečně odmítají.
5. Výsledný projekt je otevřen a zkontrolován v reálném LightBurnu; minimálně jedna relevantní zkušební výroba proběhla pod dohledem.
6. Případné neschopnosti řešit určitý typ geometrie jsou uživateli výslovně zobrazené; nejsou prezentované jako úspěch.
7. Dokumentace GUI, příklady použití a changelog odpovídají skutečnému chování.
8. Všechny povinné řetězce UI jsou ověřeny v češtině a angličtině při interním MVP, **před veřejným v1.0.0 ve všech osmi jazycích** včetně bezpečnostních hlášek; prošly testy přepnutí jazyka, formátování hodnot, serializace do `.lbrn2` a distribuovaného EXE (MVP-07/T-I18N, L10N-PUBLIC-01).

### 26.6 Evidované otázky před zahájením implementace

- Jak konkrétní současná verze LightBurnu serializuje skupiny, reference, zdroje a případné interní identifikátory při uložení?
- Jak bezpečně získat AABB každého nepřesouvaného objektu, který může kolidovat s cílovou mřížkou? Pokud to nelze, MVP musí pro tento projekt jasně odmítnout export.
- Jaký způsob minimálního zápisu zachová nejen sémantiku, ale i identitu a informace neznámých XML elementů?
- Jaký způsob kopírování a sloučení skupin je pro konkrétní `.lbrn2` skutečně podporovatelný ve v1.1 a v2.0?
- Jak má postupovat uživatel při změně nastavení stroje/počátku, aby se nová mřížka otevřela na očekávané pozici?

Toto jsou **ověřovací úkoly**, nikoli potvrzené technické možnosti současného LightBurnu.

---

## 27. Veřejné podklady použité při návrhu

- LightBurn — **Grid Array**: https://docs.lightburnsoftware.com/2.0/Reference/GridArray/
- LightBurn — **Grouping**: https://docs.lightburnsoftware.com/latest/Reference/Grouping/
- LightBurn — **Quick Nest**: https://docs.lightburnsoftware.com/2.1/Reference/QuickNest/
- LightBurn — **File Management** (rozdíl mezi Open a Import): https://docs.lightburnsoftware.com/latest/Reference/FileManagement/
- LightBurn Forum — **LBRN2 File Documentation**, listopad 2021 (struktura, matice, orientace): https://forum.lightburnsoftware.com/t/lbrn2-file-documentation/52174
- LightBurnSoftware — **REST API** (oficiální veřejné endpointy): https://github.com/LightBurnSoftware/LightBurn-REST
- LightBurn REST API — **Uploading files**: https://github.com/LightBurnSoftware/LightBurn-REST/blob/main/docs/uploading.md
- LightBurn REST API — **API EULA**, 30. 9. 2026: https://github.com/LightBurnSoftware/LightBurn-REST/blob/main/API-EULA.md
- LightBurn — **EULA**: https://docs.lightburnsoftware.com/2.1/Licensing/LightBurnEULA/
- LightBurn — existující funkční návrh **Distribute Selected Objects Across a User-Defined Grid**: https://lightburn.fider.io/posts/4796/distribute-selected-objects-across-a-user-defined-grid

**Poznámka k ověření:** Návrh obsahuje záměrně restriktivní počáteční rozsah. Není důkazem, že nástroj již umí bezpečně upravovat současné projekty `.lbrn2`; k tomu potřebuje aktuální vzorový soubor a integrační test v LightBurnu.


## 28. Záznam změn specifikace

- **v1.26 (18. 10. 2026):** Na přání vlastníka zahájeno PUBLIC-01 / L10N-PUBLIC-01: katalogy rozhraní a offline příručka v `de/sk/pl/fr/es/it` (vedle `cs/en`), volba jazyka nabízí všech osm jazyků. Překlady jsou **strojový návrh** — stav viz kap. 36.5 (*Stav k v1.26*); jazyk se nesmí prohlásit za ověřený bez lidské revize.
- **v1.25 (18. 10. 2026):** Počet kusů výrobků (V11-02 dokončeno): pole Počet kusů, kopie hned za originálem, 0 = vynechat; CLI `--quantity` (kap. 22.2).
- **v1.24 (18. 10. 2026):** Na přání vlastníka automatický počet sloupců podle šířky desky (V11-03, zjednodušené kritérium), *Vyplnit desku kopiemi* a profily rozložení (V11-01, bez desky) (kap. 22.1, 22.3).
- **v1.23 (18. 10. 2026):** Na přání vlastníka **příprava projektu pro jiný laser** a **katalog laserů** (kap. 9.1 bod 4b). Výstup pro cílový laser: hlavička `DeviceName`, `MirrorX`, `MirrorY` cílového laseru; transformace výrobků `S_cíl ∘ T ∘ S_zdroj` (zrcadlení, výrobek na cílovém laseru vypadá stejně); deska a roh plnění podle cílového laseru; při jiném počátku jen celý projekt (všechny výrobky vybrané, žádné jiné objekty); nastavení vrstev se nepřevádí. Nezávislá kontrola dovoluje v hlavičce změnu jen těchto tří atributů. Katalog v Nastavení → Lasery (`LaserProfile`: název = `DeviceName`, roh počátku, deska s okraji); lasery z otevřených projektů se přidávají automaticky. Ověřeno v LightBurnu (KAL-05, 2026-10-18).
- **v1.22 (18. 10. 2026):** Na přání vlastníka (diodové lasery) podporovány počátky **vlevo dole a vpravo dole**: roh plnění u počátku (`Corner.BOTTOM_LEFT/BOTTOM_RIGHT` — první řádek dole, další výš, zarovnání v buňce k počátku), umístění do rohu desky u počátku a ruční roh mřížky u počátku i pro spodní rohy; převod souřadnic beze změny. KAL-04 ověřeno vlastníkem 2026-10-18 (testovací zařízení v LightBurnu), upozornění odstraněno (kap. 9.1 bod 4a, `FORMAT_COMPATIBILITY.md`).
- **v1.21 (18. 10. 2026):** Automatická kontrola aktualizací při každém spuštění aplikace, ne jen jednou denně (kap. 32).
- **v1.20 (18. 10. 2026):** Na přání vlastníka je Nastavení modální okno se stránkami (Obecné, Uložení, Aktualizace; OK / Zrušit / Použít) místo rozbalovacího menu; nová volba *Panel rozložení* vlevo / vpravo od náhledu (`ui/panel_side`) (kap. 36.3).
- **v1.19 (18. 10. 2026):** Po uložení titulek a sekce Projekt ukazují naposledy uložený soubor; volba pokračovat s uloženým souborem místo originálu; návrh názvu ze `__grid_NNN` pokračuje v řadě originálu (kap. 9.4).
- **v1.18 (18. 10. 2026):** Na přání vlastníka *Otevřít v LightBurnu* — uložený výstup se otevře programem přiřazeným k `.lbrn2`; LightBurn nahradí otevřený projekt a sám upozorní na neuložené změny (kap. 9.5). Okno aplikace si pamatuje velikost a maximalizaci.
- **v1.17 (18. 10. 2026):** Rozhodnutí vlastníka: repozitář lze zveřejnit už s předběžnými verzemi, aby fungovaly nabízené aktualizace — nová brána PUB-00 (audit historie, MIT `LICENSE`, `THIRD_PARTY_NOTICES.md`, anglický `README`, `SECURITY.md`, vydání jako Pre-release); PUB-01 platí dál pro první veřejnou stabilní verzi 1.0.0 (kap. 29.1, 33.2, 33.3, 35).
- **v1.16 (17. 10. 2026):** Na přání vlastníka předsunuty kopie výrobků (V11-02, kap. 22.2): Ctrl+C / Ctrl+V, Vytvořit kopie… (počet), Odebrat kopie; zápis kopií jako nových skupin se sdílenou geometrií přes `VertID`/`PrimID`, nezávislá kontrola kopií; brána KAL-03.
- **v1.15 (17. 10. 2026):** Na přání vlastníka ruční natočení vybraných výrobků (úhel, ±90°, Automaticky) a výběr výrobku kliknutím v náhledu (kap. 7.6) — např. aby všechny klíčenky měly očko stejně. Rozměr výrobku podle skutečných extrémů Bézierových křivek (kap. 5 bod 2; dříve obal řídicích bodů).
- **v1.14 (17. 10. 2026):** Nativní tvary LightBurnu `Ellipse`, `Rect`, `Polygon` jako obrys i obsah výrobku, včetně vnořených skupin (klíčenky); ověřeno na vzorcích C pro oba lasery, náš přesun je shodný s přesunem v LightBurnu. Brána KAL-02 (mnohoúhelníky N = 3–8, zaoblené rohy, natočená elipsa) splněna — výpočet shodný s LightBurnem na 0,0000 mm. Příznak hladkého uzlu `S` ve `VertList` (kap. 5 body 8–9). Natočení: varianta „nenatáčet nic“ jako výchozí srovnání, čtvercové výrobky bez otočení o 90°, zaokrouhlení na hezký úhel (kap. 7.6).
- **v1.13 (17. 10. 2026):** Na přání vlastníka natočení výrobků pro úsporu materiálu: libovolný úhel (výchozí) / po 90° / nenatáčet, výjimky jednotlivých výrobků, společná orientace podle nejmenší mřížky, zápis `T ∘ XForm` skupiny i `BackupPath` textů s nezávislou kontrolou celé matice (kap. 7.6, ADR-0005); brána KAL-01. Podpora kruhu/elipsy/obdélníku nakreslených přímo v LightBurnu (typy `Ellipse`, `Rect`) čeká na kalibrační soubor.
- **v1.12 (17. 10. 2026):** Na přání vlastníka si uživatel při ukládání volí složku a název výstupu (návrh `__grid_NNN` zůstává); pravidlo „nikdy nepřepsat“ platí i pro zvolený cíl a jeho protokol (kap. 9.4); protokol uložení je volitelný, výchozí neukládat. GUI: nástrojová lišta s ikonami, název projektu v titulku okna, sbalitelné sekce levého panelu s kompaktními poli; **jednotky mm / palce** (Nastavení → Jednotky) jen pro zobrazení a zadávání — jádro, uložená nastavení i soubor `.lbrn2` zůstávají v mm (kap. 12.1).
- **v1.11 (17. 10. 2026):** Na přání vlastníka: (1) hlavní distribucí je instalátor (Inno Setup, per-user, bez práv správce), ZIP zůstává jako záloha, jednosouborové EXE se nepoužívá (kap. 12.1, 31.2); (2) kontrola aktualizací z GitHub Releases — automatická (volitelná, výchozí zapnutá) i ruční, nabídka vždy nejnovější verze s možností zůstat u staré nebo verzi přeskočit, stažení s ověřením SHA-256 a instalace jen po souhlasu (kap. 32, nahrazuje „mimo scope“ z v1.3); (3) verze aplikace `0.1.0-alpha.N` pro interní předběžná vydání.
- **v1.10 (16. 10. 2026):** Po prvním zkušebním rozmístění reálného projektu: (1) umístění mřížky přepínačem — roh počátku laseru (výchozí), střed desky, ručně, podle původní polohy; (2) plnění od rohu počátku laseru (alternativa „čtení“), menší výrobek přiléhá ke straně počátku; (3) deska leží u počátku, výchozí okraj 5 mm, rozměr desky předvyplněn podle laseru (`DeviceName`) z uživatelského nastavení (kap. 6 bod 7, 12.3).
- **v1.9 (16. 10. 2026):** Změny podle zjištění KAL-00 (LightBurn 2.2.00-RC-7, `docs/FORMAT_COMPATIBILITY.md`). (1) Obrys výrobku: libovolný uzavřený řezný tvar, který obsahuje veškerý ostatní obsah skupiny; rozměr = jeho AABB; nahrazuje omezení v1.8 na `Rect`/čtyřúhelník — reálné kartičky mají zaoblené rohy převedené na lomenou čáru (kap. 3.1, 4, 5). (2) Při přesunu skupiny se povinně posouvá i `BackupPath/XForm` textů, protože je ve světových souřadnicích a LightBurn jej takto posouvá (kap. 9.2, 14.3, 21.5). (3) Texty s `BackupPath` jsou měřitelné. (4) Formát čísel `.8g`. (5) Ověřený převod souřadnic podle `MirrorX/MirrorY`; podporované kombinace True/True a False/True, ostatní odmítnout (kap. 8). (6) `VertID`/`PrimID` LightBurn při uložení přečísluje → nejsou stabilní identitou mezi soubory. (7) Počátek laseru se odvozuje z `MirrorX/MirrorY` a GUI zobrazuje `DeviceName` a počátek; uživatel nic nenastavuje (kap. 9.1 bod 4a). (8) Odstup přesouvaných výrobků od nepřesouvaných překážek se kontroluje stejným pravidlem jako mezi výrobky: pár je v pořádku, je-li vodorovná vzdálenost AABB ≥ `gap_x` nebo svislá ≥ `gap_y` (kap. 21.4).
- **v1.8 (16. 10. 2026):** Rozhodnutí před implementací. (1) Sjednoceny názvy: produkt *Grid Arranger for LightBurn*, `GridArranger.exe`, balíček `grid_arranger`, specifikace `docs/specification.md`, matice `docs/FORMAT_COMPATIBILITY.md`. (2) Adaptivní mřížka pro různé rozměry je povinnou součástí MVP; ALG-04 povinný; režim pevné buňky se neimplementuje (kap. 7.3, 21.1). (3) Obrys výrobku: `Rect` nebo uzavřená osově zarovnaná čtyřúhelníková cesta (kap. 4, 5). (4) Obsah s nezměřitelnými hranicemi (typicky text) uvnitř skupiny vyvolá varování, nikoli blokaci; ověřitelná geometrie přesahující obrys dál blokuje (kap. 5). (5) Jádro pracuje v systému s osou Y dolů, převod dělá adaptér podle KAL-00 (kap. 7.1). (6) `gridarranger_en.ts` povinný kvůli množnému číslu (kap. 11, 25.3, 30.1, 36.1). (7) Neaktuální thumbnail je povolená výjimka; doporučen patch přes bajtové pozice z `expat`; zákaz `os.replace` (kap. 9.2, 9.4). (8) Výchozí počátek mřížky = levý horní roh vybraných výrobků (kap. 12.3). (9) Opraveno číslování kap. 16.
- **v1.7 (15. 10. 2026):** Závazně zvolen jediný podporovaný vstupní a výstupní formát `.lbrn2` (FMT-00). Bez větve pro starší `.lbrn`, bez implicitní konverze. Doplněna politika formátů (kap. 41), testovací brána aktuálních souborů a kompatibilitní matice. Opraven chybný odkaz v úvodu na číslo verze specifikace.
- **v1.6 (15. 10. 2026):** Nové závazné požadavky DOC-00 / DOC-01 na průběžnou projektovou a technickou dokumentaci, MVP-08 / HELP-01 na offline uživatelskou příručku integrovanou do aplikace, PLAN-00 na harmonogram a stavový přehled. Doplněna pravidla aktualizace dokumentů s kódem, konkrétní soubory repozitáře, návaznosti, odpovědnost za údržbu, testy T-DOC / T-HELP / T-PLAN a release gate `DOC-REL-01` (kapitoly 37–40). Vytvořeny iniciační šablony roadmapy, stavu a osnovy manuálu.
- **v1.5 (15. 10. 2026):** Osm podporovaných jazyků pro první veřejnou v1.0.0: čeština, angličtina, němčina, slovenština, polština, francouzština, španělština a nově italština. Interní MVP zachovává CS/EN. Upraven výběr automatického jazyka, překladové katalogy, GitHub Release/PUB brány, testy a kontrola úplnosti překladů. Nová brána `L10N-PUBLIC-01` v kap. 36.
- **v1.4 (15. 10. 2026):** Lokalizace jako povinná funkce MVP-07; čeština a angličtina, automatická volba i ruční nastavení jazyka, systém Qt překladů, invariantní `.lbrn2` a numerická data, testy T-I18N a kontrola překladů v GitHub Release procesu (kap. 36 a průběžné odkazy).
- **v1.3 (15. 10. 2026):** Přidána povinná iniciační etapa GIT-00, privátní a veřejná fáze GitHub projektu, praktický postup přes GitHub Desktop, rozlišení čísel verzí dokumentu a aplikace, pravidla větví a vydání, sestavování Windows distribuce, možnost pozdějšího ověření aktualizací, licenční a bezpečnostní kontrolní seznam, release-gates a testovací kritéria (kapitoly 29–35).
- **v1.2 (15. 10. 2026):** Závazný plán funkcí a akceptace: MVP (mřížka, výběr/ruční pořadí, materiál/kolize, bezpečný export), v1.1 (profily, množství, automatické sloupce), v2.0 (více desek, více projektů) a podmíněná budoucí integrace. Přidána ID požadavků, testovací matice, datový model instancí, verzované invariance a rozhodovací brány. Opraven rozpor, kdy ruční řazení a kontrola nepřesouvaných překážek byly ve v1.1 dokumentu odsunuty na později.
- **v1.1 (15. 10. 2026):** Výslovně určen způsob používání aplikace: offline Windows `.exe`, grafické rozhraní PySide6/Qt, bez webového serveru a bez přímého pluginu do LightBurnu. Doplněn krokový uživatelský průchod, uspořádání okna, distribuce a priorita validace před uložení. Výpočetní algoritmus a pravidla bezpečného zápisu zůstávají oproti v1.0 věcně beze změny.


## 29. Správa vývoje na GitHubu — závazná strategie

### 29.1 Cíl a zásady

- GitHub slouží jako **repozitář zdrojového kódu**, historie změn a technické dokumentace. Od v1.11 slouží GitHub Releases zároveň jako zdroj nabízených aktualizací (kap. 32); nic se neinstaluje bez souhlasu uživatele.
- Repoziář se zakládá jako **Private** a zůstává neveřejný během vývoje i interních testů. Žádné veřejné sliby, vývojové termíny či žádost o začlenění do LightBurnu nejsou podmínkou vydání.
- Veřejný přístup (**Public**) smí vlastník zapnout pouze explicitním rozhodnutím po úspěchu brány **PUB-00** (veřejný repozitář s předběžnými verzemi, kap. 33.2; rozhodnutí vlastníka 18. 10. 2026); první veřejná stabilní verze 1.0.0 navíc vyžaduje PUB-01. Zveřejnění historie a artefaktů je třeba předem prověřit.
- GitHub účet a historie projektu jsou vlastnictvím autora. Vydání nové verze se provádí **vědomým potvrzením** po testování, ne automaticky po každém uložení kódu.
- Pro správu Gitu použít primárně **GitHub Desktop**, aby běžná práce nevyžadovala terminál. Pokročilé funkce, které Desktop neumí, lze provést na webu GitHubu či připravenou automatizací.

### 29.2 Založení soukromého projektu — postup pro začátečníka (milník GIT-00)

1. Založit GitHub účet, nastavit **dvoufaktorové ověření** (preferovaně authenticator / passkey).
2. Nainstalovat GitHub Desktop a přihlásit se.
3. `File → New repository`, například `lightburn-grid-arranger`; zapnout `Initialize this repository with a README`.
4. Zvolit lokální pracovní složku mimo složky obsahující klientské zakázky či osobní data.
5. První commit obsahuje `README.md`, `.gitignore`, aktuální technickou specifikaci a přiměřené interní informace. V GitHub Desktop použít `Commit to main`.
6. Zvolit `Publish repository` a **ponechat zapnuté `Keep this code private`**. Zkontrolovat na webu `Private`.
7. Před každým `Commit` zkontrolovat seznam souborů a rozdíly; kliknout `Push origin`, aby se změny odeslaly i na GitHub.

**Slovníček:** *repository* = složka projektu s historií; *commit* = uložený kontrolní bod změn; *push* = nahrání commitů na GitHub; *branch* = pracovní větev; *tag* = štítek neměnného bodu historie; *Release* = publikovaná verze programu s popisem a binárními soubory.

### 29.3 Doporučený pracovní model

- `main` je hlavní větev. Při samostatném vývoji je přijatelné začít přímo na ní; změny ale musejí vždy projít alespoň příslušnými testy.
- Jakmile program začne mít více modulů nebo se očekávají zásahy s rizikem regrese, používat krátkodobé větve `feature/grid-order`, `fix/xform-roundtrip`, `feature/profiles` a začleňovat je přes Pull Request.
- Jedna logická změna = jeden čitelný commit; neukládat do Gitu velké dočasné výstupy a binární buildy.
- Každá funkce z původní specifikace používá ID (`MVP-01`, `V11-02`...), aby šla dohledat ve změnách, testech a release notes.
- Po každém úspěšném pracovním bloku lze vytvořit commit. To neznamená, že se současně vydává nová verze aplikace.

## 30. Struktura GitHub repozitáře a pravidla verzování

### 30.1 Doporučená struktura

```text
lightburn-grid-arranger/
├── README.md                    # co projekt umí a co zatím neumí
├── LICENSE                      # zvolená licence až při připravenosti ke zveřejnění
├── CHANGELOG.md                 # změny vydaných verzí
├── CONTRIBUTING.md              # jak nabídnout kód/překlad; veřejná fáze
├── docs/TRANSLATING.md          # překlady, glosář, kontrola a ověření
├── COMPATIBILITY.md             # ověřené verze LightBurnu + omezení formátu
├── SECURITY.md                  # bezpečnost a odpovědné hlášení problému
├── THIRD_PARTY_NOTICES.md       # licence používaných knihoven
├── .gitignore                   # nezveřejňované/dočasné soubory
├── pyproject.toml               # závislosti, testy, nastavení nástrojů
├── src/grid_arranger/
│   ├── __init__.py
│   ├── __main__.py
│   ├── version.py               # jediné zdrojové číslo verze aplikace
│   ├── core/                    # nezávislý algoritmus
│   ├── lightburn/               # adaptér / validace LBRN2
│   ├── gui/                     # PySide6, vizualizace a uživatelská akce (vč. help/)
│   ├── i18n/                    # načítání katalogů a formátování sdělení
│   └── settings/                # uložená uživatelská jazyková volba
├── translations/
│   ├── gridarranger_cs.ts       # český katalog (interní MVP)
│   ├── gridarranger_en.ts       # anglické tvary množného čísla (interní MVP)
│   ├── gridarranger_de.ts       # DE pro veřejné vydání
│   ├── gridarranger_sk.ts       # SK pro veřejné vydání
│   ├── gridarranger_pl.ts       # PL pro veřejné vydání
│   ├── gridarranger_fr.ts       # FR pro veřejné vydání
│   ├── gridarranger_es.ts       # ES pro veřejné vydání
│   └── gridarranger_it.ts       # IT pro veřejné vydání
├── tests/
│   ├── i18n/                    # testy dostupnosti katalogů a jazyků
│   ├── unit/                    # matematika, model, serializace
│   ├── integration/             # round-trip a validace projektů
│   └── fixtures/synthetic/     # pouze uměle vytvořená testovací data
├── docs/
│   ├── specification.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── FORMAT_COMPATIBILITY.md
│   ├── TEST_PLAN.md
│   ├── ROADMAP.md
│   ├── STATUS.md
│   ├── RELEASE_CHECKLIST.md
│   ├── DECISIONS/               # ADR záznamy
│   ├── manual/                  # lokalizovaná offline nápověda (cs/en/de/sk/pl/fr/es/it)
│   ├── release-process.md
│   └── test-plan.md
└── .github/
    └── workflows/              # CI a sestavení EXE: zavést až po funkčním prototypu
```

Toto je cílová struktura; prázdné složky a nehotové workflow není třeba vytvářet hned. Dokumentace může být zpočátku česky; **před veřejným vydáním musí být k dispozici anglický základní `README.md` a pokyny k instalaci**. Překlady CS/EN jsou povinné již v interním MVP; před prvním veřejným vydáním je závazně osm jazyků. Další komunitní jazyky nad tento rozsah jsou volitelné (kap. 36).

### 30.2 Pravidla pro `.gitignore` a testovací data

- Necommitovat `.venv/`, `__pycache__/`, `build/`, `dist/`, `*.log`, lokální konfigurace a projektové soubory zákazníků.
- Soukromé produkční `.lbrn2` soubory ukládat mimo pracovní repo. Ani privátní GitHub není určen pro dokumenty třetích stran bez oprávnění.
- Reálné integrační testy provádět na souborech uložených **lokálně a mimo Git**. V repozitáři mohou být jen výslovně schválené, uměle vytvořené, neobsahující citlivá data.
- Do Gitu neukládat osobní tokeny, přihlašovací údaje, podpisové certifikáty či hesla.
- `.gitignore` nepomůže se souborem, který už byl commitnut: před budoucím zveřejněním je nutné prověřit i **celou historii**.

### 30.3 Oddělené verzování

Verze specifikace a verze aplikace jsou **nezávislé**:

- `docs/...v1_6.md` = verze požadavkového dokumentu.
- `APP_VERSION = "0.1.0"` = verze implementovaného programu.
- `v0.1.0-alpha.1` = interní či označené předběžné sestavení.
- `v1.0.0` = první stabilní veřejné MVP, **až bude skutečně prověřeno**.
- `v1.1.0` = funkční rozšíření dle požadavků V11; `v1.1.1` = zpětně kompatibilní oprava; `v2.0.0` = další plánovaný celek nebo významná nekompatibilní změna.

Používat princip Semantic Versioning (MAJOR.MINOR.PATCH), předběžné verze označovat příponou `-alpha.N`, `-beta.N` nebo `-rc.N`. Číslo je jediným zdrojem pravdy pro GUI, sestavení, release notes a názvy balíčků. Stabilní `v1.0.0` nesmí označovat nedokončené MVP jen proto, že má GUI.

## 31. Výroba, testování a distribuce Windows aplikace

### 31.1 Dvě oddělené pipelines

**Pipeline CI (automatická kontrola kódu):** po odeslání změny spustit jednotkové testy, statickou kontrolu, kontrolu překladů (`.ts` → `.qm`, chybějící kritické řetězce/placeholdery) a bezpečnou syntaktickou validaci. Později na GitHub Actions: `push` a `pull_request`. GitHub automaticky **nemůže** potvrdit, že zpracovaný výrobní projekt funguje v aktuálním LightBurnu a na laseru. To je povinná ruční integrační kontrola.

**Pipeline Release (sestavení distribuce):** sestavit aplikaci na Windows prostředí z konkrétního commitu/tagu, výstup otestovat na čistém Windows počítači, ověřit kontrolní součet SHA-256 a připravit vydání jako koncept. Publikovat pouze ručně po potvrzení release-gate.

### 31.2 Formát distribuce

**Výstupy každého vydání (v1.11):** (1) instalátor `GridArranger-Setup-v1.0.0-win-x64.exe` (Inno Setup; per-user, bez práv správce, stálé `AppId`, před instalací odstraní `_internal` předchozí verze, uživatelské nastavení v registru HKCU zůstává), (2) záložní přenosný ZIP `GridArranger-v1.0.0-win-x64.zip`, (3) `SHA256SUMS.txt` se součty obou. Žádný výstup nevyžaduje Python ani administrátorská oprávnění. `onefile` EXE se nepoužívá. Licenční povinnosti PySide6/Qt (LGPL) splňuje oddělené umístění knihoven v `_internal` a `THIRD_PARTY_NOTICES.txt`; před veřejným vydáním ověřit v rámci PUB-01.

- Pro PySide6 lze použít `pyside6-deploy` (Qt uvádí tento nástroj jako doporučenou možnost) nebo jiný ověřený balicí nástroj; volbu uzamknout až po experimentálním build testu.
- BIN soubory `dist/` neukládat do hlavní větve; **distribuční ZIP přikládat až k GitHub Release**.
- V ZIP připojit `README.txt`, `LICENSES/` či odpovídající informace o třetích stranách, případně `SHA256SUMS.txt` vedle stažitelného ZIPu. V interním MVP musí být přibalen český `.qm` katalog a anglický zdrojový jazyk; **první veřejný v1.0.0 musí přibalit `cs/de/sk/pl/fr/es/it` `.qm` katalogy a mít anglické zdrojové texty**. Ověřit osm jazyků na čistém PC bez internetu.
- Windows může na nepodepsanou aplikaci upozornit. Neobcházet SmartScreen a nepožadovat vypínání antiviru; digitální podpis zvážit až při pravidelné veřejné distribuci.

### 31.3 Proces pro vydání každé verze

1. Vybrat přesný commit odpovídající dokončené verzi a opravit blokující chyby.
2. Spustit všechny požadované automatické testy a ruční integrační testy s kopií `.lbrn2` v LightBurnu; zapsat výsledek.
3. Zkontrolovat `CHANGELOG.md`, `COMPATIBILITY.md`, licence, seznam známých omezení a **úplnost překladů všech jazyků požadovaných pro daný typ vydání** (interní MVP CS/EN, první veřejné v1.0.0 všech osm), zejména bezpečnostních hlášek; po změnách UI znovu vygenerovat `.ts/.qm`.
4. Vytvořit tag např. `v1.0.0` (jednoznačně identifikuje zdrojový kód).
5. Ze stejného tagu sestavit Windows ZIP; na jiném PC nebo čistém testovacím prostředí ověřit jeho spuštění a základní scénáře.
6. Na GitHubu vytvořit `Draft a new release`, připojit ZIP a kontrolní součty, zapsat změny a varování; interní verze mohou zůstat v privátním repozitáři.
7. Po splnění brány PUB-01/REL-01 ručně vydat release. Testovací veřejné sestavení označit jako **Pre-release**, nikoli stabilní.
8. V budoucnu vydávat nové verze pod **novými tagy**; nepřepisovat zpětně distribuovaný ZIP pod stejným číslem.

### 31.4 Minimální release notes

```text
Verze: v1.1.1
Datum vydání: YYYY-MM-DD
Co je nového: oprava přesnosti umístění v konkrétním scénáři
Opraveno: popis opravené chyby
Kompatibilita: ověřené verze LightBurnu / podporované soubory
Známá omezení: typy projektů, které adaptér záměrně odmítne
Instalace/aktualizace: stáhnout ZIP, rozbalit; zálohovat vlastní nastavení
Bezpečnost: výstup vždy ověřit v LightBurnu před výrobou
```

## 32. Uživatelské aktualizace programu

### 32.1 Zásady (v1.11)

- **Žádné tiché aktualizace.** Aplikace novou verzi pouze **nabídne**; stažení i instalace proběhnou až po výslovném souhlasu uživatele. Uživatel může zůstat u stávající verze.
- Uživatelská nastavení se ukládají mimo složku aplikace (registr HKCU přes `QSettings`), takže přežijí aktualizaci, přeinstalaci i výměnu ZIPu. Při každém vydání uvést, zda se mění formát nastavení či podporované typy `.lbrn2`.
- V menu `Nápověda → O aplikaci` zobrazovat číslo verze.
- Výrobní funkce nesmějí být nikdy omezeny nedostupností sítě nebo GitHubu.

### 32.2 Kontrola aktualizací

- **Nastavení → Aktualizace:** „Automaticky kontrolovat aktualizace“ (výchozí zapnuto) a „Nabízet i předběžné verze“ (výchozí zapnuto, pokud je běžící verze předběžná). **Nápověda → Zkontrolovat aktualizace…** kdykoli ručně.
- Automatická kontrola proběhne na pozadí **při každém spuštění** (v1.21, přání vlastníka; dříve nejvýš jednou za ~20 hodin — jeden anonymní dotaz na GitHub API, limit 60 dotazů za hodinu na IP adresu nevadí); chyby sítě/API zaznamená bez rušení uživatele. Ruční kontrola chybu srozumitelně oznámí (offline, GitHub nedostupný, omezení počtu dotazů, žádná veřejná vydání).
- Zdroj: oficiální GitHub API `GET /repos/Knapis522/lightburn-grid-arranger/releases`, anonymně (bez tokenu v aplikaci). Funguje až po zveřejnění repozitáře (PUB-00); do té doby ruční kontrola oznámí, že vydání nejsou veřejná. Koncepty (draft) se ignorují; předběžné verze jen při zapnutém kanálu.
- Porovnání podle Semantic Versioning 2.0 včetně předběžných verzí (`-alpha.N` < `-beta.N` < `-rc.N` < vydání).
- **Vždy se nabízí nejnovější vydání**; každý instalátor obsahuje celou aplikaci, mezilehlé verze se neinstalují. Dialog ukáže přehled změn všech vydání novějších než nainstalovaná verze a volby **Stáhnout a nainstalovat** / **Připomenout později** / **Přeskočit tuto verzi**. Přeskočená verze se při automatické kontrole znovu nenabízí, novější ano; ruční kontrola ukáže i přeskočenou.
- Odesílaná data: jen běžný HTTPS dotaz s hlavičkou `User-Agent: GridArranger/<verze>`; žádné údaje o projektech, souborech ani uživateli.

### 32.3 Stažení a instalace

- Automaticky instalovat lze jen kopii nainstalovanou instalátorem (vedle EXE je `unins000.exe`). Kopie ze ZIPu a vývojové spuštění nabídnou jen **Otevřít stránku ke stažení**.
- Instalátor se stáhne do nové dočasné složky a ověří proti `SHA256SUMS.txt` téhož vydání; při chybějícím součtu nebo neshodě se smaže a **nespustí**. Stahování lze zrušit.
- Po ověření se aplikace ukončí a spustí instalátor (`/SILENT`, bez dotazů, s ukazatelem průběhu, bez práv správce); instalátor nahradí soubory a aplikaci znovu spustí. Běžící EXE se nikdy nepřepisuje za běhu.
- Digitální podpis instalátoru zvážit před pravidelnou veřejnou distribucí (SmartScreen); do té doby je integrita chráněna HTTPS a SHA-256 z téhož GitHub Release.

### 32.4 Testy aktualizací

| ID | Scénář | Očekávaný výsledek |
|---|---|---|
| T-UPD-01 | Porovnání verzí včetně předběžných | Pořadí podle SemVer 2.0 |
| T-UPD-02 | Více novějších vydání, uživatel dříve odmítl | Nabídne se jen nejnovější, přehled změn obsahuje všechna novější |
| T-UPD-03 | Přeskočená verze | Automatická kontrola ji nenabídne, novější ano, ruční ji ukáže |
| T-UPD-04 | Offline / 404 / 403 / neplatná odpověď | Automatická kontrola mlčí, ruční srozumitelně oznámí; práce s projekty pokračuje |
| T-UPD-05 | Poškozený instalátor nebo chybějící součet | Nic se nespustí, soubor se smaže |
| T-UPD-06 | Kopie ze ZIPu | Nabídne jen stránku ke stažení |
| T-UPD-07 | Aktualizace nainstalované verze na Windows | Aplikace se zavře, nainstaluje se nová verze do stejné složky, znovu se spustí, nastavení zůstane |
| T-UPD-08 | Automatická kontrola vypnuta | Žádný síťový dotaz |

## 33. Brány pro zveřejnění a pravidla bezpečnosti

### 33.1 REL-01 — každé vydání

**Povinné před release:**

- Pro interní MVP úspěšné T-I18N-01 až 16 a kompletní CS/EN bezpečnostní hlášky; pro **veřejné v1.0.0 a další veřejné verze** navíc úspěšné T-I18N-17 až 22 a `L10N-PUBLIC-01` pro všech osm jazyků. Ověřovat skutečně sestavený Windows ZIP.

- Testy odpovídající rozsahu verze (MVP-*, V11-*, V20-*) úspěšné a zdokumentované.
- Počet výrobků, geometrie, `CutIndex`, `CutSetting`, obsah projektu a nevybrané skupiny splňují invarianty z kap. 20–26.
- Původní testovací soubor zůstává byte-identický. Výstup lze otevřít v ověřené verzi LightBurnu; Preview zkontrolováno.
- Zůstává blokován každý typ projektu, který adaptér neumí bezpečně zpracovat.
- Distribuce je otestována na Windows **bez instalovaného Pythonu**.
- `APP_VERSION`, Git tag, názvy instalátoru a ZIPu a release notes odpovídají stejné verzi; ke Release je přiložen `SHA256SUMS.txt` se součty obou (bez něj aplikace aktualizaci neinstaluje).
- Kontrolní součet SHA-256 staženého artefaktu byl porovnán s vypočteným po sestavení.
- Je připravena srozumitelná upozornění na známá omezení a na potřebu kontroly v LightBurnu před řezáním.

### 33.2 PUB-00 — veřejný repozitář s předběžnými verzemi (v1.17, rozhodnutí vlastníka 18. 10. 2026)

Důvod: nabízené aktualizace (kap. 32) fungují jen z veřejných GitHub Releases; aplikace nesmí obsahovat token. Repozitář lze proto zveřejnit už ve fázi interních předběžných verzí (alpha/beta), pokud jsou splněny body:

1. Autor výslovně schválí zveřejnění.
2. **Audit celé Git historie** (bod 2 PUB-01) — žádné zákaznické projekty, osobní údaje, tokeny, interní firemní dokumenty ani cizí grafika.
3. `LICENSE` vlastního kódu (MIT), `THIRD_PARTY_NOTICES.md` a licence přibalená k sestavení.
4. Anglický `README`: účel, stav **alpha**, instalace, podporované projekty, omezení, nutnost kontroly v LightBurnu, neoficiálnost a ochranná známka.
5. `SECURITY.md`: co aplikace dělá na počítači a v síti, jak hlásit problémy.
6. Vydání zůstávají **Pre-release**; release notes uvádějí omezení.

Brána PUB-00 **nenahrazuje** PUB-01: první veřejná stabilní verze 1.0.0 musí splnit PUB-01 celou (MVP-ACCEPT, `L10N-PUBLIC-01` pro osm jazyků, úplná dokumentace a nezávisle otestovaná instalace).

### 33.3 PUB-01 — brána před první veřejnou stabilní verzí 1.0.0

1. Autor schválí, že chce projekt veřejně zveřejnit; neveřejný vývoj není selhání.
2. **Audit celé Git historie**, nejen aktuálních souborů: žádné zákaznické projekty, osobní údaje, tokeny, interní firemní dokumenty, problematické grafické podklady či neautorizované binární součásti.
3. Ověřeny autorské a licenční podmínky veškerého vlastní/cizího kódu a balených knihoven. Návrh MIT pro **vlastní zdrojový kód**, pokud bude s použitými závislostmi slučitelný; licence PySide6/Qt (LGPLv3/GPL/komerční) je nutno samostatně dodržet včetně distribučních povinností.
4. `README` vysvětluje účel, stav podporovaných funkcí, instalaci, podporované formáty, omezení a rizika; neprohlašuje projekt za oficiální produkt LightBurnu.
5. Připravit `LICENSE`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`, `COMPATIBILITY.md`, `SECURITY.md`, **anglický návod a `docs/TRANSLATING.md`** a vestavěný manuál ověřený dle `HELP-01`; zkontrolovat cizí ochranné známky a nepoužívat oficiální logo LightBurnu bez oprávnění.
6. Veřejné vydání projde REL-01, `L10N-PUBLIC-01` (všech osm jazyků) a nezávisle otestovanou instalací/spuštěním z distribučního ZIPu.
7. Teprve pak změnit `Settings → Danger Zone → Change repository visibility → Public` a následně zveřejnit schválený Release. Uživatel musí počítat s veřejností dosavadní historie a workflow logů.

**Zásadní poznámka:** Software používající `.lbrn2` nevytváří oficiální podporu LightBurnu; přímý zápis souborů zůstává neoficiální a musí být veřejně popsán jako experimentálně kompatibilní jen s otestovanými verzemi.

## 34. Akceptační testy pro správu verzí a distribuci

**GIT-00 je splněno pouze při úspěchu GH-01 a GH-02**, kontrole nastavení `Private` a prověrce, že v seznamu verzovaných souborů nejsou žádné zákaznické projekty, tajné údaje ani lokální výrobní soubory. Splnění zaznamenat před první programátorskou etapou.

| ID | Scénář | Očekávaný výsledek |
|---|---|---|
| GH-01 | Založení repozitáře přes GitHub Desktop a `Publish repository` s `Keep this code private` | Na webu je označen `Private`, bez přístupu nepovolaných osob |
| GH-02 | Úprava kódu, `Commit`, potom `Push origin` | Změna je viditelná v historii lokálně i na GitHubu; lze ji dohledat |
| GH-03 | Vytvoření dvou pracovních commitů bez release | Historie se změnila, číslo veřejné verze nikoliv |
| GH-04 | Git projekt obsahuje `.venv`, `dist`, lokální `.lbrn2` zákazníka | `.gitignore` a kontrola souborů zabrání nechtěnému přidání; zkontrolovat i historii |
| GH-05 | Sestavení EXE/ZIP na čistém Windows | Aplikace funguje bez Pythonu a závislostí instalovaných pro vývoj |
| GH-06 | Tag `v1.1.1` a ZIP stejné verze | GUI, tag, soubor, metadata a notes se shodují |
| GH-07 | Testovaný ZIP se přiloží do Draft Release | Není veřejně vydán dříve než po schválení |
| GH-08 | Neúspěšný integrační test LightBurnu | REL-01 selže; release není označen za stabilní |
| GH-09 | V archivu se objeví cizí zakázka / token | PUB-01 blokuje zveřejnění, dokud není problém bezpečně vyřešen v celé historii |
| GH-10 | Offline režim a žádná kontrola aktualizací | Veškerá základní funkčnost aplikace funguje bez sítě |
| GH-11 | Ruční kontrola aktualizací: dostupná vyšší stabilní verze | Uživateli se ukáže verze, changelog a oficiální stránka Release; nic se samo neinstaluje |
| GH-12 | GitHub API nedostupné či požadavek selže | Pouze neblokující hláška, bez ovlivnění projektu nebo výroby |
| GH-13 | Starší uživatelské profily při aktualizaci 1.1+ | Zachovány nebo bezpečně migrovány; nikdy nedochází k tiché ztrátě nastavení |
| GH-14 | Projekt zůstane navždy soukromý | Všechny interní vývojové a testovací postupy nadále fungují bez veřejné publikace |
| GH-15 | Nový release obsahuje změněné řetězce UI | Interně CS/EN, veřejně osm jazyků; překladové katalogy, placeholdery a kritické texty ověřeny, chybějící povinný překlad blokuje REL-01 |
| GH-16 | Stažená Windows distribuce a nabídka jazyků | Interně CS/EN, veřejně všech osm jazyků včetně Italiano; jazyk lze změnit offline bez Pythonu a stahování překladů |

## 35. Doporučené pořadí zavádění GitHub nástrojů

- **Při zahájení vývoje — povinné etapy GIT-00 + DOC-00:** GitHub účet + 2FA, GitHub Desktop, privátní repo, `.gitignore`, základní `README`, kopie aktuální technické specifikace; ověřit commit, push a viditelnost `Private`.
- **Po prvním funkčním algoritmu:** pravidelné commity, jednotkové testy, `CHANGELOG.md`, samostatný soubor s číslem verze aplikace.
- **Po úspěchu KAL-00 a před MVP:** zahrnout `MVP-07` (základ i18n), Qt katalogy a testy T-I18N; GitHub Actions pro automatické testy; volitelně jednoduché pracovní větve; lokální balení Windows ZIP a samostatné testování.
- **Před soukromým kandidátem na vydání:** reprodukovatelný build, kontrolní součet, draft interního GitHub Release, `COMPATIBILITY.md` a protokol o ručním testování v LightBurnu.
- **Před zveřejněním repozitáře s předběžnými verzemi:** PUB-00 (kap. 33.2).
- **Před veřejným stabilním vydáním 1.0.0:** PUB-01 + `L10N-PUBLIC-01` pro všech osm jazyků (včetně italštiny), licence a třetí strany, bezpečnostní a historický audit, návod a release notes; poté teprve přepnout viditelnost.
- **Od v1.11 (interně, funkční po zveřejnění vydání):** automatická i ruční kontrola aktualizací, instalace jen po souhlasu uživatele a ověření SHA-256 (kap. 32); tichá automatická instalace se neplánuje.

### Referenční zdroje pro GitHub proces

- GitHub Desktop, založení a publikování projektu: https://docs.github.com/en/desktop/overview/creating-your-first-repository-using-github-desktop
- GitHub, změna viditelnosti repozitáře a upozornění na důsledky: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility
- GitHub, Releases a tagy: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- GitHub, ruční vytvoření Release: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- GitHub, ochrana a odstranění citlivých dat z historie: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- Qt for Python, nástroj `pyside6-deploy`: https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html
- Qt for Python, licenční informace: https://doc.qt.io/qtforpython-6/licensing.html


## 36. Lokalizace a mezinárodní distribuce — MVP-07 (závazné)

### 36.1 Účel, rozsah a podporované jazyky

**Cíl:** Připravit aplikaci od první obrazovky na lokalizaci bez vazby překladů na matematiku, data výrobků nebo formát `.lbrn2`. `MVP-07` znamená interní dvoujazyčné MVP a **závazný požadavek osmi jazyků nejpozději pro první veřejné stabilní vydání v1.0.0**. GitHub repozitář může zůstat soukromý až do splnění ostatních publikačních bran.

| Kód pro nastavení | Název v nabídce | Systémová locale (příklad) | Dostupnost | Implementace |
|---|---|---|---|---|
| `cs` | Čeština | `cs-CZ` | Interní MVP a veřejné vydání | `gridarranger_cs.ts/.qm` |
| `en` | English | `en-US`, `en-GB` | Interní MVP a veřejné vydání | **Výchozí zdrojový jazyk**; `gridarranger_en.ts/.qm` **povinný** pro správné anglické tvary množného čísla (Qt bez něj zobrazí např. „1 item(s)“) |
| `de` | Deutsch | `de-DE`, `de-AT` | První veřejné v1.0.0 | `gridarranger_de.ts/.qm` |
| `sk` | Slovenčina | `sk-SK` | První veřejné v1.0.0 | `gridarranger_sk.ts/.qm` |
| `pl` | Polski | `pl-PL` | První veřejné v1.0.0 | `gridarranger_pl.ts/.qm` |
| `fr` | Français | `fr-FR`, `fr-CA` | První veřejné v1.0.0 | `gridarranger_fr.ts/.qm` |
| `es` | Español | `es-ES`, `es-MX` | První veřejné v1.0.0 | `gridarranger_es.ts/.qm` |
| `it` | Italiano | `it-IT` | První veřejné v1.0.0 | `gridarranger_it.ts/.qm` |

**Rozhodnutí:** Pro první veřejné vydání je závazných **osm** jazyků; italština patří do stejné prioritní skupiny jako němčina, slovenština, polština, francouzština a španělština. Prototyp lze mezitím interně zkoušet v CS/EN. Další jazyky (např. portugalština, nizozemština) jsou až volitelný výhled. U každého veřejně podporovaného jazyka platí stejné bezpečnostní a funkční požadavky.

### 36.2 Uživatelské chování (výběr a automatická detekce)

1. Volba **Nastavení → Jazyk / Settings → Language** (od v1.20 v okně Nastavení, stránka Obecné) je přístupná i bez otevřeného projektu. Položky: `Automaticky (podle systému)`, `Čeština`, `English`, `Deutsch`, `Slovenčina`, `Polski`, `Français`, `Español`, `Italiano` (interní MVP smí mít zatím jen dostupné CS/EN). Jazyky jsou zobrazeny vlastním názvem, takže se uživatel z chybně zvolené lokalizace snadno vrátí.
2. Výchozí nastavení je `auto`. Aplikace načte seznam preferovaných jazyků Windows, vybere první podporovaný jazyk z `cs/en/de/sk/pl/fr/es/it` (v interním MVP `cs/en`). Regionální varianty se normalizují: např. `de-AT → de`, `es-MX → es`. U nepodporovaného jazyka použít `en`; neexistující nebo poškozený katalog nesmí způsobit pád.
3. Ruční výběr jazyka má před systémovou detekcí přednost a přetrvá restart, přesun ZIP složky i aktualizaci programu. Přepnutí zpět na `auto` obnoví automatickou detekci.
4. Preferováno je přepnutí celé aplikace **za běhu**. Jestliže konkrétní komponentu nelze bezpečně přeložit, smí aplikace vyžadovat restart se srozumitelným upozorněním, ale nikdy nesmí potichu zahodit neuložený projekt, výběr skupin či nastavené parametry.
5. Lokalizovat úplně všechna menu, dialogy, popisky, prázdné stavy, tooltipy, stavové zprávy, varování při kolizi a přesahu materiálu, chyby souboru, bezpečnostní upozornění, názvy ovládacích prvků i viditelné texty budoucích verzí 1.1 a 2.0. Nepřekládá se **obsah uživatelských výrobků**, názvy skupin, názvy a cesty souborů ani identifikátory.
6. Angličtina je **bezpečný runtime fallback**. Během vývoje pomůže přežít chybějící překlad; **před veřejným vydáním však nemá nahrazovat nedokončené povinné katalogy**.
7. Jazyky jsou plně **offline**. Nevyžadovat účet, stahování překladů ani síťový překladač.

### 36.3 Technická implementace — PySide6/Qt

- Angličtina je kanonický zdrojový jazyk: GUI používá `self.tr(...)` nebo `QCoreApplication.translate(...)`, ne natvrdo zapsané české řetězce a překlady ve výpočetní logice.
- Překladové katalogy jako zdrojové `translations/gridarranger_<kód>.ts`; při buildu `pyside6-lrelease` vytvoří `.qm`, které se bezpečně přibalí k EXE. `pyside6-lupdate` udržuje katalogy po změnách UI. Aktualizace katalogů musí být součástí procesu sestavení a CI.
- Přepínání soustředit do `LocaleManager` (`QTranslator` a `QLocale`, překladač držet po celou dobu používání). Formátování hodnot v GUI používat přes Qt lokalizované číselné ovládací prvky; jádro a adaptér Qt nepoužívají.
- Uložené nastavení `ui_language` = `auto|cs|en|de|sk|pl|fr|es|it` přes `QSettings` či `QStandardPaths.AppConfigLocation`. Nepatří do `.lbrn2`, nezasahuje do výrobních profilů ani strojových parametrů.
- Každý katalog musí správně mapovat `placeholdery`, proměnné a množná čísla. Neprovádět překlad jednotlivých slov skládáním gramaticky nepřesných vět. Testovat mimo jiné počty `0, 1, 2, 5, 21`; doplnit specifické kontroly množného čísla pro `cs`, `sk`, `pl` i příslušné další jazyky.
- V `docs/TRANSLATING.md` popsat editaci `.ts` v Qt Linguist, aktualizaci, kontrolu překladů, sestavení `.qm` a cestu k Pull Requestu. Příspěvky komunity podléhají revizi a testům.
- K překladům lze využít strojový návrh, ale **bez lidské revize významu a terminologie nelze prohlásit jazyk za ověřený**; obzvlášť kontrolovat provozní varování a odlišnosti například „mezera“, „rozteč“, „obrys“, „materiál“, „kolize“, „uložit nový projekt“.

**Referenční dokumentace Qt:** https://doc.qt.io/qtforpython-6/tutorials/basictutorial/translations.html ; https://doc.qt.io/qtforpython-6/PySide6/QtCore/QTranslator.html ; https://doc.qt.io/qtforpython-6/PySide6/QtCore/QStandardPaths.html

### 36.4 Numerické hodnoty a výrobní data jsou jazykově invariantní

**Žádná volba jazyka nesmí změnit výsledek výpočtu ani jediný bajt výrobního projektu (při identickém vstupu a deterministickém serializéru).**

- Mezery, šířky, výšky a souřadnice jsou interně numerické hodnoty v mm. V GUI mohou mít podle locale desetinnou **čárku nebo tečku**, ale v `XForm`, `.lbrn2` a strojových JSON schématech se používá invariantní reprezentace se **tečkou**.
- Vstup `3,5` v češtině, němčině, slovenštině, polštině, francouzštině, španělštině či italštině a `3.5` v angličtině má po správném naparsování dát **stejnou hodnotu 3.5 mm**. Parsování musí respektovat skutečnou `QLocale`, bez automatického hádání nejednoznačných tisícových oddělovačů.
- Přepnutí jazyka pouze aktualizuje textové podání, nikoliv význam parametru či již vypočtené pozice výrobků.
- Stabilní klíče (`profile_id`, `schema_version`, `error_code`) a obsah výrobků se nikdy nepřekládají. Lokalizované chybové věty se tvoří až v UI z kódu chyby a parametrů.
- Dva exporty ze stejného projektu, se stejnými numerickými parametry a pořadím skupin musejí mít stejné pozice i obsah bez ohledu na `cs/en/de/sk/pl/fr/es/it`.

### 36.5 Pravidla publikace a správy překladů

- **Interní MVP:** kompletní `cs` a `en` včetně všech bezpečnostně důležitých dialogů. Tím je splněna první vývojová část `MVP-07`, ale **nikoliv jazyková brána pro veřejné vydání**.
- **První veřejné stabilní vydání v1.0.0:** osm jazyků v tabulce 36.1, včetně `it`; anglický `README.md`, základní bezpečnostní instrukce, `CHANGELOG.md`, `COMPATIBILITY.md`, `docs/TRANSLATING.md`. Další překlady dokumentace lze rozšiřovat postupně; bezpečnostní výstrahy uvnitř aplikace musí být úplné v osmi jazycích.
- Při každé změně UI před veřejným releasem aktualizovat `.ts`, překontrolovat úplnost a placeholdery, sestavit `.qm` a otestovat skutečný Windows ZIP. Překlad přidaného kritického hlášení je povinný ve všech osmi jazycích. Neúplný překlad blokuje release, i pokud samotné výpočetní testy prošly.
- Před označením konkrétního katalogu za hotový provést **jazykovou revizi člověkem se znalostí daného jazyka a laserové terminologie**, případně odpovídající odbornou kontrolu; při nedostatku revize nevydávat „plně podporovaný“ jazyk. V takovém případě veřejné vydání **odložit nebo výslovně změnit plán a specifikaci**, nikoliv bez upozornění zveřejnit neověřený překlad.
- Pro dobrovolnické překladatele používat GitHub Pull Requests. Nepřebírat překlady automaticky, ověřit právní oprávnění přispěvatele a licenční podmínky příspěvku.

**Stav k v1.26 (18. 10. 2026):** Katalogy `gridarranger_{de,sk,pl,fr,es,it}.ts` jsou úplné (všechny řetězce, placeholdery a tvary množného čísla — `sk`/`pl` tři tvary, ostatní dva), `.qm` se sestavují a balí; offline příručka (8 témat) existuje ve všech osmi jazycích a na stránce *Verze* nese poznámku o strojovém překladu. Překlad vytvořila AI podle anglického zdroje a terminologie z `docs/TRANSLATING.md`; **jazyková revize člověkem chybí**, takže tyto jazyky jsou v předběžných verzích (`alpha`) k dispozici jako náhled a nejsou „plně podporované“. Do revize všech šesti jazyků nelze splnit `L10N-PUBLIC-01`. Automaticky ověřeno: T-I18N-17 (načtení offline), T-I18N-18 (detekce), T-I18N-19 (úplnost a placeholdery strojově; jazyková část čeká), T-I18N-20 (stejný výstup v osmi jazycích); T-I18N-21 snímky obrazovky offscreen (de/pl/fr/es/it, okno 1024 × 700) bez useknutých textů — na Windows ověřit ručně.

### 36.6 Akceptační testy lokalizace

| ID | Scénář | Očekávaný výsledek |
|---|---|---|
| T-I18N-01 | První spuštění `cs-CZ`, `auto` | Zobrazí se čeština |
| T-I18N-02 | První spuštění `en-US` a nepodporované systémové locale, `auto` | Angličtina a bezchybný fallback |
| T-I18N-03 | Ruční změna `auto → cs → en → auto` | Dialogy a menu ve správném jazyce |
| T-I18N-04 | Výslovná volba jazyka, restart, přesun adresáře programu | Volba zachována |
| T-I18N-05 | Aktualizace programu z ZIP | Jazykové nastavení se neztratí |
| T-I18N-06 | Všechny funkční obrazovky v `cs/en` | Bez nepřeložených a uříznutých textů, bezpečnostní význam zachován |
| T-I18N-07 | Kolize, přesah materiálu, nepodporovaný projekt, chyba zápisu | Správné `cs/en` bezpečnostní hlášky |
| T-I18N-08 | `3,5` (`cs`) / `3.5` (`en`) | Identické interní mm a invariantní XML čísla |
| T-I18N-09 | Změna jazyka během práce s uspořádáním | Zachovány skupiny, pořadí i čísla |
| T-I18N-10 | Export identických parametrů při `cs/en` | Identický `.lbrn2` výsledek |
| T-I18N-11 | Unicode ve jménech a názvech výrobků | Uživatelský obsah se nepřekládá ani nepoškodí |
| T-I18N-12 | Chybějící `.qm` nebo položka během vývoje | Aplikace nespadne; bezpečný anglický fallback, release gate neprojde |
| T-I18N-13 | Plurály pro `0/1/2/5/21` | Správně zvolený tvar zprávy |
| T-I18N-14 | `lupdate`, `lrelease` a kontrola placeholderů | Katalogy lze bezchybně zpracovat |
| T-I18N-15 | Nová kritická hláška bez CS překladu | CI / release gate selže |
| T-I18N-16 | Interní ZIP na čistém Windows bez Pythonu či internetu | Kompletní `cs/en` |
| T-I18N-17 | Veřejný ZIP: `cs/en/de/sk/pl/fr/es/it` | Všechny jazyky jsou v nabídce, lze je offline přepnout; obsah v balíčku |
| T-I18N-18 | `auto` v systémech `de-AT`, `sk-SK`, `pl-PL`, `fr-CA`, `es-MX`, `it-IT` | Automaticky zvolen správný základní jazyk |
| T-I18N-19 | Jazyková matice pro každou bezpečnostní hlášku ve všech osmi jazycích | Bez chybějícího významu, řetězců a placeholderů; doložená jazyková kontrola |
| T-I18N-20 | Numerické ovládání v osmi locale, přepínání během práce | Identické interní mm, stejné geometrie a finální `.lbrn2` |
| T-I18N-21 | Dlouhé německé, polské, francouzské a italské texty v okně malého rozlišení | Ovládací prvky a důležité dialogy se neoříznou, varování zůstane čitelné |
| T-I18N-22 | Nová funkce ve v1.1/v2.0 a nový text v UI | Před veřejným releasem ověřeno všech osm jazyků; případná mezera blokuje release |

### 36.7 Návaznosti na fáze vývoje

1. **GIT-00:** založit soukromý GitHub repozitář, `translations/`, `docs/TRANSLATING.md` (zpočátku kostru) a připravit kontrolu katalogů; překlady nevkládat do jádra.
2. **Etapa 0/KAL-00 a etapa 1:** algoritmus a práce s `.lbrn2` používají výhradně jazykově invariantní data, bez importu Qt lokalizace.
3. **Etapa 3 / GUI:** nejprve implementovat `LocaleManager`, výběr jazyka a interní `cs/en`; průběžně zakládat katalogy dalších šesti jazyků, aby nevznikaly nepřeložitelné prvky.
4. **Brána interní MVP:** splnit T-I18N-01 až 16, běžná použitelná aplikace v CS/EN, bez povinnosti předčasně zveřejňovat nehotové překlady.
5. **Brána prvního veřejného v1.0.0 `L10N-PUBLIC-01`:** splnit T-I18N-17 až 22, jazykovou revizi všech osmi jazyků, úplnost kritických zpráv, kontrolu `.qm` artefaktů v sestaveném ZIPu a číselnou invariantnost ve všech locale. Je to doplněk, nikoliv náhrada `REL-01` a `PUB-01`.
6. **Každé další veřejné vydání:** regresní kontrola všech osmi jazyků a aktualizace katalogů; přidání dalšího jazyka vyžaduje schválení nové cílové lokalizace a odpovídajících testů.

**Definice dokončení:** Interní MVP: kompletní ovládání a bezpečnostní zprávy v češtině i angličtině, invariantní výsledky. **První veřejné vydání a každé následné veřejné vydání:** navíc úplná a revidovaná nabídka **Čeština · English · Deutsch · Slovenčina · Polski · Français · Español · Italiano**, offline ve Windows distribuci. Pokud libovolná z těchto podmínek chybí, označit lokalizaci za nedokončenou a veřejný release neprovádět.


## 37. Průběžná vývojová dokumentace — DOC-00 / DOC-01 (závazné)

### 37.1 Cíl a princip „dokumentace současně s kódem“

Dokumentace není samostatný závěrečný úkol. Musí vznikat **v průběhu každého kroku vývoje** a být součástí verzované historie repozitáře. Cílem je, aby bylo možné po přerušení práce obnovit stav projektu, pochopit důvody technických rozhodnutí a bezpečně navázat při opravách a nových verzích. Tento postup platí **už pro soukromý vývoj**, není podmíněn zveřejněním.

- **DOC-00**: při GIT-00 založit strukturu dokumentace a výchozí plány; nečekat až na funkční aplikaci.
- **DOC-01**: při každé významné změně implementace aktualizovat příslušný dokument, testy a stavovou evidenci **ve stejné pracovní změně** (ideálně ve stejném Pull Requestu nebo souvisejícím commitu).
- **Zásada pravdivosti**: rozlišovat **navrženo**, **rozpracováno**, **implementováno**, **otestováno** a **akceptováno**. Funkci nelze označit za hotovou pouze proto, že existuje kód nebo prototyp obrazovky.
- Soubory dokumentace jsou verzované v Gitu a dohledatelné podle `MVP-*`, `V11-*`, `V20-*`, `T-*`, `KAL-00`, `GIT-00`, `DOC-*`, `HELP-*`, `PLAN-*`.

### 37.2 Povinné dokumenty repozitáře

| Soubor | Obsah / účel | Kdy vytvořit | Kdy aktualizovat |
|---|---|---|---|
| `README.md` | Cíl projektu, skutečné schopnosti, známá omezení, rychlý start; výslovně neoficiální vztah k LightBurnu | DOC-00 | Změna veřejného chování, vydání |
| `docs/specification.md` | Aktuální schválená technická specifikace a odkazy na historie verzí | DOC-00 | Změna požadavku, rozsahu či akceptace |
| `docs/ARCHITECTURE.md` | Moduly, rozhraní, datové modely, závislosti, tok `.lbrn2` | První kód / KAL-00 | Změna návrhu, modulů nebo rozhraní |
| `docs/DECISIONS/ADR-XXXX.md` | Architecture Decision Record: problém, varianty, rozhodnutí, důsledky, datum | Při prvním zásadním rozhodnutí | Nové rozhodnutí; starší zápis nemazat, případně nahradit novým |
| `docs/DEVELOPMENT.md` | Vývojové prostředí, spuštění, testy, sestavení EXE a diagnostika | První kód | Změna postupu vývoje a buildu |
| `docs/FORMAT_COMPATIBILITY.md` | Verze `.lbrn2`, ověřené vlastnosti, odmítnuté konstrukce, regresní vzorky | KAL-00 | Každý objevený formát či kompatibilní/neslučitelný případ |
| `docs/TEST_PLAN.md` | Testovací strategie, případy, očekávané výsledky, odkaz na důkazy | DOC-00 | Změna chování a oprava chyby |
| `docs/ROADMAP.md` | Milníky, pořadí etap, závislosti a brány | DOC-00 | Při změně priorit a po každém milníku |
| `docs/STATUS.md` | Stručný průběžný stav: dokončeno, probíhá, překážky, další krok, datum | DOC-00 | Na konci každého smysluplného vývojového bloku a při uzavření milníku |
| `CHANGELOG.md` | Historie změn vydaných verzí (včetně interních označených sestavení) | První označené sestavení | Každé vydání; pro průběžné změny volitelná sekce Unreleased |
| `docs/RELEASE_CHECKLIST.md` | Brány REL-01, L10N-PUBLIC-01, DOC-REL-01, PUB-01 a evidence splnění | Před prvním release kandidátem | Každý release; uchovat historii schválení |
| `docs/manual/<locale>/...` | Uživatelský manuál / podklady pro offline nápovědu | Při prvním GUI | Se změnou každé uživatelské funkce; viz kap. 38 |
| `docs/TRANSLATING.md` | Pravidla překladů a terminologický slovníček | DOC-00 (kostra) | Každá změna lokalizace; viz kap. 36 |

**Jednotný zdroj pravdy:** GitHub Issues/Projects spravují *aktuální stav jednotlivých úkolů*; `docs/STATUS.md` je čitelný **datovaný souhrn**, nikoli paralelní nezávislá databáze. Specifikace určuje *co musí být splněno*, testy a záznamy určují *zda to bylo prokázáno*.

### 37.3 Aktualizační pravidlo (Definition of Done / DoD)

Funkce, oprava chyby či refaktor jsou **hotové** pouze pokud současně platí:

1. Kód odpovídá schválenému požadavku; změny mimo rozsah jsou vysvětleny.
2. Existuje odpovídající automatický test tam, kde je proveditelný; u `.lbrn2` a GUI také relevantní ruční integrační test a výsledek.
3. Byla aktualizována technická dokumentace, datový model či ADR, **pokud se jich změna týká**.
4. Je-li změna viditelná uživateli, byl **současně upraven manuál a nápověda** v povinných jazycích pro aktuální fázi; žádný postup nepopisuje neexistující tlačítko.
5. Stav GitHub Issue byl změněn na `Done` až s důkazem (commit/test/log/verze sestavení), případně byl po etapě aktualizován souhrn `docs/STATUS.md`.
6. Nová funkce určená do vydání je zaznamenána v `CHANGELOG.md` / návrhu poznámek k vydání.
7. Kontroly soukromí prošly: žádný zákaznický `.lbrn2`, citlivý obsah, přihlašovací údaj ani obrazovka zakázky se nedostaly do historie projektu, screenshotů či veřejných testovacích dat.

Výjimku (např. časově omezené experimentální větve) lze ponechat jako **rozpracováno** s odkazem na otevřený úkol. Nelze ji označit za dokončenou.

### 37.4 Vzor technického rozhodnutí (ADR)

```markdown
# ADR-0001: Způsob manipulace se soubory .lbrn2
Datum: YYYY-MM-DD
Stav: Navrženo | Přijato | Nahrazeno
Kontext: Jak bezpečně měnit polohy skupin?
Varianty: A) vlastní adaptér  B) API  C) manuální export/import
Rozhodnutí: ...
Důvody: ...
Rizika a omezení: ...
Odkazy: požadavky ..., testy ..., související commit/issue ...
```

**Podmínka uzavření DOC-00:** Struktura repozitáře vytvořena, do Gitu přidána aktuální specifikace, `README`, roadmapa, stav, plán testů a kostry vývojové dokumentace; úspěšný soukromý commit/push a kontrola obsahu. **DOC-01** se kontroluje při každém dalších relevantním úkolu.

## 38. Vestavěná uživatelská nápověda a manuál — MVP-08 / HELP-01

### 38.1 Cíl a uživatelský scénář

Uživatel může **bez připojení k internetu** kdykoliv v aplikaci zobrazit návod, aniž musí hledat externí PDF či GitHub. Přístup přes menu `Nápověda → Uživatelská příručka`, klávesu **F1** a podle potřeby kontextové tlačítko `?` u složitějších voleb. Nápověda bude odpovídat skutečné instalované verzi aplikace a rozhraní aktuálně zvoleného jazyka.

**MVP-08 (interní):** úplný a funkčně správný manuál v češtině a angličtině. **Veřejná v1.0.0:** uživatelská příručka a bezpečnostně důležité části dostupné ve všech osmi podporovaných jazycích `cs/en/de/sk/pl/fr/es/it`, jazykově revidované v souladu s kap. 36. Pro každý veřejný release musí manuál odpovídat dané verzi.

### 38.2 Minimální struktura manuálu

1. **Úvod a hranice použití** — program není oficiální součástí LightBurnu; podporované a nepodporované `.lbrn2`.
2. **Instalace, první spuštění a jazyk** — Windows ZIP, žádný Python, offline provoz.
3. **Příprava projektu v LightBurnu** — seskupení kartiček, uložení projektu a práce pouze s kopií.
4. **Načtení a výběr výrobků** — rozpoznání skupin, ruční přeuspořádání, odmítnuté skupiny.
5. **Nastavení mřížky** — počet sloupců, vodorovná/svislá mezera v mm, počátek, pořadí, režimy.
6. **Kontrola materiálu a kolizí** — rozměry materiálu, okraje, překážky, význam chyb a varování.
7. **Náhled, validace a export** — nový soubor; kontrola v LightBurnu přes `Open` a `Preview`, bezpečnostní omezení.
8. **Řešení problémů** — nepodporovaná geometrie, chyba zápisu, konflikt nastavení, postup při hlášení chyby.
9. **Verze, aktualizace a ochrana dat** — kde zjistit číslo verze, jak se ručně aktualizuje, jak bezpečně poskytnout diagnostiku.
10. **Nové funkce verze 1.1 / 2.0** — přidávat teprve až jsou implementované a ověřené (množství, automatická mřížka, více desek, více projektů).

Pro každou funkci uvést **účel, požadované vstupy, stručný postup, očekávaný výsledek, omezení, možné chyby a bezpečnostní upozornění**. Vzorové projekty musejí být syntetické, nikoli z reálných zakázek bez oprávnění.

### 38.3 Technický návrh nápovědy

- Zdrojové soubory jako **Markdown** v `src/grid_arranger/gui/help/<locale>/` (v1.10: přímo v balíčku aplikace, aby je sestavení EXE spolehlivě přibalilo; nahrazuje `docs/manual/<locale>/`), s indexem kapitol a stabilními identifikátory témat = názvy souborů (`index`, `prepare`, `items`, `grid`, `board`, `save`, `troubleshooting`, `about`).
- Modulu `gui/help/` předat pouze `topic_id` a `locale`; s výpočetním jádrem ani s XML adaptérem není propojen. Při sestavení Windows ZIP zabalit ověřenou verzi manuálu **lokálně** spolu s aplikací (např. Qt resources / datové soubory zabalené PySide6 deployem).
- Zobrazovač může být samostatné okno s `QTextBrowser`/Qt Markdown nebo jiný bezpečný lokální renderer. Nenavrhovat webový server ani vyžadovat Qt WebEngine; online nápověda může být pouze dobrovolný doplněk.
- Minimálně **obsah kapitol, Back/Forward, odkazování mezi tématy a hledání v rámci manuálu** (index nebo fulltext dle zvolené implementace). F1 otevře nápovědu na vhodné téma podle právě aktivní obrazovky; není-li kontext známý, otevře úvod.
- Odkazy na síť se otevírají pouze po akci uživatele v externím prohlížeči. Nápověda nesmí spouštět kód ze souborů ani načítat externí skripty či vložený vzdálený obsah.
- Datové soubory manuálu nejsou zdrojem proměnných aplikace. **Aktuální výrobní data ani projekty se do nápovědy neodesílají.**
- Přeložené manuály musí používat stejná `topic_id` a odpovídající členění; při nedostupné části lze interně bezpečně přepnout na angličtinu s viditelnou informací, ale **veřejné vydání** nesmí tvrdit úplný jazyk, pokud povinné části chybí.

### 38.4 Průběžná údržba manuálu

- Nový uživatelský ovládací prvek → ve stejné změně přidat návod, chybové stavy a překlad.
- Změněné chování → odstranit zastaralý postup **před začleněním** změny do stabilní větve.
- Opravená chyba se změnou pracovního postupu → upravit relevantní část manuálu a release notes.
- Screenshoty používat jen když reálně pomáhají; před zveřejněním musí být bez zákaznických dat a prověřené ve více lokalizacích.
- Na začátku manuálu zobrazit verzi aplikace/dokumentace a případně přehled podporovaných verzí LightBurnu. Nevytvářet zavádějící návody na neotestované funkce.
- Jazykový přepínač aplikace ovládá i jazyk nápovědy; při změně jazyka má zůstat zachováno aktuální téma, pokud existuje překlad.

### 38.5 Testovací kritéria nápovědy

| ID | Test | Očekávaný výsledek |
|---|---|---|
| T-HELP-01 | Stisk `F1` v hlavním okně | Otevře se offline příručka bez síťového spojení |
| T-HELP-02 | `Nápověda → Uživatelská příručka` a kontextové `?` | Otevře příslušné téma; nikdy nevznikne chybný odkaz |
| T-HELP-03 | Obsah, interní odkazy, zpět/vpřed a vyhledání textu | Funkční pro zabalený manuál na čistých Windows |
| T-HELP-04 | Přepnutí `cs ↔ en` během otevřené nápovědy | Jazyk manuálu se synchronizuje; aktivní téma zachováno |
| T-HELP-05 | Veřejný ZIP, osmi jazyků `cs/en/de/sk/pl/fr/es/it` | Úvod, všechny aktuální funkce, bezpečnostní části a postupy kompletní a revidované v každém jazyce |
| T-HELP-06 | Odpojený internet; spuštění aplikace z přenosné složky | Nápověda funguje kompletně offline a bez Pythonu |
| T-HELP-07 | Nové tlačítko / změna validace bez aktualizovaného návodu | Kontrola DoD/CI zablokuje označení úkolu za dokončený či release |
| T-HELP-08 | Manuál obsahuje zastaralý krok, skrytý klientský výkres či neověřenou možnost | Kontrola releasu selže; nezveřejnit |
| T-HELP-09 | Chybějící kapitola nebo neznámé `topic_id` | Bez pádu aplikace se zobrazí bezpečná úvodní stránka s upozorněním |
| T-HELP-10 | Aktuální verze aplikace proti verzi manuálu | Označená verze manuálu odpovídá sestavení a release notes |

**Brána HELP-01:** uživatelský manuál je skutečně **přibalený uvnitř EXE/ZIP distribuce** a lze jej otevřít F1 v reálné nainstalované/spuštěné aplikaci; nestačí jen `.md` v repozitáři.

## 39. Harmonogram, roadmapa a průběžný přehled dokončení — PLAN-00

### 39.1 Jak bude projekt řízen

Zvolit **milníkový (etapový) harmonogram**, nikoli závazné kalendářní termíny stanovené před ověřením technických rizik. Časy a data dokončení se doplní teprve podle skutečného tempa práce a výsledků KAL-00. Pro každou etapu evidovat: **ID, název, prioritu, závislosti, stav, kritéria dokončení a důkaz**.

V soukromém GitHub repozitáři založit při **GIT-00** jednoduchý GitHub **Projects** board se stavy `Backlog`, `Ready`, `In Progress`, `Review/Test`, `Blocked`, `Done`. Jednotlivé úkoly vést jako **GitHub Issues**; pro začátek je možné vytvořit jen důležité milníky a dílčí úkoly přidávat postupně. `docs/ROADMAP.md` drží logické pořadí a cíle, `docs/STATUS.md` aktuální ověřený stav projektu.

### 39.2 Výchozí harmonogram etap

| Etapa / ID | Výstup | Závislost | Stav při sepsání v1.6 |
|---|---|---|---|
| `GIT-00` | Soukromý GitHub, zabezpečení a GitHub Desktop | Žádná | Nezahájeno |
| `DOC-00` | Složky a základní soubory dokumentace, roadmapa, status, testovací plán | Souběžně s `GIT-00` | Připraven návrh, Git repozitář ještě nezaložen |
| `PLAN-00` | GitHub Projects board, milníky, Issue šablona, návaznost na ID a stavový report | `GIT-00` | Nezahájeno |
| `KAL-00` | Důkaz bezpečné změny polohy skupiny a validace `.lbrn2` | `GIT-00`, `DOC-00` | Nezahájeno |
| `CORE-00` | Samostatný deterministický algoritmus mřížky s testy | `DOC-00`; lze provádět souběžně s KAL-00 | Nezahájeno |
| `ADAPT-00` | Bezpečné čtení, identifikace skupin, zápis a diff | Úspěšné `KAL-00` | Nezahájeno |
| `GUI-00` | PySide6 EXE s výběrem, pořadím, náhledem a validací | `CORE-00`, použitelný adaptér | Nezahájeno |
| `HELP-01` | Offline F1 příručka a lokalizace CS/EN pro interní MVP | `GUI-00` (paralelně během vývoje GUI) | Nezahájeno |
| `MVP-ACCEPT` | Ověření všech MVP-* a fyzický test otevírání/Preview v LightBurnu | `CORE-00`, `ADAPT-00`, `GUI-00`, `HELP-01` | Nezahájeno |
| `PUBLIC-01` | První veřejný stabilní release v1.0.0 | `MVP-ACCEPT`, `REL-01`, `PUB-01`, `L10N-PUBLIC-01`, `DOC-REL-01` | Nezahájeno / není schváleno zveřejnění |
| `V11-ACCEPT` | Profily, různé počty kusů, automatická mřížka | `MVP-ACCEPT` | Plánováno |
| `V20-ACCEPT` | Více desek, více projektů | Ověřená verze 1.1 | Plánováno |
| `FUT-01` | Přímá integrace s LightBurnem | Externí možnosti API a samostatné rozhodnutí | Pouze výhled |

**Pozor:** Pořadí `PUBLIC-01` a interního zahájení prací na v1.1 lze změnit; zveřejnění je vždy samostatné rozhodnutí vlastníka. Procenta ani datum ukončení **nevyplňovat odhadem bez měřitelných podkladů**.

### 39.3 Záznam jednoho úkolu

```markdown
ID: MVP-03
Název: Ruční změna pořadí vybraných skupin
Stav: Backlog | Ready | In Progress | Review/Test | Blocked | Done
Závislosti: MVP-02, CORE-00
Akceptace: Přesné pořadí v náhledu i výstupním souboru; test T-MVP-...
Důkaz: odkaz na commit / test / issue / záznam integračního testu
Blokuje: ... (pouze při skutečné překážce)
Aktualizováno: YYYY-MM-DD
```

Nepoužívat status `Done` bez odkazu na ověření. U přerušené práce zachovat jasné „co bylo naposledy ověřeno / co zkusit dál“.

### 39.4 Pravidla aktualizace stavu a harmonogramu

- **Po každém smysluplném pracovním bloku:** zaznamenat hotové změny, probíhající úkol, překážky a nejbližší další krok v GitHub Issue; souhrn `docs/STATUS.md` udržovat aktuální minimálně při uzavření milníku a při důležité změně směru.
- **Při změně priorit a na konci etapy:** aktualizovat `docs/ROADMAP.md`, zejména závislosti, přesuny mezi MVP/1.1/2.0 a rozhodovací brány.
- **Před zahájením každé další etapy:** přečíst `STATUS.md` a poslední otevřený úkol; nepředpokládat, že rozpracovaná funkce funguje jen proto, že existuje soubor s kódem.
- **Před vydáním verze:** provést kontrolu splnění všech předcházejících etap, archivovat výsledky testů a propojit vydání na relevantní commity/issues.
- **Pokud se pracuje bez otevřeného GitHubu:** dočasně vést tytéž soubory lokálně a synchronizovat je při připojení; nic se samo „na pozadí“ neaktualizuje.

### 39.5 Zobrazení postupu

Pro rychlý přehled používat krátkou tabulku **Hotovo / Probíhá / Blokováno / Další**, vždy s datem. Procentuální údaj je **nepovinný**; používat jej jen při jasně definovaném počtu uzavřených akceptačních kritérií (např. 7/10 ověřených testů), nikoli jako dojem z objemu napsaného kódu. U každé verze uvádět seznam „Implementováno“ odděleně od „Otestováno“. To zabrání nepravdivému dojmu, že je funkce připravena pro výrobu.

### 39.6 Akceptační testy řízení vývoje

| ID | Test | Očekávaný výsledek |
|---|---|---|
| T-PLAN-01 | Při GIT-00 vytvořit board a Issues pro první etapy | Lze rozeznat naplánované, rozpracované a blokované kroky |
| T-PLAN-02 | Dokončení `KAL-00` | Issue Done má důkaz, roadmapa uvádí splněnou bránu a `STATUS.md` datum |
| T-PLAN-03 | Zablokovaný adaptér `.lbrn2` | Stav Blocked a popsaná příčina; následující nebezpečná etapa se nespustí |
| T-PLAN-04 | Změna rozsahu MVP | Upravena specifikace, roadmapa, odpovídající Issue a testy; dohledatelný commit |
| T-PLAN-05 | Přerušení projektu a pozdější návrat | Neznalý vývojář z dokumentace zjistí poslední ověřený stav a další bezpečný krok |
| T-PLAN-06 | Pokus označit funkci Done bez testu či manuálu | Kontrola DoD odmítne uzavření nebo zapíše explicitní blokaci |

## 40. Dokumentační testy, vydávací brána a návaznosti

### 40.1 Kontroly technické dokumentace

| ID | Kontrola | Podmínka splnění |
|---|---|---|
| T-DOC-01 | Struktura DOC-00 v privátním GitHub repozitáři | README, specifikace, ROADMAP, STATUS, TEST_PLAN, `.gitignore`; žádná citlivá data |
| T-DOC-02 | Změna datového modelu/adaptéru | `ARCHITECTURE.md` a případné ADR aktualizované ve stejné změně |
| T-DOC-03 | Nová uživatelská funkce | Testy + aktualizovaný manuál + poznámky k vydání / Unreleased |
| T-DOC-04 | Vrácení ke staršímu commitu | Lze dohledat odpovídající stav specifikace a dokumentace |
| T-DOC-05 | Projekt má blokující nevyřešenou chybu | `STATUS.md` ani README jej neprezentují jako plně funkční |
| T-DOC-06 | Veřejné vydání | Dokumentace odpovídá aktuálnímu EXE a uvádí omezení/kompatibilitu |
| T-DOC-07 | Překlad GUI/manualu na osm jazyků | Všechny aktuální manuálové kapitoly dostupné a významově ověřené pro veřejný release |

### 40.2 Release gate `DOC-REL-01`

**Před každým interním označeným vydáním:** aktuální `STATUS.md`, `CHANGELOG.md`, testovací protokol a `README.md` bez falešných tvrzení; návod odpovídá tomu, co je v sestavení. **Před veřejným vydáním:** navíc celý vestavěný manuál `cs/en/de/sk/pl/fr/es/it` splňuje `HELP-01`, žádný bezpečnostní text nechybí, aktuální kompatibilita je doložená a distribuční balíček skutečně obsahuje soubory nápovědy.

Dokumentační brána **nenahrazuje** `REL-01`, `PUB-01` ani `L10N-PUBLIC-01`; platí současně s nimi. Pokud dokumentace zaostává za kódem, release se **nevydává**. Nesmí se jen aktualizovat číslo verze manuálu bez ověření jeho skutečné správnosti.

### 40.3 Doporučené zavedení v první programátorské iteraci

1. Zahájit `GIT-00` a souběžně `DOC-00`: založit soukromé repo, vložit tuto specifikaci a pracovní šablony `ROADMAP.md`, `STATUS.md`, `TEST_PLAN.md` a `README.md`.
2. Zahájit `PLAN-00`: v GitHub Projects založit milníky a Issue minimálně pro `KAL-00`, `CORE-00`, `ADAPT-00`, `GUI-00`, `HELP-01`, `MVP-ACCEPT`; přiřadit závislosti a stav.
3. Spustit `KAL-00` na kopii reálného projektu; současně zapisovat skutečné nálezy do `FORMAT_COMPATIBILITY.md` a případné rozhodnutí do ADR.
4. Při prvním GUI vytvořit `docs/manual/cs` a `docs/manual/en`, připravit `F1` + nabídku nápovědy a text manuálu současně s jednotlivými obrazovkami.
5. Při dokončování interního MVP ověřit nové T-DOC, T-HELP, T-PLAN; **před veřejným v1.0.0** navíc dokončit překlady manuálu a GUI do všech osmi jazyků a projít všemi branami vydání.

**Konečné pravidlo:** Výstupem práce není jen zdrojový kód a EXE. Součástí každé relevantní změny je pravdivá dokumentace, aktualizovaná uživatelská nápověda a dohledatelný stav realizace. Žádný z těchto dokumentů se nesmí vydávat za důkaz technického dokončení, pokud neexistují ověřené testy a funkční sestavení.


---

## 41. Závazná politika projektového formátu — pouze `.lbrn2`

### 41.1 Rozhodnutí `FMT-00`

**Stav: SCHVÁLENO ve fázi návrhu (15. 10. 2026).** Vlastník projektu zvolil `.lbrn2` jako **jediný** cílový formát pro práci LightBurn Grid Arrangeru. Důvodem je zaměření na aktuální doporučený formát LightBurnu a vyhnutí se investici do legacy podpory. Toto rozhodnutí je závazné pro MVP, v1.1 i v2.0, pokud nebude změněno samostatným ADR.

- Podporované vstupy: pouze jednotlivé soubory `.lbrn2` v MVP; více souborů `.lbrn2` ve v2.0.
- Podporované výstupy: pouze **nové** soubory `.lbrn2`, nikdy přepis originálu.
- `.lbrn` není podporován: není cílem vytvořit parser, writer ani převodník `.lbrn`; nepoužívat jej ani jako automatickou alternativu při chybě `.lbrn2`.
- Import SVG/DXF/PDF nebo strojových souborů není součástí tohoto projektu; cílem je zachovat plnohodnotný projekt v LightBurnu.
- V GUI musí být filtr pro `.lbrn2`, ale samotná přípona **není důkazem** platného obsahu.
- Při pokusu otevřít `.lbrn` zobrazit srozumitelnou lokalizovanou zprávu: „Tato aplikace podporuje pouze projekty .lbrn2. Uložte projekt v LightBurnu ve formátu .lbrn2.“ Aplikace sama převod neprovádí.

**Podklad:** Oficiální správa souborů LightBurnu označuje `.lbrn2` za výchozí a doporučenou možnost; `.lbrn` označuje jako *Legacy Project*. Zdroj: https://docs.lightburnsoftware.com/latest/Reference/FileManagement/

### 41.2 Formát není veřejné stabilní API

Existuje veřejný popis XML struktury některých historických `.lbrn2` včetně `Shape`, `Group` a `XForm`, ale nejde o garanci kompatibility se všemi aktuálními nebo budoucími projekty. Zdroj: https://forum.lightburnsoftware.com/t/lbrn2-file-documentation/52174

**Zakázané předpoklady:** (1) každá verze má stejné schéma; (2) všechny vnořené transformace a externí zdroje se chovají stejně; (3) libovolnou neznámou strukturu je možné bez rizika přeserializovat; (4) úspěšné parsování znamená správné rozmístění nebo bezpečnou výrobu.

### 41.3 Brána `KAL-00` — výhradně `.lbrn2`

Vstupem bude nezávadný testovací `.lbrn2` vytvořený v aktuálním LightBurnu, se známou verzí aplikace a dokumentovaným obsahem. Nejprve pouze čtení, pak pokus o přesun jediné skupiny v **kopii** souboru.

**Test musí prokázat:**

1. Identifikaci struktury a relevantních polí aktuálního `.lbrn2`, včetně jednoznačných skupin a jejich transformací.
2. Správné zjištění hranic objektu po všech transformacích, případně bezpečné odmítnutí nevyhodnotitelného stavu.
3. Při čistém přesunu změnu pouze dovolené translace skupiny; ostatní uzly/hodnoty nezměněny podle schváleného strukturálního porovnání.
4. Platný, znovu čitelný výstup `.lbrn2`; originál je byte-identický podle SHA-256.
5. Otevření přes **File → Open** v LightBurnu (nikoli Import), zachování textů, vrstev, parametrů, skupin, geometrie a úspěšnou kontrolu Preview.
6. Negativní test neznámé nebo poškozené struktury: bezpečná chyba, žádný označený úspěšný výstup.
7. Záznam skutečně ověřené verze LightBurnu, Windows a typu testovacího projektu; všechny neověřené kombinace zůstávají nezaručené.

**Brána zůstává NEPROVEDENA**, dokud nejsou k dispozici reálné testy. Schválení formátu `.lbrn2` **neznamená** potvrzení technické proveditelnosti adaptéru.

### 41.4 Kompatibilita, změny verzí a selhání

- Vést `docs/FORMAT_COMPATIBILITY.md` s maticí *verze LightBurnu × typ konstrukce × stav importu / přesunu / round-trip / Preview*.
- Uživatel musí v aplikaci vidět, pro které verze a konstrukce byla kompatibilita skutečně ověřena.
- Pokud soubor obsahuje neznámé kritické konstrukce a aplikace nemůže prokázat bezpečné zachování dat, export je zablokován.
- Po vydání nové verze LightBurnu provést cílené regresní testy před deklarováním její podpory; případná chyba nesmí vést k tiché úpravě projektu.
- Neobcházet nepodporovaný `.lbrn2` tím, že jej aplikace skrytě převede na `.lbrn`.

### 41.5 Kritéria přijetí `FMT-00` / `FMT-01`

| ID testu | Scénář | Očekávaný výsledek |
|---|---|---|
| T-FMT-01 | Otevření platného testovaného `.lbrn2` | Načtení nebo jasně zdokumentované omezení |
| T-FMT-02 | Otevření `.lbrn` | Odmítnutí s přeloženou nápovědou, bez konverze |
| T-FMT-03 | Soubor přejmenovaný na `.lbrn2`, ale se špatným obsahem | Bezpečné odmítnutí |
| T-FMT-04 | Výstup z podporovaného projektu | Nový `.lbrn2`, originál beze změny |
| T-FMT-05 | Neznámá kritická struktura v projektu | Odmítnutí exportu a diagnostický záznam |
| T-FMT-06 | Ověření výsledku v LightBurnu přes Open a Preview | Správné skupiny, souřadnice a nastavení, bez vedlejších změn |
| T-FMT-07 | Opakovaná úprava se stejnými vstupy | Deterministický, významově shodný výsledek |

### 41.6 Návaznosti na GitHub a dokumentaci

- `docs/specification.md`: kapitola 41 je hlavním závazným zdrojem rozhodnutí.
- `docs/ARCHITECTURE.md`: explicitní `Lbrn2ProjectAdapter`, žádná větev `LegacyLbrnAdapter`.
- `docs/FORMAT_COMPATIBILITY.md`: živá matice, testovací důkazy a odmítnuté případy.
- `docs/ROADMAP.md`: cesta `GIT-00 → KAL-00 → ADAPT-00`; bez samostatného milníku pro `.lbrn`.
- `docs/manual`: seznam podporovaných formátů a srozumitelné chyby (pro veřejné vydání ve všech osmi jazycích).
- **Definice hotového adaptéru:** splněný KAL-00, zelené příslušné regresní testy, aktualizovaná matice a ručně ověřený výstup v LightBurnu.

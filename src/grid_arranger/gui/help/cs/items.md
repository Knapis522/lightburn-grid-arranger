# Výběr a pořadí výrobků

Po otevření projektu (ikona **Otevřít projekt** na nástrojové liště, **Soubor → Otevřít projekt** nebo Ctrl+O) se v seznamu zobrazí všechny skupiny nejvyšší úrovně:

- **Zaškrtnuté** výrobky se rozmístí do mřížky. Číslo před názvem je jejich pořadí v mřížce.
- **Nezaškrtnuté** výrobky se do výstupu nezapíší: v uloženém projektu nebudou a mřížka s nimi nepočítá. Pokud je chcete raději ponechat na místě, zvolte **Nastavení → Uložení → Nezaškrtnuté objekty → Ponechat na místě** — mřížka se jim pak vyhne.
- **Šedé** položky („nelze přesunout“) aplikace odmítla — důvod uvidíte po najetí myší. Nikdy se nepřesunou.
- ⚠ znamená upozornění (např. text, který nejde změřit) — výrobek lze použít, ale zkontrolujte ho v Preview.
- **Vynechání objektů:** vyberte položky v seznamu (i šedé) a stiskněte **Delete** (nebo **Úpravy → Vynechat z výstupu**, případně pravým tlačítkem). Přesunou se přeškrtnuté na konec seznamu a v uloženém projektu nebudou — hodí se, když z rozsáhlého projektu potřebujete jen část. **Úpravy → Obnovit vynechané objekty** vybrané vrátí. Vybrané kopie se jednoduše odeberou. Původní projekt se nikdy nemění.
- **Přejmenování:** F2, dvojklik nebo pravé tlačítko → *Přejmenovat výrobek…* dá výrobku vlastní název (např. „Klíčenka Petr“). Název je jen v aplikaci — v seznamu, protokolu a v názvech nových stránek — do projektu LightBurnu se nezapisuje. Aplikace si názvy pro daný soubor pamatuje.

Pořadí: **chyťte kartičku v náhledu myší a přetáhněte ji na místo jiné kartičky** — zelený rámeček ukazuje, kam dopadne; **obě kartičky si prohodí místa**, ostatní zůstanou, kde jsou, a seznam se přečísluje. Puštění mimo kartičky tažení zruší. Nebo vyberte položku v seznamu a použijte **Nahoru / Dolů**. Nově zaškrtnutý výrobek se zařadí na konec. **Výchozí pořadí** vrátí pořadí ze souboru. **Vybrat vše / Zrušit výběr** hromadně mění výběr.

**Natočení:** u natočeného výrobku je v seznamu šipka a úhel (↻ po směru, ↺ proti směru hodinových ručiček). Výrobek vyberete **kliknutím v náhledu** (oranžový rámeček) nebo v seznamu; **Ctrl+klik** přidá další, **Esc** výběr zruší. Pro vybrané výrobky:

- **↺ 90° / ↻ 90°** — otočí o 90° (např. aby měly všechny klíčenky očko nahoře);
- **Úhel vybraných** — zadejte libovolný úhel ve stupních (kladný = po směru hodinových ručiček);
- **Nenatáčet** — výrobek zůstane, jak je v projektu (směr textu, struktura materiálu);
- **Automaticky** — zruší ruční úhel, výrobek natočí aplikace.

Ručně zadaný úhel je v seznamu označen „(ručně)“, aplikace ho nemění a platí i při volbě Natočení *Nenatáčet*. Úhel se počítá od polohy v původním projektu. Po otevření jiného projektu se ruční úhly zruší. Viz [mřížka](grid.md).

**Kopie (vyplnění desky):** vyberte výrobky a stiskněte **Ctrl+C** a **Ctrl+V** — přidá se jedna kopie každého. Více kopií najednou: ikona **Vytvořit kopie** na nástrojové liště (nebo **Ctrl+D**, menu Úpravy) a zadejte počet, např. 5. Kopie se přidají na konec pořadí, jsou v seznamu označené „(kopie G5)“, převezmou ruční úhel a dají se natáčet a přesouvat jako ostatní výrobky. Kopii odeberete klávesou **Delete** nebo odškrtnutím. Do uloženého projektu se kopie zapíšou jako nové skupiny; originál projektu se nemění.

**Počet kusů** (pole vedle *Úhlu vybraných*): kolik kusů vybraného výrobku se má rozmístit — např. 5 = originál + 4 kopie, které se zařadí hned za něj (výrobky tak zůstanou v pořadí po variantách). Snížením se odeberou nejnovější kopie, **0** výrobek vůbec nerozmístí. Vyberete-li kopii, mění se počet kusů jejího originálu; v seznamu je u výrobku „×5“.

**Vyplnit desku kopiemi** (ikona desky s výrobky na nástrojové liště, **Ctrl+Shift+D**, menu Úpravy): přidá tolik kopií vybraných výrobků, kolik se ještě vejde na desku tak, aby rozložení prošlo kontrolou. Je-li vybráno více výrobků, kopie se střídají (A, B, A, B…). Nejlépe funguje s *Automatickým* počtem sloupců; s pevným počtem sloupců přibývají jen řádky.

Číslo **1** se umístí do rohu mřížky podle volby *Pořadí plnění* (viz [mřížka](grid.md)).

[← Příprava](prepare.md) · [Další: mřížka →](grid.md)

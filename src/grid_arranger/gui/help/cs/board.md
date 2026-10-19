# Deska, okraje a kontrola kolizí

**Deska** je obdélník materiálu v souřadnicích LightBurnu. Výchozí deska leží u počátku laseru (roh desky X 0, Y 0). Rozměr se předvyplní podle laseru uloženého v projektu; tlačítkem **Uložit jako výchozí pro tento laser** si nastavení zapamatujete. **Okraje** (výchozí 5 mm) jsou pás u hran desky, kam se nesmí nic umístit.

> Deska v aplikaci není pracovní plocha stroje. Skutečnou polohu materiálu a rámování ověřte na stroji.

Před uložením aplikace kontroluje:

- všechny přesouvané výrobky leží ve využitelné ploše desky,
- výrobky se nepřekrývají a dodržují mezeru,
- výrobky dodržují mezeru i od **nepřesouvaných** skupin a volných objektů, pokud ve výstupu zůstávají (Nastavení → Uložení); vynechané objekty se nepočítají,
- objekt, jehož rozměr nejde zjistit, uložení **zablokuje** (nelze potvrdit bezpečnost).

Chyby (✖) uložení blokují a uvádějí konkrétní výrobky. Upozornění (⚠) uložení nebrání. Aplikace nikdy sama nemění měřítko, neotáčí ani neposouvá nevybrané objekty.

Kontrola řeší obrysy v projektu, ne skutečný přesah při rastrování, kompenzaci šířky řezu ani pohyb hlavy — proto je **Preview v LightBurnu povinný**.

## Více desek

Když se kusy nevejdou na jednu desku, aplikace je rozdělí na více desek. Jak, zvolíte v sekci Deska v poli **Když se nevejde**:

- *Rozdělit na desky postupně* (výchozí) — deska 1 plná, pak deska 2 …; nejméně desek.
- *Rozdělit na desky rovnoměrně* — na každé desce stejný počet kusů (např. 50 → 17/17/16).
- *Rozdělit na desky podle výrobků* — na každé desce jen kusy jednoho výrobku (originál a jeho kopie).
- *Nerozdělovat (chyba)* — jako dřív: když se rozložení nevejde, je zablokované.

**Doplnit poslední desku kopiemi** přidá kopie, dokud není poslední deska plná (u *podle výrobků* se poslední deska každého výrobku doplní kopiemi téhož výrobku).

Nad náhledem jsou záložky desek jako stránky v LightBurnu; záložka s chybou je označená ✖ a hlášení uvádí desku. Uložit lze, jen když projdou všechny desky. Všechny desky mají stejné nastavení mřížky a stejnou desku; objekty ponechané na místě (Nastavení → Uložení) jsou jen na desce 1.

Při více deskách ukazuje seznam Výrobky kusy zobrazené desky (číslované na ní) a pod nimi nezaškrtnuté a vynechané objekty; automaticky doplněné kopie jsou šedé. **Ctrl+A** označí všechny výrobky — při více deskách jen na zobrazené desce.

**Uložení:** deska 1 zůstane na rozkládané stránce a desky 2 … se přidají jako nové stránky hned za ni („Stránka 1 – deska 2“ …). V LightBurnu přepínejte stránky (**Window → Pages**) a pálte jednu desku po druhé — Preview i Frame pracují jen s aktivní stránkou. Případně **Nastavení → Desky → Jako samostatné soubory** uloží co deska, to soubor (`…__deska1.lbrn2` …). Výchozí hodnoty (způsob rozdělení, doplnění, upozornění nad počet desek) jsou v **Nastavení → Desky**.

[← Mřížka](grid.md) · [Další: uložení →](save.md)

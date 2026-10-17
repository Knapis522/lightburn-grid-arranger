# Řešení problémů

**„Podporovány jsou pouze projekty .lbrn2“** — uložte projekt v LightBurnu jako `.lbrn2`.

**„Nepodporovaná verze LightBurnu“** — projekt uložil LightBurn, se kterým aplikace zatím nebyla ověřena. Výstup by nemusel být bezpečný, proto je odmítnut.

**„Tento počátek laseru zatím nebyl ověřen“** — podporovány jsou lasery s počátkem nahoře (vlevo nebo vpravo).

**Výrobek „nelze přesunout“** — najeďte na něj myší. Nejčastěji: skupina nemá uzavřený řezný obrys, něco z ní vyčnívá ven z obrysu, je zamčená, nebo obsahuje typ objektu, který aplikace zatím neumí bezpečně přesunout (např. bitmapu).

**„Mnohoúhelník s N stranami / obdélník se zaoblenými rohy zatím nebyl ověřen“** — tyto tvary nakreslené přímo v LightBurnu aplikace zatím bezpečně nezná. V LightBurnu tvar vyberte, převeďte na křivky (*Convert to Path*) a projekt znovu uložte. Kruh, elipsa, obdélník bez zaoblení a šestiúhelník fungují přímo.

**„Geometrie textu neodpovídá jeho poloze“** — otevřete projekt v LightBurnu a znovu ho uložte.

**Uložení je zablokované** — přečtěte chyby (✖) pod náhledem: přesah desky, kolize, malá mezera nebo nezměřitelný objekt. Upravte sloupce, mezery, desku nebo výběr.

**„Původní soubor se změnil“** — projekt byl mezitím znovu uložen. Otevřete ho v aplikaci znovu.

**Windows hlásí „Systém Windows ochránil váš počítač“** — aplikace zatím není digitálně podepsaná. Pokud ZIP pochází od správce aplikace, klikněte na **Další informace → Přesto spustit**. Antivirus nevypínejte.

**Aplikace se nespustí nebo hlásí chybějící soubor** — nejspíš chybí složka `_internal` vedle `GridArranger.exe` (např. byl zkopírován jen samotný EXE). Rozbalte ZIP znovu celý. Kontrolu instalace provede příkaz `GridArranger.exe --self-test report.json` v příkazovém řádku; výsledek je v `report.json`.

**Hlášení chyby** — zapněte Nastavení → Protokol uložení, uložte znovu a pošlete protokol `.json` (obsahuje kontrolní součty a parametry, ne obsah výrobků) a popis kroků. Zákaznické projekty posílejte jen s oprávněním.

[← Úvod](index.md)

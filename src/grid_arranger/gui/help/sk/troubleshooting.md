# Riešenie problémov

**„Aplikácia podporuje iba projekty .lbrn2“** — uložte projekt v LightBurne ako `.lbrn2`.

**„Nepodporovaná verzia LightBurnu“** — projekt bol uložený verziou LightBurnu, s ktorou aplikácia nebola overená. Výstup by nemusel byť bezpečný, preto je odmietnutý.

**Výrobok „nedá sa presunúť“** — podržte nad ním myš. Najčastejšie: skupina nemá uzavretý rezný obrys, niečo presahuje obrys, je uzamknutá alebo obsahuje typ objektu, ktorý aplikácia zatiaľ nevie bezpečne presunúť (napr. bitmapu).

**„Geometria textu nezodpovedá jeho polohe“** — otvorte projekt v LightBurne a znova ho uložte.

**Uloženie je zablokované** — prečítajte chyby (✖) pod náhľadom: presah dosky, kolízia, príliš malá medzera alebo objekt, ktorý nemožno zmerať. Zmeňte stĺpce, medzery, dosku alebo výber.

**„Pôvodný súbor sa od otvorenia zmenil“** — projekt bol medzitým znova uložený. Otvorte ho v aplikácii znova.

**Windows hlási „Windows ochránil váš počítač“** — aplikácia zatiaľ nie je digitálne podpísaná. Ak inštalátor pochádza z vydaní tohto projektu na GitHube, kliknite na **Ďalšie informácie → Spustiť aj tak**. Antivírus nevypínajte.

**Aplikácia sa nespustí alebo hlási chýbajúci súbor** — najpravdepodobnejšie chýba priečinok `_internal` vedľa `GridArranger.exe` (napr. sa skopírovalo len EXE). Rozbaľte celý ZIP znova. Na kontrolu inštalácie spustite v príkazovom riadku `GridArranger.exe --self-test report.json`; výsledok sa zapíše do `report.json`.

**Nahlásenie problému** — zapnite Nastavenia → Ukladanie → Protokol uloženia, uložte znova a pošlite protokol `.json` (obsahuje kontrolné súčty a parametre, nie obsah výrobkov) a popis krokov. Zákaznícke projekty posielajte len s povolením.

[← Úvod](index.md)

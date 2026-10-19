# Doska, okraje a kontrola kolízií

**Doska** je obdĺžnik materiálu v súradniciach LightBurnu. Predvolene leží pri počiatku lasera (roh dosky X 0, Y 0). Jej rozmer sa predvyplní podľa lasera uloženého v projekte; **Uložiť ako predvolené pre tento laser** si vaše hodnoty zapamätá. **Okraje** (predvolene 5 mm) sú pás pozdĺž hrán dosky, kam sa nič neumiestni.

> Doska v aplikácii nie je pracovná plocha stroja. Skutočnú polohu materiálu a rámovanie overte na stroji.

Pred uložením aplikácia skontroluje, že:

- všetky presúvané výrobky ležia vnútri využiteľnej plochy dosky,
- výrobky sa neprekrývajú a dodržiavajú medzeru,
- výrobky dodržiavajú medzeru aj od **nepresúvaných** skupín a voľných objektov, ak vo výstupe zostávajú (Nastavenia → Ukladanie); vynechané objekty sa nepočítajú,
- objekt, ktorého rozmer nemožno určiť, uloženie **zablokuje** (bezpečnosť nemožno potvrdiť).

Chyby (✖) uloženie blokujú a uvádzajú dotknuté výrobky. Upozornenia (⚠) nie. Aplikácia nikdy sama nemení mierku, neotáča ani nepresúva nevybrané objekty.

Kontrola pracuje s obrysmi v projekte, nie so skutočným prejazdom pri gravírovaní, kompenzáciou šírky rezu ani pohybom hlavy — preto je **Preview v LightBurne povinné**.

## Viac dosiek

Keď sa kusy nevojdú na jednu dosku, aplikácia ich rozdelí na viac dosiek. Ako, zvolíte v sekcii Doska v poli **Keď sa nevojde**:

- *Rozdeliť na dosky postupne* (predvolené) — doska 1 plná, potom doska 2 …; najmenej dosiek.
- *Rozdeliť na dosky rovnomerne* — na každej doske rovnaký počet kusov (napr. 50 → 17/17/16).
- *Rozdeliť na dosky podľa výrobkov* — na každej doske len kusy jedného výrobku (originál a jeho kópie).
- *Nerozdeľovať (chyba)* — ako doteraz: keď sa rozloženie nevojde, je zablokované.

**Doplniť poslednú dosku kópiami** pridá kópie, kým nie je posledná doska plná (pri *podľa výrobkov* sa posledná doska každého výrobku doplní kópiami toho istého výrobku).

Nad náhľadom sú záložky dosiek ako strany v LightBurne; záložka s chybou je označená ✖ a hlásenie uvádza dosku. Uložiť možno, len keď prejdú všetky dosky. Všetky dosky majú rovnaké nastavenie mriežky a rovnakú dosku; objekty ponechané na mieste (Nastavenia → Ukladanie) sú len na doske 1.

Pri viacerých doskách zobrazuje zoznam Výrobky kusy zobrazenej dosky (číslované na nej) a pod nimi nezaškrtnuté a vynechané objekty; automaticky doplnené kópie sú sivé. **Ctrl+A** označí všetky výrobky — pri viacerých doskách len na zobrazenej doske.

**Uloženie:** doska 1 zostane na rozkladanej strane a dosky 2 … sa pridajú ako nové strany hneď za ňu („Strana 1 – doska 2“ …). V LightBurne prepínajte strany (**Window → Pages**) a páľte jednu dosku po druhej — Preview aj Frame pracujú len s aktívnou stranou. Prípadne **Nastavenia → Dosky → Ako samostatné súbory** uloží čo doska, to súbor (`…__doska1.lbrn2` …). Predvolené hodnoty (spôsob rozdelenia, doplnenie, upozornenie nad počet dosiek) sú v **Nastavenia → Dosky**.

[← Mriežka](grid.md) · [Ďalej: uloženie →](save.md)

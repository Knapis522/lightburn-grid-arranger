# Doska, okraje a kontrola kolízií

**Doska** je obdĺžnik materiálu v súradniciach LightBurnu. Predvolene leží pri počiatku lasera (roh dosky X 0, Y 0). Jej rozmer sa predvyplní podľa lasera uloženého v projekte; **Uložiť ako predvolené pre tento laser** si vaše hodnoty zapamätá. **Okraje** (predvolene 5 mm) sú pás pozdĺž hrán dosky, kam sa nič neumiestni.

> Doska v aplikácii nie je pracovná plocha stroja. Skutočnú polohu materiálu a rámovanie overte na stroji.

Pred uložením aplikácia skontroluje, že:

- všetky presúvané výrobky ležia vnútri využiteľnej plochy dosky,
- výrobky sa neprekrývajú a dodržiavajú medzeru,
- výrobky dodržiavajú medzeru aj od **nepresúvaných** skupín a voľných objektov,
- objekt, ktorého rozmer nemožno určiť, uloženie **zablokuje** (bezpečnosť nemožno potvrdiť).

Chyby (✖) uloženie blokujú a uvádzajú dotknuté výrobky. Upozornenia (⚠) nie. Aplikácia nikdy sama nemení mierku, neotáča ani nepresúva nevybrané objekty.

Kontrola pracuje s obrysmi v projekte, nie so skutočným prejazdom pri gravírovaní, kompenzáciou šírky rezu ani pohybom hlavy — preto je **Preview v LightBurne povinné**.

[← Mriežka](grid.md) · [Ďalej: uloženie →](save.md)

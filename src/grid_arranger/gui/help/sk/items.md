# Výber a poradie výrobkov

Po otvorení projektu (ikona **Otvoriť projekt** na paneli nástrojov, **Súbor → Otvoriť projekt** alebo Ctrl+O) zoznam ukazuje všetky skupiny najvyššej úrovne:

- **Zaškrtnuté** výrobky sa rozmiestnia do mriežky. Číslo pred názvom je ich poradie v mriežke.
- **Nezaškrtnuté** výrobky sa do výstupu nezapíšu: v uloženom projekte nebudú a mriežka s nimi nepočíta. Ak ich chcete radšej ponechať na mieste, zvoľte **Nastavenia → Ukladanie → Nezaškrtnuté objekty → Ponechať na mieste** — mriežka sa im potom vyhne.
- **Sivé** výrobky („nedá sa presunúť“) boli odmietnuté — po podržaní myši sa zobrazí dôvod. Nikdy sa nepresúvajú.
- ⚠ označuje upozornenie (napr. text, ktorý nemožno zmerať) — výrobok možno použiť, ale skontrolujte ho v Preview.
- **Vynechanie objektov:** vyberte položky v zozname (aj sivé) a stlačte **Delete** (alebo **Úpravy → Vynechať z výstupu**, prípadne pravým tlačidlom). Presunú sa prečiarknuté na koniec zoznamu a v uloženom projekte nebudú — hodí sa, keď z rozsiahleho projektu potrebujete len časť. **Úpravy → Obnoviť vynechané objekty** vybrané vráti. Vybrané kópie sa jednoducho odoberú. Pôvodný projekt sa nikdy nemení.
- **Premenovanie:** F2, dvojklik alebo pravé tlačidlo → *Premenovať výrobok…* dá výrobku vlastný názov (napr. „Kľúčenka Peter“). Názov je len v aplikácii — v zozname, protokole a v názvoch nových strán — do projektu LightBurnu sa nezapisuje. Aplikácia si názvy pre daný súbor pamätá.

Poradie: **výrobok v náhľade chyťte myšou a pretiahnite na miesto iného výrobku** — zelený rámik ukazuje, kam dopadne; **oba výrobky si vymenia miesta**, ostatné zostanú a zoznam sa prečísluje. Pustenie mimo výrobkov ťahanie zruší. Alebo výrobok vyberte v zozname a použite **Hore / Dole**. Novo zaškrtnutý výrobok sa pridá na koniec. **Predvolené poradie** obnoví poradie zo súboru. **Vybrať všetko / Zrušiť výber** zmenia výber naraz.

**Otočenie:** otočený výrobok má v zozname šípku a uhol (↻ v smere hodinových ručičiek, ↺ proti). Výrobok vyberte **kliknutím v náhľade** (oranžový rámik) alebo v zozname; **Ctrl+klik** pridá ďalšie, **Esc** výber zruší. Pre vybrané výrobky:

- **↺ 90° / ↻ 90°** — otočí o 90° (napr. aby mali všetky kľúčenky očko hore);
- **Uhol vybraných** — zadajte ľubovoľný uhol v stupňoch (kladný = v smere hodinových ručičiek);
- **Neotáčať** — výrobok zostane tak, ako je v projekte (smer textu, vlákna materiálu);
- **Automaticky** — zruší ručný uhol; aplikácia výrobok znova otáča sama.

Ručný uhol je v zozname označený „(ručne)“; aplikácia ho nikdy nemení a platí aj pri Otočení *Neotáčať*. Uhol sa meria od polohy v pôvodnom projekte. Otvorením iného projektu sa ručné uhly zrušia. Pozri [mriežku](grid.md).

**Kópie (vyplnenie dosky):** vyberte výrobky a stlačte **Ctrl+C** a **Ctrl+V** — pridá sa jedna kópia každého. Viac kópií naraz: ikona **Vytvoriť kópie** na paneli nástrojov (alebo **Ctrl+D**, ponuka Úpravy) a zadajte počet, napr. 5. Kópie sa pridajú na koniec poradia, sú v zozname označené „(kópia G5)“, prevezmú ručný uhol a dajú sa otáčať a presúvať ako ostatné výrobky. Kópiu odoberiete klávesom **Delete** alebo odškrtnutím. Do uloženého projektu sa kópie zapíšu ako nové skupiny; pôvodný projekt sa nemení.

**Počet kusov** (pole vedľa *Uhla vybraných*): koľko kusov vybraného výrobku sa má rozmiestniť — napr. 5 = originál + 4 kópie hneď za ním (výrobky tak zostanú zoradené podľa variantov). Znížením sa odoberú najnovšie kópie, **0** výrobok vôbec nerozmiestni. Ak vyberiete kópiu, mení sa počet kusov jej originálu; v zozname je pri výrobku „×5“.

**Vyplniť dosku kópiami** (ikona dosky s výrobkami na paneli nástrojov, **Ctrl+Shift+D**, ponuka Úpravy): pridá toľko kópií vybraných výrobkov, koľko sa ešte zmestí na dosku tak, aby rozloženie prešlo kontrolou. Ak je vybraných viac výrobkov, kópie sa striedajú (A, B, A, B…). Najlepšie funguje s *automatickým* počtom stĺpcov; s pevným počtom stĺpcov pribúdajú len riadky.

Výrobok číslo **1** je v rohu mriežky podľa *Poradia plnenia* (pozri [mriežku](grid.md)).

[← Príprava](prepare.md) · [Ďalej: mriežka →](grid.md)

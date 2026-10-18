# Mriežka a umiestnenie

**Profil rozloženia** — nastavenie uložené pod názvom (napr. „Kľúčenky 3 mm“): počet stĺpcov (alebo *Automaticky*), medzery, poradie plnenia, otočenie a umiestnenie. Výberom profilu v sekcii **Profil rozloženia** sa hodnoty nastavia; **Uložiť…** uloží aktuálne nastavenie ako profil (rovnaký názov = prepísať), **Vymazať** ho odstráni. Keď hodnoty zmeníte, výber sa prepne na *bez profilu* — profil sám zostane bez zmeny. Doska v profile nie je, patrí k laseru (Nastavenia → Lasery).

**Počet stĺpcov** — koľko výrobkov bude v jednom riadku. Počet riadkov sa dopočíta. So zaškrtnutým **Automaticky** použije aplikácia toľko stĺpcov, koľko sa zmestí na šírku dosky (využiteľnú plochu po odpočítaní okrajov); pole potom ukazuje vypočítaný počet. Hodí sa s kópiami a s *Vyplniť dosku kópiami*.

**Medzera X / Y** — vzdialenosť medzi reznými obrysmi susedných výrobkov (vodorovne / zvisle) vo zvolených jednotkách. Medzera 0 je dovolená, ale aplikácia upozorní na riziko pri rezaní. Desatinné čísla zadávajte, ako je zvykom v jazyku aplikácie (po slovensky s čiarkou).

Ak majú výrobky **rôzne rozmery**, šírka stĺpca je podľa najširšieho výrobku v stĺpci a výška riadku podľa najvyššieho v riadku. Zadaná medzera je potom **minimálna** — medzi menšími výrobkami bude väčšia.

**Poradie plnenia**

- *Od počiatku lasera* (predvolené) — výrobok č. 1 je v rohu pri počiatku lasera; pri počiatku vpravo sa riadky plnia sprava doľava, pri počiatku dole je prvý riadok dole a ďalšie sú nad ním.
- *Poradie čítania* — výrobok č. 1 je vždy vľavo hore, riadky zľava doprava.

**Umiestnenie mriežky**

- *Do rohu dosky pri počiatku lasera* (predvolené) — roh mriežky pri počiatku leží v rohu dosky + okraj.
- *Do stredu dosky*.
- *Ručne* — zadajte súradnice X/Y LightBurnu (vzdialenosť od počiatku) rohu mriežky pri počiatku.
- *Na pôvodné miesto výrobkov*.

Polia **Roh X / Y** sa dajú upraviť len v režime *Ručne*. V ostatných režimoch sú sivé a ukazujú roh, ktorý aplikácia práve vypočítala (mení sa napríklad s okrajmi). Po prepnutí na *Ručne* v nich zostane aktuálny roh, takže sa mriežka neposunie a môžete ju len doladiť.

Náhľad ukazuje dosku, využiteľnú plochu (čiarkovane), počiatok lasera (●), presúvané výrobky so skutočnými motívmi a textami vo farbách vrstiev a s poradím a nepresúvané objekty sivo. Výrobky s chybou sú červené. Prepínač **Zobraziť motívy** v hlavičke sekcie Výrobky vypne kresbu a nechá len obdĺžniky výrobkov. Koliesko myši (aj touchpad) plynulo približuje, ťahaním prázdneho miesta posúvate pohľad (ťahaním výrobku meníte poradie), ikona **Prispôsobiť náhľad** na paneli nástrojov (Ctrl+0) alebo dvojklik do prázdneho miesta zobrazí všetko.

## Otočenie kvôli úspore materiálu

Voľba **Otočenie** v sekcii Mriežka:

- *Ľubovoľný uhol (najmenšia plocha)* — predvolené. Každý výrobok sa otočí tak, aby obdĺžnik okolo neho bol čo najmenší (pri šikmých alebo nepravidelných tvaroch, napr. kľúčenkách, to ušetrí miesto). Obdĺžnikové kartičky zostanú rovno.
- *Po 90°* — výrobky sa len otáčajú o štvrť otáčky (na šírku / na výšku).
- *Neotáčať* — výrobky sa len posúvajú.

Vo všetkých režimoch aplikácia navyše vyskúša, či by mriežka nebola menšia, keby všetky výrobky ležali na šírku alebo na výšku, a zvolí menšiu variantu — prednostne tú, ktorá sa zmestí na dosku. Ak by otočenie mriežku nezmenšilo, výrobky zostanú, ako sú; okrúhle výrobky sa o 90° neotáčajú. Otočenie je vidieť v náhľade aj v zozname výrobkov. Výrobok sa otáča okolo svojho stredu aj s textami a motívmi; po uložení skontrolujte v LightBurne Preview. Výnimky pre jednotlivé výrobky: tlačidlo **Neotáčať** v sekcii Výrobky.

[← Výber](items.md) · [Ďalej: doska a kontrola →](board.md)

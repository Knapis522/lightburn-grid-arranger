# Mřížka a umístění

**Počet sloupců** — kolik výrobků bude v jednom řádku. Počet řádků se dopočítá.

**Mezera X / Y** — vzdálenost mezi řeznými obrysy sousedních výrobků (vodorovně / svisle) ve zvolených jednotkách. Mezera 0 je dovolená, ale aplikace upozorní na riziko při řezání. Desetinná čísla zadávejte s čárkou (česky) nebo tečkou (anglicky) podle jazyka aplikace.

Mají-li výrobky **různé rozměry**, šířka sloupce je podle nejširšího výrobku ve sloupci a výška řádku podle nejvyššího v řádku. Zadaná mezera je pak **minimální** — mezi menšími výrobky bude větší.

**Pořadí plnění**

- *Od počátku laseru* (výchozí) — výrobek č. 1 je v rohu u počátku laseru; u laseru s počátkem vpravo nahoře se řádky plní zprava doleva.
- *Čtení* — výrobek č. 1 je vždy vlevo nahoře, řádky zleva doprava.

**Umístění mřížky**

- *Do rohu desky u počátku laseru* (výchozí) — roh mřížky u počátku leží v rohu desky + okraj.
- *Na střed desky*.
- *Ručně* — zadejte souřadnice X/Y LightBurnu (vzdálenost od počátku) rohu mřížky u počátku.

Pole **Roh X / Y** jdou upravit jen v režimu *Ručně*. V ostatních režimech jsou zašedlá a ukazují roh, který aplikace právě vypočítala (mění se třeba s okraji). Po přepnutí na *Ručně* v nich zůstane aktuální roh, takže se mřížka neposune a můžete ji jen doladit.
- *Podle původní polohy výrobků*.

Náhled vpravo ukazuje desku, využitelnou plochu (čárkovaně), počátek laseru (●), přesouvané výrobky se skutečnými motivy a texty v barvách vrstev a s pořadím a nepřesouvané objekty šedě. Výrobky s chybou jsou červené. Přepínač **Zobrazit motivy** v hlavičce sekce Výrobky vypne kresbu a nechá jen obdélníky výrobků. Kolečko myši (i touchpad) plynule přibližuje, tažením prázdného místa posouváte pohled (tažením kartičky měníte pořadí), ikona **Přizpůsobit** na nástrojové liště (Ctrl+0) nebo dvojklik do prázdného místa zobrazí vše.

## Natočení pro úsporu materiálu

Volba **Natočení** v sekci Mřížka:

- *Libovolný úhel (nejmenší plocha)* — výchozí. Každý výrobek se natočí tak, aby obdélník kolem něj byl co nejmenší (u šikmých nebo nepravidelných tvarů, např. klíčenek, to ušetří místo). Obdélníkové kartičky zůstanou rovně.
- *Po 90°* — výrobky se jen otáčí o čtvrt otáčky (na šířku / na výšku).
- *Nenatáčet* — výrobky se jen posouvají.

Ve všech režimech aplikace navíc vyzkouší, zda by mřížka nebyla menší, kdyby všechny výrobky ležely na šířku nebo na výšku, a zvolí menší variantu — přednostně tu, která se vejde na desku. Natočení je vidět v náhledu i v seznamu výrobků. Výrobek se natáčí kolem svého středu i s texty a motivy; po uložení zkontrolujte v LightBurnu Preview. Výjimky pro jednotlivé výrobky: tlačítko **Nenatáčet** v sekci Výrobky.

[← Výběr](items.md) · [Další: deska a kontrola →](board.md)

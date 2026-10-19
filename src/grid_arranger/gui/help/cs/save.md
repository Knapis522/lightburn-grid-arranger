# Uložení a kontrola v LightBurnu

Ikona **Uložit jako nový projekt** na nástrojové liště (nebo **Soubor → Uložit jako nový projekt**, Ctrl+S) je aktivní, jen když rozložení prošlo kontrolou. Otevře se okno pro uložení: navržený je název `původní__grid_001.lbrn2` (další `_002`, …) ve složce originálu — **složku i název můžete změnit**. Po potvrzení aplikace:

1. připraví nový soubor, ve kterém se změní jen polohy vybraných skupin (a jejich textů), vynechané objekty se odeberou,
2. nezávisle ověří, že se nic jiného nezměnilo (vrstvy, výkony, texty, ostatní objekty),
3. ověří, že se originál od otevření nezměnil,
4. uloží **nový** soubor pod zvoleným názvem.

**Protokol uložení** (`.json`) — záznam o tom, z čeho a jak výstup vznikl: kontrolní součty, laser, nastavení mřížky, posuny výrobků a výsledek kontroly (žádné motivy ani texty výrobků). Hodí se pro dohledání nebo hlášení chyby. **Nastavení → Uložení → Protokol uložení**: *Neukládat* (výchozí), *Vedle uloženého projektu* (`<název>.json`), nebo *Do složky protokolů aplikace* (otevřete ji tamtéž položkou **Otevřít složku protokolů**).

**Po uložení pracujete dál s originálem.** Uložený soubor je samostatná nová kopie; v aplikaci zůstává otevřený původní projekt, takže můžete zkusit jiné rozložení a uložit další variantu (`_002`, …). Titulek okna i sekce Projekt ukazují *naposledy uloženo jako …*. Chcete-li místo toho pokračovat s uloženým souborem (jako „Uložit jako“), zaškrtněte v hlášení o uložení **Pokračovat v aplikaci s uloženým souborem** — otevře se místo originálu, kopie a natočení v něm už jsou napevno a krok zpět začíná znovu. Další uložení pak pokračuje v číselné řadě originálu (`_002`, ne `__grid_001__grid_001`).

Existující soubory ani originál se nikdy nepřepisují — pokud zvolený soubor (nebo jeho protokol vedle něj) už existuje, aplikace požádá o jiný název. Při jakékoli chybě nevznikne žádný výstup.

**Potom v LightBurnu:**

1. Otevřete výstup: v hlášení o uložení tlačítkem **Otevřít v LightBurnu** (nebo ikonou na nástrojové liště, **Soubor → Otevřít uložený projekt v LightBurnu**, Ctrl+L). Aplikace soubor otevře stejně jako dvojklik v Průzkumníku: běžící LightBurn nahradí otevřený projekt — má-li neuložené změny, sám se zeptá na uložení; jinak se LightBurn spustí. Ručně otevírejte přes **File → Open** (ne Import — Import nenačte nastavení projektu).
2. Zkontrolujte vrstvy, výkony a rychlosti.
3. Spusťte **Preview** a prohlédněte dráhy.
4. Ověřte polohu na stroji (**Frame**). Teprve potom řežte, pod dohledem.

**Neuložené změny:** pokud jste rozložení od otevření nebo od posledního uložení změnili, je za názvem projektu v titulku okna hvězdička (`karty.lbrn2*`). Při zavření aplikace, otevření jiného projektu nebo instalaci aktualizace se aplikace zeptá, zda rozložení uložit jako nový projekt, zahodit, nebo akci zrušit. Pokud rozložení neprošlo kontrolou, nabídne jen zahodit nebo zrušit.

[← Deska](board.md) · [Řešení problémů →](troubleshooting.md)

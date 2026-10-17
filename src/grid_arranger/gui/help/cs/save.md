# Uložení a kontrola v LightBurnu

Ikona **Uložit jako nový projekt** na nástrojové liště (nebo **Soubor → Uložit jako nový projekt**, Ctrl+S) je aktivní, jen když rozložení prošlo kontrolou. Otevře se okno pro uložení: navržený je název `původní__grid_001.lbrn2` (další `_002`, …) ve složce originálu — **složku i název můžete změnit**. Po potvrzení aplikace:

1. připraví nový soubor, ve kterém se změní jen polohy vybraných skupin (a jejich textů),
2. nezávisle ověří, že se nic jiného nezměnilo (vrstvy, výkony, texty, ostatní objekty),
3. ověří, že se originál od otevření nezměnil,
4. uloží **nový** soubor pod zvoleným názvem.

**Protokol uložení** (`.json`) — záznam o tom, z čeho a jak výstup vznikl: kontrolní součty, laser, nastavení mřížky, posuny výrobků a výsledek kontroly (žádné motivy ani texty výrobků). Hodí se pro dohledání nebo hlášení chyby. Nastavení → **Protokol uložení**: *Neukládat* (výchozí), *Vedle uloženého projektu* (`<název>.json`), nebo *Do složky protokolů aplikace* (otevřete ji tamtéž položkou **Otevřít složku protokolů**).

Existující soubory ani originál se nikdy nepřepisují — pokud zvolený soubor (nebo jeho protokol vedle něj) už existuje, aplikace požádá o jiný název. Při jakékoli chybě nevznikne žádný výstup.

**Potom v LightBurnu:**

1. Otevřete výstup přes **File → Open** (ne Import — Import nenačte nastavení projektu).
2. Zkontrolujte vrstvy, výkony a rychlosti.
3. Spusťte **Preview** a prohlédněte dráhy.
4. Ověřte polohu na stroji (**Frame**). Teprve potom řežte, pod dohledem.

[← Deska](board.md) · [Řešení problémů →](troubleshooting.md)

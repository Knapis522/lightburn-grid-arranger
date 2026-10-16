# Uložení a kontrola v LightBurnu

Tlačítko **Uložit jako nový projekt** je aktivní, jen když rozložení prošlo kontrolou. Po potvrzení aplikace:

1. připraví nový soubor, ve kterém se změní jen polohy vybraných skupin (a jejich textů),
2. nezávisle ověří, že se nic jiného nezměnilo (vrstvy, výkony, texty, ostatní objekty),
3. ověří, že se originál od otevření nezměnil,
4. uloží **nový** soubor vedle originálu: `původní__grid_001.lbrn2` (další `_002`, …) a protokol `.json`.

Existující soubory se nikdy nepřepisují. Při jakékoli chybě nevznikne žádný výstup.

**Potom v LightBurnu:**

1. Otevřete výstup přes **File → Open** (ne Import — Import nenačte nastavení projektu).
2. Zkontrolujte vrstvy, výkony a rychlosti.
3. Spusťte **Preview** a prohlédněte dráhy.
4. Ověřte polohu na stroji (**Frame**). Teprve potom řežte, pod dohledem.

[← Deska](board.md) · [Řešení problémů →](troubleshooting.md)

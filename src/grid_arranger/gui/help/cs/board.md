# Deska, okraje a kontrola kolizí

**Deska** je obdélník materiálu v souřadnicích LightBurnu. Výchozí deska leží u počátku laseru (roh desky X 0, Y 0). Rozměr se předvyplní podle laseru uloženého v projektu; tlačítkem **Uložit jako výchozí pro tento laser** si nastavení zapamatujete. **Okraje** (výchozí 5 mm) jsou pás u hran desky, kam se nesmí nic umístit.

> Deska v aplikaci není pracovní plocha stroje. Skutečnou polohu materiálu a rámování ověřte na stroji.

Před uložením aplikace kontroluje:

- všechny přesouvané výrobky leží ve využitelné ploše desky,
- výrobky se nepřekrývají a dodržují mezeru,
- výrobky dodržují mezeru i od **nepřesouvaných** skupin a volných objektů,
- objekt, jehož rozměr nejde zjistit, uložení **zablokuje** (nelze potvrdit bezpečnost).

Chyby (✖) uložení blokují a uvádějí konkrétní výrobky. Upozornění (⚠) uložení nebrání. Aplikace nikdy sama nemění měřítko, neotáčí ani neposouvá nevybrané objekty.

Kontrola řeší obrysy v projektu, ne skutečný přesah při rastrování, kompenzaci šířky řezu ani pohyb hlavy — proto je **Preview v LightBurnu povinný**.

[← Mřížka](grid.md) · [Další: uložení →](save.md)

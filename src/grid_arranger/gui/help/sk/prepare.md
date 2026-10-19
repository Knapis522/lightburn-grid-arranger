# Príprava projektu v LightBurne

1. **Každý výrobok zoskupte samostatne** (Ctrl+G). Jedna skupina = jeden výrobok.
2. Každá skupina musí mať **uzavretý rezný obrys**, vnútri ktorého leží všetko ostatné (texty, motívy). Obrys môže mať zaoblené rohy alebo iný tvar — rozmer výrobku je obdĺžnik okolo obrysu. Obrysom môže byť krivka aj tvar nakreslený priamo v LightBurne (kruh, elipsa, obdĺžnik, mnohouholník); skupina môže obsahovať ďalšie skupiny (napr. kľúčenka: kruh s otvorom + text).
3. Projekt uložte (**Save As**) ako `.lbrn2`. Aplikácia číta len uložený súbor — neuložené zmeny v LightBurne nevidí.
4. Projekt ukladajte pre laser, na ktorom budete rezať. Aplikácia z projektu sama rozpozná laser a jeho počiatok (vľavo hore, vpravo hore, vľavo dole alebo vpravo dole — napr. diódové lasery). **Po prepnutí lasera v LightBurne projekt znova uložte** a znova ho otvorte.

Podporované: LightBurn 2.2, projekty `.lbrn2`, lasery s počiatkom v ktoromkoľvek rohu. Staršie súbory `.lbrn` aplikácia odmietne — uložte projekt v LightBurne ako `.lbrn2`.

## Projekt pre iný laser

Projekt uložený pre jeden laser môžete pripraviť pre iný, napr. z lasera s počiatkom vpravo hore pre laser s počiatkom vľavo hore — bez prepínania zariadenia a ručného prevracania v LightBurne. V sekcii **Projekt** zvoľte **Pripraviť pre:** laser z katalógu. Aplikácia ponúkne jeho dosku, mriežku plní od jeho počiatku a uložený súbor (`…__Nazov_lasera__grid_001.lbrn2`) je rovno preň: v súbore je cieľový laser a výrobky sú zrkadlovo prevrátené tak, aby na ňom vyzerali rovnako (texty čitateľné).

- Katalóg laserov: **Nastavenia → Lasery** (alebo *Spravovať lasery…* v ponuke). Lasery z otvorených projektov sa pridajú samy; ďalšie (napr. diódový) pridáte ručne — **názov musí zodpovedať zariadeniu v LightBurne**; zvoľte roh počiatku a dosku.
- Pri inom počiatku musia byť vybrané **všetky výrobky** a projekt nesmie obsahovať iné objekty (na druhom laseri by zostali zrkadlovo). Týka sa to len objektov ponechaných vo výstupe — nezaškrtnuté a vynechané objekty vo výstupe nebudú (predvolené nastavenie), takže prevodu neprekážajú.
- **Nastavenie vrstiev (výkon, rýchlosť) sa neprevádza** — zostáva z pôvodného projektu. Výstup otvorte v LightBurne s cieľovým laserom a vrstvy skontrolujte.

## Projekt s viacerými stranami

Otvoriť možno aj projekt s viacerými stranami (**Window → Pages** v LightBurne). V sekcii Projekt zvoľte **Rozložiť stranu:**; ostatné strany zostanú bez zmeny. Predvolená je strana, ktorá bola aktívna pri uložení projektu.

[← Úvod](index.md) · [Ďalej: výber a poradie →](items.md)

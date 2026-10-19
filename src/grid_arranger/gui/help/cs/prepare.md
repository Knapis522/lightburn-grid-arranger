# Příprava projektu v LightBurnu

1. Každý výrobek (kartičku) **seskupte samostatně** (Ctrl+G). Jedna skupina = jeden výrobek.
2. Každá skupina musí mít **uzavřený řezný obrys**, uvnitř kterého leží všechno ostatní (texty, motivy). Obrys může mít zaoblené rohy nebo jiný tvar — rozměr výrobku je obdélník kolem obrysu. Obrysem může být křivka i tvar nakreslený přímo v LightBurnu (kruh, elipsa, obdélník, mnohoúhelník); skupina může obsahovat další skupiny (např. klíčenka: kruh s otvorem + text).
3. Projekt uložte (**Save As**) jako `.lbrn2`. Aplikace čte jen uložený soubor — neuložené změny v LightBurnu nevidí.
4. Projekt ukládejte pro laser, na kterém budete řezat. Aplikace z projektu sama pozná laser a jeho počátek (vlevo nahoře, vpravo nahoře, vlevo dole nebo vpravo dole — např. diodové lasery). **Po přepnutí laseru v LightBurnu projekt znovu uložte** a otevřete znovu.

Podporováno: LightBurn 2.2, projekty `.lbrn2`, laser s počátkem v kterémkoli rohu. Starší `.lbrn` aplikace neotevře — uložte projekt v LightBurnu jako `.lbrn2`.

## Projekt pro jiný laser

Projekt uložený pro jeden laser můžete připravit pro jiný, např. z laseru s počátkem vpravo nahoře pro laser s počátkem vlevo nahoře — bez přepínání zařízení a ručního převracení v LightBurnu. V sekci **Projekt** zvolte **Připravit pro:** laser z katalogu. Aplikace nabídne jeho desku, mřížku plní od jeho počátku a uložený soubor (`…__Nazev_laseru__grid_001.lbrn2`) je rovnou pro něj: v souboru je cílový laser a výrobky jsou zrcadlově převrácené tak, aby na něm vypadaly stejně (texty čitelné).

- Katalog laserů: **Nastavení → Lasery** (nebo *Spravovat lasery…* v nabídce). Lasery z otevřených projektů se přidají samy; další (např. diodový) přidáte ručně — **název musí odpovídat zařízení v LightBurnu**, zvolte roh počátku a desku.
- Při jiném počátku musí být vybrány **všechny výrobky** a projekt nesmí obsahovat jiné objekty (na druhém laseru by zůstaly zrcadlově). To se týká jen objektů ponechaných ve výstupu — nezaškrtnuté a vynechané objekty ve výstupu nebudou (výchozí nastavení), takže převodu nevadí.
- **Nastavení vrstev (výkon, rychlost) se nepřevádí** — zůstává z původního projektu. Výstup otevřete v LightBurnu s cílovým laserem a vrstvy zkontrolujte.

## Projekt s více stránkami

Otevřít lze i projekt s více stránkami (**Window → Pages** v LightBurnu). V sekci Projekt zvolte **Rozložit stránku:**; ostatní stránky zůstanou beze změny. Výchozí je stránka, která byla aktivní při uložení projektu.

[← Úvod](index.md) · [Další: výběr a pořadí →](items.md)

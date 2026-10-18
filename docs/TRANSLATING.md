# Překlady

Zdrojový jazyk rozhraní je **angličtina**. Aplikace má osm jazyků: `cs`, `en`, `de`, `sk`, `pl`, `fr`, `es`, `it` (spec. kap. 36).

## Stav jazyků

| Jazyk | Rozhraní | Příručka (F1) | Revize člověkem |
|---|---|---|---|
| `en` English | zdroj | zdroj | — |
| `cs` Čeština | úplné | úplná | vlastník projektu |
| `de` Deutsch | úplné | úplná | **čeká** |
| `sk` Slovenčina | úplné | úplná | **čeká** |
| `pl` Polski | úplné | úplná | **čeká** |
| `fr` Français | úplné | úplná | **čeká** |
| `es` Español | úplné | úplná | **čeká** |
| `it` Italiano | úplné | úplná | **čeká** |

Překlady `de/sk/pl/fr/es/it` vytvořila AI (strojový návrh, 2026-10-18) podle anglického zdroje a slovníčku níže. Dokud je nezkontroluje člověk se znalostí jazyka a laserové terminologie, nejsou „plně podporované“ a nesplňují bránu `L10N-PUBLIC-01` (spec. kap. 36.5). Stránka příručky *Verze* v těchto jazycích na to upozorňuje. Revize je vítaná — viz *Příspěvek* níže.

## Kde co je

- `translations/gridarranger_<jazyk>.ts` — zdrojové katalogy rozhraní (XML, verzované v Gitu, editace v Qt Linguist nebo textovém editoru).
- `src/grid_arranger/gui/translations/*.qm` — sestavené katalogy (negitují se, přibalí se do EXE).
- `src/grid_arranger/gui/help/<jazyk>/*.md` — offline příručka (8 témat: `index`, `prepare`, `items`, `grid`, `board`, `save`, `troubleshooting`, `about`). Chybějící téma se zobrazí anglicky.

## Postup

Ve složce projektu (Windows):

```
cd C:\Users\marti\Documents\Claude\Projects\lightburn-grid-arranger
.venv\Scripts\activate
python tools\build_translations.py
```

Skript spustí `pyside6-lupdate` nad `src/grid_arranger/gui/*.py` (doplní nové a odstraní zastaralé řetězce), zkontroluje katalogy a sestaví `.qm` (`pyside6-lrelease`). `--no-update` přeskočí lupdate. Kontrola selže, když v katalogu `cs/de/sk/pl/fr/es/it` chybí překlad nebo nesedí placeholdery (`{name}`, `%n`) — neúplný katalog blokuje vydání.

Úprava překladu:

1. Otevřít `translations/gridarranger_<jazyk>.ts` v Qt Linguist (`pyside6-linguist`), přeložit / opravit, uložit.
2. Spustit `python tools\build_translations.py --no-update`.
3. Spustit aplikaci (`python -m grid_arranger.gui` nebo `spustit.bat`), přepnout jazyk v **Nastavení → Obecné → Jazyk** a projít okna. Hledat useknuté texty (T-I18N-21).
4. `python -m pytest tests\gui\test_i18n.py tests\gui\test_help.py`.

Pravidla:

- Placeholdery `{…}` a `%n` zachovat beze změny (pořadí ve větě se měnit smí).
- Množné číslo: `cs`, `sk`, `pl` mají tři tvary (1 / 2–4 / 5+; v polštině 12–14 patří k 5+), `de`, `fr`, `es`, `it`, `en` dva.
- Desetinná čárka/tečka se řídí jazykem (`QLocale`); výstupní `.lbrn2` je vždy stejný (T-I18N-20).
- Názvy z LightBurnu (`File → Open`, `Preview`, `Frame`, `Save As`, `Import`) a názvy souborů se nepřekládají.
- Příručka používá přesně stejné názvy ovládacích prvků jako přeložené rozhraní.

## Příspěvek

Opravy překladů přes GitHub Pull Request: změněný `.ts` a/nebo `help/<jazyk>/*.md`, v popisu jazyk a co bylo zkontrolováno. Příspěvky se nepřebírají automaticky; přispěvatel potvrzuje, že překlad smí poskytnout pod licencí MIT projektu. Po revizi celého jazyka se v tabulce výše uvede „hotovo“ s datem.

## Terminologický slovníček

Termíny s bezpečnostním významem se nesmějí zaměňovat.

| Čeština | English | Deutsch | Slovenčina | Polski | Français | Español | Italiano | Význam |
|---|---|---|---|---|---|---|---|---|
| výrobek | item | Objekt | výrobok | element | élément | elemento | elemento | jedna nejvyšší skupina = jeden kus |
| skupina | group | Gruppe | skupina | grupa | groupe | grupo | gruppo | `Group` v projektu LightBurnu |
| obrys | outline | Kontur | obrys | kontur | contour | contorno | contorno | vnější řezný obrys výrobku |
| mezera | gap | Abstand | medzera | odstęp | espacement | separación | spaziatura | vzdálenost mezi obrysy sousedních výrobků |
| rozteč | pitch | Rastermaß | rozostup | podziałka | pas | paso | passo | vzdálenost stejných bodů sousedních výrobků (≠ mezera) |
| počátek | origin | Nullpunkt | počiatok | punkt zerowy | origine | origen | origine | počátek souřadnic laseru |
| deska | board | Platte | doska | płyta | plaque | plancha | lastra | uživatelem zadaný obdélník materiálu (≠ pracovní plocha laseru) |
| okraj | margin | Rand | okraj | margines | marge | margen | margine | nepoužitelný pruh u hrany desky |
| kolize | collision | Kollision | kolízia | kolizja | collision | colisión | collisione | překryv obrysů nebo překážky |
| překážka | obstacle | Hindernis | prekážka | przeszkoda | obstacle | obstáculo | ostacolo | nepřesouvaný objekt v cílové oblasti |
| uložit jako nový projekt | save as new project | Als neues Projekt speichern | uložiť ako nový projekt | zapisz jako nowy projekt | enregistrer comme nouveau projet | guardar como proyecto nuevo | salva come nuovo progetto | vždy nový soubor, nikdy přepis |

# Překlady (kostra)

Zdrojový jazyk rozhraní je **angličtina**. Interní MVP: `cs` + `en`. První veřejné v1.0.0: `cs/en/de/sk/pl/fr/es/it` (spec. kap. 36).

Postup (`pyside6-lupdate` → Qt Linguist → `pyside6-lrelease`) se doplní při zahájení GUI.

## Terminologický slovníček

Termíny s bezpečnostním významem se nesmějí zaměňovat.

| Čeština | English | Význam |
|---|---|---|
| výrobek | item | jedna nejvyšší skupina = jeden kus |
| skupina | group | `Group` v projektu LightBurnu |
| obrys | outline | vnější řezný obdélník výrobku |
| mezera | gap | vzdálenost mezi obrysy sousedních výrobků |
| rozteč | pitch | vzdálenost stejných bodů sousedních výrobků (≠ mezera) |
| počátek | origin | levý horní roh mřížky |
| materiál / deska | material / board | uživatelem zadaný obdélník (≠ pracovní plocha laseru) |
| okraj | margin | nepoužitelný pruh u hrany materiálu |
| kolize | collision | překryv obrysů nebo překážky |
| překážka | obstacle | nepřesouvaný objekt v cílové oblasti |
| uložit nový projekt | save as new project | vždy nový soubor, nikdy přepis |

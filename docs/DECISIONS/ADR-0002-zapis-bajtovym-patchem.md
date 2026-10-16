# ADR-0002: Zápis `.lbrn2` cíleným přepisem bajtových úseků

**Datum:** 2026-10-16
**Stav:** Přijato (na základě KAL-00)

**Kontext:** Výstup musí měnit jen posuny vybraných skupin; vše ostatní má zůstat beze změny (spec. kap. 9.2, 21.5). LightBurn 2.2 ukládá deterministicky (opakované uložení = stejné bajty), používá CRLF a řádky až ~31 kB.

**Varianty:** A) načíst XML knihovnou a celý dokument znovu serializovat; B) přepsat jen bajtové úseky textu `<XForm>` určené streamovým parserem `expat`; C) regulární výraz nad textem.

**Rozhodnutí:** B. `expat` (standardní knihovna, bez externích entit) poskytne pozici každého `<XForm>`; mění se jen obsah mezi `<XForm>` a `</XForm>` u (1) nejvyšší přesouvané skupiny a (2) `BackupPath` každého textu v jejím podstromu. Čísla ve formátu `.8g`. Výstup se otevírá v režimu „nikdy nepřepsat“.

**Důvody:** prototyp v KAL-00 změnil přesně 2 řádky a výsledek odpovídal souboru uloženému LightBurnem (rozdíl jen thumbnail a zaokrouhlení 1,3·10⁻⁴ mm); LightBurn soubor otevřel správně. Diff se zjednoduší na „vše mimo povolené úseky je bajtově shodné“. Varianta A riskuje změnu formátování, pořadí atributů a konců řádků; C nemá kontext struktury (spec. ji výslovně zakazuje).

**Rizika:** nové verze LightBurnu mohou změnit strukturu → version gate a regresní vzorky (`FORMAT_COMPATIBILITY.md`).

**Odkazy:** spec. kap. 9.2, 41; `tools/kal00/patch_poc.py`; `docs/FORMAT_COMPATIBILITY.md` V-002.

# ADR-0005: Natočení výrobků pro úsporu materiálu

**Stav:** přijato 2026-10-17 (požadavek vlastníka; spec. v1.13 kap. 7.6); zápis natočení ověřen v LightBurnu (KAL-01 splněno 2026-10-17).
**Souvisí:** ADR-0002 (zápis bajtovým patchem), KAL-00 (BackupPath textů ve světových souřadnicích).

## Rozhodnutí

1. **Režimy** `any` (libovolný úhel, výchozí — volba vlastníka), `90`, `none`; společná volba + výjimky jednotlivých výrobků.
2. **Úhel**: nejmenší osový obdélník kolem konvexního obalu všech křivek výrobku (obrys, motivy, `BackupPath` textů; Bézier rozvinutý s odchylkou ≤ 0,002 mm, obdélník o ni zvětšen). Natáčí se jen při úspoře ≥ 0,5 % — kruhy a obdélníky zůstanou rovně.
3. **Orientace**: varianty „beze změny“ / „vše na šířku“ / „vše na výšku“; vybere se ta, která se vejde na desku, a z nich nejmenší plocha mřížky (jiná než beze změny jen při úspoře ≥ 0,5 %). Při otočení o 90° navíc menší celkový úhel (−60° místo 120°).
4. **Zápis**: výrobek se natočí kolem středu obrysu a posune; transformace jádra `T` se převede do souboru `S ∘ T ∘ S` (`S = diag(±1, ±1)` podle MirrorX/Y) a zapíše jako `XForm' = T ∘ XForm` u skupiny i u `BackupPath` každého textu. Násobky 90° používají přesné 0/±1.
5. **Kontroly**: nezávislá kontrola porovná celou matici (lineární část 1e-6, posun 1e-3 mm); po znovunačtení výstupu musí skutečné křivky natočených výrobků ležet v cílovém obdélníku (±0,02 mm, násobky 90° ±0,001 mm).

## Důsledky

- Výstup je dál bajtově shodný mimo `XForm`; bez natočení se chování nemění (čistý posun).
- Natočení o 180° se nedělá samo (plochu nezmenší) — výrobek „vzhůru nohama“ zůstane, jak je.
- KAL-01 ověřeno vlastníkem v LightBurnu 2.2.00-RC-7 pro oba typy laseru (natočené skupiny i texty, srovnání výstupem aplikace).

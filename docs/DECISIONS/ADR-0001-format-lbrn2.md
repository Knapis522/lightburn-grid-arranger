# ADR-0001: Výhradní projektový formát `.lbrn2`

**Datum:** 2026-10-15
**Stav:** Přijato (FMT-00, spec. kap. 41)

**Kontext:** LightBurn ukládá projekty jako `.lbrn2` (výchozí, doporučený) nebo `.lbrn` (Legacy Project). Podpora obou by zdvojila adaptér i testy.

**Varianty:** A) pouze `.lbrn2`  B) `.lbrn2` + `.lbrn`  C) `.lbrn2` s automatickou konverzí z `.lbrn`

**Rozhodnutí:** A — pouze `.lbrn2` pro vstup i výstup, ve všech verzích (MVP, 1.1, 2.0).

**Důvody:** aktuální doporučený formát; žádná investice do legacy podpory; menší testovací matice.

**Důsledky:** `.lbrn` se odmítá s lokalizovanou hláškou, bez konverze. Architektura obsahuje jen `Lbrn2ProjectAdapter`. Schválení formátu neznamená ověřenou proveditelnost adaptéru — to prokáže KAL-00.

**Odkazy:** spec. kap. 41; T-FMT-01 až 07.

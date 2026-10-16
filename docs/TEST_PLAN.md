# Testovací plán

Úplné definice testů jsou ve specifikaci; zde se eviduje **stav a důkaz**. Stavy: `nezahájeno` / `napsán` / `prochází` / `selhává` / `ruční – ověřeno`.

| Sada | ID | Kap. spec. | Typ | Stav | Důkaz |
|---|---|---|---|---|---|
| Algoritmus | ALG-01 – ALG-10 | 14.1 | automatický (pytest) | nezahájeno | — |
| Integrace `.lbrn2` | LB-01 – LB-13 | 14.2 | automatický + ruční v LightBurnu | nezahájeno | — |
| Invariance MVP | — | 14.3 | automatický | nezahájeno | — |
| MVP funkce | T-MVP-01 – T-MVP-26 | 26.1 | automatický / ruční (T-MVP-26) | nezahájeno | — |
| Formát | T-FMT-01 – T-FMT-07 | 41.5 | automatický / ruční | nezahájeno | — |
| Lokalizace (interní) | T-I18N-01 – T-I18N-16 | 36.6 | automatický / ruční | nezahájeno | — |
| Lokalizace (veřejná) | T-I18N-17 – T-I18N-22 | 36.6 | ruční | nezahájeno | — |
| Nápověda | T-HELP-01 – T-HELP-10 | 38.5 | ruční | nezahájeno | — |
| Dokumentace | T-DOC-01 – T-DOC-07 | 40.1 | kontrola | nezahájeno | — |
| Řízení | T-PLAN-01 – T-PLAN-06 | 39.6 | kontrola | nezahájeno | — |
| GitHub / distribuce | GH-01 – GH-16 | 34 | ruční | nezahájeno | — |
| Verze 1.1 | T-11-01 – T-11-20 | 26.2 | — | plánováno | — |
| Verze 2.0 | T-20-01 – T-20-19 | 26.3 | — | plánováno | — |

## Testovací data

- Automatické testy používají jen syntetické soubory v `tests/fixtures/synthetic/`.
- Reálné projekty pro ruční a kompatibilitní testy leží mimo Git v `..\lightburn-grid-arranger-data\`.
- Každý ruční test v LightBurnu zapsat: datum, verze LightBurnu, verze Windows, soubor (jen název), výsledek, poznámka.

## Protokol ručních testů

| Datum | Test | LightBurn | Soubor | Výsledek | Poznámka |
|---|---|---|---|---|---|
| 2026-10-16 | GH-01 | — | — | prochází | Repo publikováno jako Private; v commitu `55ab47e` jen 9 dokumentačních souborů, žádný `.lbrn2` |
| 2026-10-16 | GH-02 | — | — | probíhá | Commit + push změny `docs/STATUS.md`, `ROADMAP.md`, `TEST_PLAN.md` |

# KAL-00 — diagnostické prototypy

Jednorázové skripty použité při ověření formátu `.lbrn2` (2026-10-16). **Nejsou součástí aplikace** a nesmí se používat na výrobní projekty; čistá implementace vznikne v etapě ADAPT-00.

- `inspect_lbrn2.py <soubor>` — vypíše skupiny, vrstvy, AABB obrysů a textů (`BackupPath`); jen čte.
- `patch_poc.py <zdroj> <cíl> <index_skupiny> <dx> <dy>` — posune jednu skupinu nejvyšší úrovně přepsáním bajtových úseků `XForm` (skupina + `BackupPath` textů); cílový soubor nikdy nepřepíše.

Výsledky viz `docs/FORMAT_COMPATIBILITY.md`.

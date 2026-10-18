# ADR-0004: Instalátor Inno Setup a nabízené aktualizace z GitHub Releases

**Stav:** přijato 2026-10-17 (požadavek vlastníka; spec. v1.11 kap. 12.1, 31.2, 32).
**Souvisí:** ADR-0003 (PyInstaller onedir).

## Kontext

Vlastník chce místo ZIPu instalační balíček a v nastavení volbu automatické nebo ruční kontroly aktualizací. Nová verze se má jen nabídnout; uživatel může zůstat u staré, a když mezitím vyjde více verzí, nainstaluje rovnou nejnovější. Repozitář je zatím soukromý, výhledově veřejný.

## Rozhodnutí

1. **Instalátor Inno Setup 6.3+** (`packaging/GridArranger.iss`) nad složkou z PyInstalleru: per-user bez práv správce (`%LOCALAPPDATA%\Programs\Grid Arranger`), stálé `AppId`, nabídka Start, volitelně ikona na ploše, odinstalace; před instalací smaže `_internal` předchozí verze. ZIP zůstává jako záloha. Jednosouborové EXE ne (rozbalování při každém startu, plané poplachy antiviru).
2. **Kontrola aktualizací** (`grid_arranger/updates.py`, GUI `gui/updates_ui.py`) přes anonymní GitHub REST API `/releases`; SemVer 2.0 včetně předběžných verzí; vždy nejnovější vydání; přeskočení verze; automatická kontrola na pozadí při každém spuštění (od spec. v1.21 na přání vlastníka, dříve nejvýš ~1× denně), chyby jen do logu.
3. **Instalace jen po souhlasu**: stažení do nové dočasné složky, ověření proti `SHA256SUMS.txt` z téhož vydání, pak ukončení aplikace a spuštění instalátoru `/SILENT`; instalátor aplikaci znovu spustí (`[Run] … Check: WizardSilent`). Kopie ze ZIPu jen otevře stránku ke stažení.
4. Síť přes `urllib` (standardní knihovna, certifikáty Windows), ne QtNetwork — knihovna Qt6Network se do balíčku nepřibaluje (ADR-0003).

## Zvažované alternativy

- **Token v aplikaci pro soukromý repozitář** — zamítnuto: token by šlo z EXE vytáhnout (spec. kap. 29: žádné tokeny).
- **Sdílená síťová složka ve firmě** — nepotřebné, vlastník plánuje veřejný repozitář.
- **Hotový aktualizační framework (např. WinSparkle)** — zbytečná další závislost a podepisovací infrastruktura; potřebná logika je malá a testovatelná.

## Důsledky

- Do zveřejnění repozitáře ruční kontrola oznámí „žádná veřejná vydání“ (API vrací 404); automatická mlčí.
- Ke každému Release je nutné přiložit instalátor, ZIP a `SHA256SUMS.txt` — vyrábí je `tools/build_exe.py`.
- Integrita = HTTPS + SHA-256 z téhož Release; ochranu proti kompromitaci účtu GitHub by dal až podpis instalátoru (zvážit před veřejnou distribucí).
- Na vývojovém PC je potřeba jednou nainstalovat Inno Setup (`winget install JRSoftware.InnoSetup`).

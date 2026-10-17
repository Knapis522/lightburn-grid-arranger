# Postup vydání (interní)

Podle spec. kap. 30.3, 31.3 a brány REL-01 (kap. 33.1). Popisy na GitHubu (commit, tag, release notes) **anglicky**.

## Číslo verze

- Jediný zdroj: `src/grid_arranger/version.py` (`__version__` v PEP 440, např. `0.1.0a1`).
- Tag, název ZIPu, okno O aplikaci a release notes používají SemVer z `display_version()`: `0.1.0-alpha.1` → tag `v0.1.0-alpha.1`.
- Předběžné verze: `aN` → `-alpha.N`, `bN` → `-beta.N`, `rcN` → `-rc.N`. Stabilní `1.0.0` až po MVP-ACCEPT a PUB-01.
- Jednou vydaný instalátor/ZIP se pod stejným číslem nikdy nenahrazuje — oprava = nové číslo (aplikace podle čísla pozná novou verzi).

## Kroky

1. `version.py` a `CHANGELOG.md` (sekce verze s datem), `docs/releases/v<verze>.md` (anglicky, osnova spec. kap. 31.4), `STATUS.md`.
2. **Commit a push** v GitHub Desktop (seznam Changes musí zůstat prázdný).
3. `tools\build_exe.bat` → testy, PyInstaller, samokontrola; vše ve složce `dist\v<verze>\`: instalátor, ZIP, `SHA256SUMS.txt`, `RELEASE_NOTES.md`. V `dist\v<verze>\GridArranger\README.txt` je commit, ze kterého sestavení vzniklo — musí odpovídat poslednímu commitu.
4. GitHub Desktop: **History** → pravým tlačítkem na poslední commit → **Create Tag…** → `v<verze>` → **Push origin**.
5. github.com → **Releases** → **Draft a new release** → zvolit tag → titulek `Grid Arranger v<verze>` → text z `RELEASE_NOTES.md` ve složce verze → přiložit **instalátor, ZIP a `SHA256SUMS.txt`** (bez instalátoru a součtů aplikace aktualizaci jen nabídne ke stažení) → u předběžné verze zaškrtnout **Set as a pre-release** → **Publish release** (u soukromého repozitáře vidí jen vlastník a přizvaní).
6. Stáhnout instalátor z GitHubu, ověřit `Get-FileHash` proti `SHA256SUMS.txt`, nainstalovat na počítači bez Pythonu a projít ruční scénář (GH-05, T-I18N-16, HELP-01); po zveřejnění repozitáře ověřit i aktualizaci ze starší verze přes Nápověda → Zkontrolovat aktualizace (T-UPD-07). Výsledek zapsat do `TEST_PLAN.md`.

## REL-01 pro interní předběžnou verzi (kontrola před krokem 5)

- [ ] Všechny automatické testy prošly (součást `build_exe.bat`).
- [ ] Samokontrola zabaleného EXE 5/5.
- [ ] Ruční test výstupu v LightBurnu (File → Open, Preview) zapsán v `TEST_PLAN.md`.
- [ ] `version.py`, tag, název ZIPu a release notes mají stejné číslo.
- [ ] Release notes uvádějí kompatibilitu, známá omezení a nutnost kontroly v LightBurnu.
- [ ] Žádný zákaznický `.lbrn2`, token ani heslo v commitu ani v ZIPu.
- [ ] Před označením stabilní verze navíc: test na Windows bez Pythonu (GH-05) a MVP-ACCEPT.

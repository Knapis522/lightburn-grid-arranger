# Verze, podporované soubory a data

- Číslo verze aplikace: **Nápověda → O aplikaci**.
- Ověřeno s: LightBurn 2.2.00, projekty `.lbrn2`, lasery s počátkem v kterémkoli rohu (vlevo a vpravo nahoře na skutečných laserech, vlevo a vpravo dole s testovacím zařízením v LightBurnu).
- Aplikace pracuje **offline** a neovládá laser. Jediné spojení s internetem je kontrola aktualizací na GitHubu (bez jakýchkoli údajů o projektech); lze ji vypnout v **Nastavení → Aktualizace**.
- **Nastavení** (položka v liště menu, ikona ozubeného kola, Ctrl+,) se otevře jako samostatné okno se stránkami *Obecné*, *Lasery* (katalog laserů — viz [Projekt pro jiný laser](prepare.md)), *Uložení* (nezaškrtnuté objekty, protokol uložení) a *Aktualizace*. Změny se projeví tlačítkem **OK** nebo **Použít**; **Zrušit** okno zavře beze změny (po *Použít* se tlačítko jmenuje **Zavřít**).
- **Jazyk:** **Nastavení → Obecné → Jazyk** — Automaticky (podle Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Každý jazyk je uveden svým vlastním názvem. Překlady do němčiny, slovenštiny, polštiny, francouzštiny, španělštiny a italštiny jsou strojové a čekají na kontrolu rodilým mluvčím.
- **Panel rozložení:** **Nastavení → Obecné → Panel rozložení** — sekce Projekt, Výrobky, Mřížka, Umístění a Deska vlevo, nebo vpravo od náhledu.
- Vzhled aplikace: **Nastavení → Obecné → Vzhled** (automaticky podle Windows; světlý = celá aplikace světlá; tmavý = tmavé ovládání, náhled desky zůstává světlý).
- **Jednotky:** **Nastavení → Obecné → Jednotky** — milimetry nebo palce (jako v LightBurnu). Mění se jen zobrazení a zadávání hodnot; výpočet i uložený projekt jsou vždy v milimetrech, takže přepnutí jednotek nic neposune.
- Sekce bočního panelu (Projekt, Výrobky, Mřížka, …) lze kliknutím na hlavičku sbalit; stav se pamatuje.
- Nastavení (jazyk, vzhled, jednotky, strana panelu, výchozí desky podle laseru, katalog laserů, profily) se ukládá do uživatelského profilu Windows, ne do projektu.
- Instalace: spusťte `GridArranger-Setup-….exe` (nepotřebuje práva správce; aplikace se objeví v nabídce Start). Záložní varianta bez instalace: rozbalte ZIP a spusťte `GridArranger.exe` — musí zůstat vedle složky `_internal`.
- **Aktualizace:** při zapnuté automatické kontrole (**Nastavení → Aktualizace**) aplikace při každém spuštění nabídne novou verzi; kdykoli také tlačítkem **Zkontrolovat aktualizace** v **Nastavení → Aktualizace** (nebo Nápověda → Zkontrolovat aktualizace). Vždy se nabízí nejnovější verze s přehledem změn. Můžete ji nainstalovat (aplikace se zavře, nainstaluje novou verzi a znovu se spustí), připomenout později, nebo verzi přeskočit — novější vám aplikace nabídne znovu. Nic se neinstaluje bez vašeho souhlasu; stažený instalátor se před spuštěním ověří kontrolním součtem. Předběžné (testovací) verze se nabízejí jen při zapnuté volbě „Nabízet i předběžné verze“.
- Projekt lze otevřít i přetažením souboru `.lbrn2` na `GridArranger.exe`.
- Kopii ze ZIPu aktualizujete ručně: novou verzi rozbalte do nové složky; nastavení se zachová.

[← Úvod](index.md)

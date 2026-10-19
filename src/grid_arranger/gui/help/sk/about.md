# Verzia, podporované súbory a údaje

- Číslo verzie aplikácie: **Pomocník → O aplikácii**.
- Overené s: LightBurn 2.2.00, projekty `.lbrn2`, lasery s počiatkom v ktoromkoľvek rohu (vľavo a vpravo hore na skutočných laseroch, vľavo a vpravo dole s testovacím zariadením v LightBurne).
- Aplikácia pracuje **offline** a neovláda laser. Jediné spojenie s internetom je kontrola aktualizácií na GitHube (bez akýchkoľvek údajov o projektoch); dá sa vypnúť v **Nastavenia → Aktualizácie**.
- **Nastavenia** (položka v ponukovej lište, ikona ozubeného kolesa, Ctrl+,) sa otvoria ako samostatné okno so stránkami *Všeobecné*, *Lasery* (katalóg laserov — pozri [Projekt pre iný laser](prepare.md)), *Ukladanie* (nezaškrtnuté objekty, protokol uloženia) a *Aktualizácie*. Zmeny sa prejavia tlačidlom **OK** alebo **Použiť**; **Zrušiť** okno zavrie bez zmeny (po *Použiť* sa tlačidlo volá **Zavrieť**).
- **Nastavenia → Dosky:** predvolený spôsob rozdelenia na viac dosiek, doplnenie poslednej dosky, upozornenie nad určitý počet dosiek a uloženie ako strany alebo samostatné súbory — pozri [Viac dosiek](board.md).
- **Jazyk:** **Nastavenia → Všeobecné → Jazyk** — Automaticky (podľa Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Každý jazyk je uvedený vlastným názvom.
- **Panel rozloženia:** **Nastavenia → Všeobecné → Panel rozloženia** — sekcie Projekt, Výrobky, Mriežka, Umiestnenie a Doska vľavo alebo vpravo od náhľadu.
- Vzhľad aplikácie: **Nastavenia → Všeobecné → Vzhľad** (automaticky podľa Windows; svetlý = celá aplikácia svetlá; tmavý = tmavé ovládanie, náhľad dosky zostáva svetlý).
- **Jednotky:** **Nastavenia → Všeobecné → Jednotky** — milimetre alebo palce (ako v LightBurne). Mení sa len zobrazovanie a zadávanie hodnôt; výpočet aj uložený projekt sú vždy v milimetroch, takže prepnutie jednotiek nič neposunie.
- Sekcie bočného panela (Projekt, Výrobky, Mriežka, …) sa dajú zbaliť kliknutím na ich hlavičku; stav sa pamätá.
- Nastavenia (jazyk, vzhľad, jednotky, strana panela, predvolené dosky podľa lasera, katalóg laserov, profily, názvy výrobkov, priečinok naposledy otvoreného projektu) sa ukladajú do používateľského profilu Windows, nie do projektu.
- Inštalácia: spustite `GridArranger-Setup-….exe` (netreba práva správcu; aplikácia sa objaví v ponuke Štart). Náhradne bez inštalácie: rozbaľte ZIP a spustite `GridArranger.exe` — musí zostať vedľa priečinka `_internal`.
- **Aktualizácie:** pri zapnutej automatickej kontrole (**Nastavenia → Aktualizácie**) aplikácia po každom spustení ponúkne novú verziu; kedykoľvek aj tlačidlom **Skontrolovať aktualizácie** v **Nastavenia → Aktualizácie** (alebo Pomocník → Skontrolovať aktualizácie). Vždy sa ponúka najnovšia verzia s prehľadom zmien. Môžete ju nainštalovať (aplikácia sa zavrie, nainštaluje novú verziu a znova sa spustí), pripomenúť neskôr alebo verziu preskočiť — novšia sa ponúkne znova. Bez vášho súhlasu sa nič neinštaluje; stiahnutý inštalátor sa pred spustením overí kontrolným súčtom. Predbežné (testovacie) verzie sa ponúkajú len so zapnutou voľbou „Ponúkať aj predbežné verzie“.
- Projekt sa dá otvoriť aj pretiahnutím súboru `.lbrn2` na `GridArranger.exe`.
- Kópia zo ZIPu sa aktualizuje ručne: novú verziu rozbaľte do nového priečinka; nastavenia zostanú.

> Poznámka: tento preklad bol vytvorený strojovo a čaká na kontrolu rodeným hovoriacim.

[← Úvod](index.md)

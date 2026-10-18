# Wersja, obsługiwane pliki i dane

- Wersja aplikacji: **Pomoc → O programie**.
- Sprawdzono z: LightBurn 2.2.00, projektami `.lbrn2`, laserami z punktem zerowym w dowolnym rogu (lewy i prawy górny na prawdziwych laserach, lewy i prawy dolny z urządzeniami testowymi w LightBurn).
- Aplikacja działa **offline** i nie steruje laserem. Jedynym połączeniem z internetem jest sprawdzanie aktualizacji na GitHub (bez żadnych danych o projektach); można je wyłączyć w **Ustawienia → Aktualizacje**.
- **Ustawienia** (pozycja na pasku menu, ikona koła zębatego, Ctrl+,) otwierają osobne okno ze stronami *Ogólne*, *Lasery* (katalog laserów — zobacz [Projekt dla innego lasera](prepare.md)), *Zapisywanie* (niezaznaczone obiekty, protokół zapisu) i *Aktualizacje*. Zmiany obowiązują po **OK** lub **Zastosuj**; **Anuluj** zamyka okno bez zmian (po *Zastosuj* przycisk nazywa się **Zamknij**).
- **Język:** **Ustawienia → Ogólne → Język** — Automatycznie (według Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Każdy język jest podany własną nazwą.
- **Panel układu:** **Ustawienia → Ogólne → Panel układu** — sekcje Projekt, Elementy, Siatka, Umieszczenie i Płyta z lewej lub z prawej strony podglądu.
- Wygląd: **Ustawienia → Ogólne → Wygląd** (automatycznie według Windows; jasny = cała aplikacja jasna; ciemny = ciemne elementy sterujące, podgląd płyty pozostaje jasny).
- **Jednostki:** **Ustawienia → Ogólne → Jednostki** — milimetry lub cale (jak w LightBurn). Zmienia się tylko wyświetlanie i wprowadzanie wartości; obliczenia i zapisany projekt są zawsze w milimetrach, więc zmiana jednostek niczego nie przesuwa.
- Sekcje panelu bocznego (Projekt, Elementy, Siatka, …) można zwinąć, klikając ich nagłówek; stan jest zapamiętywany.
- Ustawienia (język, wygląd, jednostki, strona panelu, domyślne płyty dla laserów, katalog laserów, profile) są zapisywane w profilu użytkownika Windows, a nie w projekcie.
- Instalacja: uruchom `GridArranger-Setup-….exe` (nie są potrzebne uprawnienia administratora; aplikacja pojawi się w menu Start). Zastępczo bez instalacji: rozpakuj ZIP i uruchom `GridArranger.exe` — musi pozostać obok folderu `_internal`.
- **Aktualizacje:** przy włączonym automatycznym sprawdzaniu (**Ustawienia → Aktualizacje**) aplikacja po każdym uruchomieniu zaproponuje nową wersję; w dowolnej chwili także przyciskiem **Sprawdź aktualizacje** w **Ustawienia → Aktualizacje** (lub Pomoc → Sprawdź aktualizacje). Zawsze proponowana jest najnowsza wersja z listą zmian. Możesz ją zainstalować (aplikacja zamknie się, zainstaluje nową wersję i uruchomi się ponownie), przypomnieć sobie później lub pominąć wersję — nowsza zostanie zaproponowana ponownie. Bez Twojej zgody nic nie jest instalowane; pobrany instalator jest przed uruchomieniem weryfikowany sumą kontrolną. Wersje wstępne (testowe) są proponowane tylko przy włączonej opcji „Uwzględniaj wersje wstępne”.
- Projekt można też otworzyć, przeciągając plik `.lbrn2` na `GridArranger.exe`.
- Kopię z pliku ZIP aktualizuje się ręcznie: rozpakuj nową wersję do nowego folderu; ustawienia zostaną zachowane.

> Uwaga: to tłumaczenie zostało przygotowane maszynowo i czeka na sprawdzenie przez rodzimego użytkownika języka.

[← Wprowadzenie](index.md)

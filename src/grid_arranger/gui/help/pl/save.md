# Zapis i kontrola w LightBurn

Ikona **Zapisz jako nowy projekt** na pasku narzędzi (lub **Plik → Zapisz jako nowy projekt**, Ctrl+S) jest aktywna tylko wtedy, gdy układ przeszedł kontrolę. Otwiera się okno zapisu z proponowaną nazwą `oryginal__grid_001.lbrn2` (potem `_002`, …) w folderze oryginału — **folder i nazwę można zmienić**. Po potwierdzeniu aplikacja:

1. przygotowuje nowy plik, w którym zmieniają się tylko położenia zaznaczonych grup (i ich tekstów), pominięte obiekty są usuwane,
2. niezależnie sprawdza, czy nic innego się nie zmieniło (warstwy, moc, teksty, inne obiekty),
3. sprawdza, czy oryginał nie zmienił się od otwarcia,
4. zapisuje **nowy** plik pod wybraną nazwą.

**Protokół zapisu** (`.json`) — zapis tego, z czego i jak powstał wynik: sumy kontrolne, laser, ustawienia siatki, przesunięcia elementów i wynik kontroli (bez grafiki i tekstów elementów). Przydatny do śledzenia lub zgłaszania problemu. **Ustawienia → Zapisywanie → Protokół zapisu**: *Nie zapisuj* (domyślnie), *Obok zapisanego projektu* (`<nazwa>.json`) lub *W folderze protokołów aplikacji* (otworzysz go tam przyciskiem **Otwórz folder protokołów**).

**Po zapisie pracujesz dalej z oryginałem.** Zapisany plik jest osobną nową kopią; oryginalny projekt pozostaje otwarty w aplikacji, więc możesz wypróbować inny układ i zapisać kolejny wariant (`_002`, …). Pasek tytułu i sekcja Projekt pokazują *ostatnio zapisano jako …*. Aby zamiast tego kontynuować z zapisanym plikiem (jak „Zapisz jako”), zaznacz w komunikacie o zapisie **Kontynuuj pracę z zapisanym plikiem** — zostanie otwarty zamiast oryginału, jego kopie i obroty są już utrwalone, a historia cofania zaczyna się od nowa. Kolejny zapis kontynuuje wtedy numerację oryginału (`_002`, a nie `__grid_001__grid_001`).

Istniejące pliki ani oryginał nigdy nie są nadpisywane — jeśli wybrany plik (lub jego protokół obok) już istnieje, aplikacja poprosi o inną nazwę. W razie jakiegokolwiek błędu wynik nie powstaje.

**Następnie w LightBurn:**

1. Otwórz wynik: w komunikacie o zapisie przyciskiem **Otwórz w LightBurn** (lub ikoną na pasku narzędzi, **Plik → Otwórz zapisany projekt w LightBurn**, Ctrl+L). Aplikacja otwiera plik tak jak dwuklik w Eksploratorze: uruchomiony LightBurn zastępuje otwarty projekt — jeśli ma niezapisane zmiany, sam zapyta o zapis; w przeciwnym razie LightBurn się uruchomi. Ręcznie otwieraj przez **File → Open** (nie Import — Import nie wczytuje ustawień projektu).
2. Sprawdź warstwy, moc i prędkość.
3. Uruchom **Preview** i obejrzyj ścieżki.
4. Sprawdź położenie na maszynie (**Frame**). Dopiero potem tnij, pod nadzorem.

[← Płyta](board.md) · [Rozwiązywanie problemów →](troubleshooting.md)

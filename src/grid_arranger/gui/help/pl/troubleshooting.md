# Rozwiązywanie problemów

**„Aplikacja obsługuje tylko projekty .lbrn2”** — zapisz projekt w LightBurn jako `.lbrn2`.

**„Nieobsługiwana wersja LightBurn”** — projekt został zapisany wersją LightBurn, z którą aplikacja nie była sprawdzana. Wynik mógłby nie być bezpieczny, dlatego jest odrzucany.

**Element „nie można przesunąć”** — najedź na niego myszą. Najczęściej: grupa nie ma zamkniętego konturu cięcia, coś wystaje poza kontur, jest zablokowana lub zawiera typ obiektu, którego aplikacja nie potrafi jeszcze bezpiecznie przesunąć (np. bitmapę).

**„Geometria tekstu nie odpowiada jego położeniu”** — otwórz projekt w LightBurn i zapisz go ponownie.

**Zapis jest zablokowany** — przeczytaj błędy (✖) pod podglądem: przekroczenie płyty, kolizja, za mały odstęp lub obiekt, którego nie można zmierzyć. Zmień kolumny, odstępy, płytę lub zaznaczenie.

**„Oryginalny plik zmienił się od otwarcia”** — projekt został w międzyczasie ponownie zapisany. Otwórz go w aplikacji jeszcze raz.

**Windows wyświetla „System Windows ochronił ten komputer”** — aplikacja nie jest jeszcze podpisana cyfrowo. Jeśli instalator pochodzi z wydań tego projektu na GitHub, kliknij **Więcej informacji → Uruchom mimo to**. Nie wyłączaj programu antywirusowego.

**Aplikacja się nie uruchamia lub zgłasza brakujący plik** — najprawdopodobniej brakuje folderu `_internal` obok `GridArranger.exe` (np. skopiowano tylko EXE). Rozpakuj ponownie cały ZIP. Aby sprawdzić instalację, uruchom w wierszu poleceń `GridArranger.exe --self-test report.json`; wynik zostanie zapisany w `report.json`.

**Zgłaszanie problemu** — włącz Ustawienia → Zapisywanie → Protokół zapisu, zapisz ponownie i wyślij protokół `.json` (zawiera sumy kontrolne i parametry, a nie zawartość elementów) oraz opis kroków. Projekty klientów wysyłaj tylko za zgodą.

[← Wprowadzenie](index.md)

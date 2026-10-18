# Przygotowanie projektu w LightBurn

1. **Zgrupuj każdy element osobno** (Ctrl+G). Jedna grupa = jeden element.
2. Każda grupa musi mieć **zamknięty kontur cięcia**, wewnątrz którego leży wszystko inne (teksty, grafika). Kontur może mieć zaokrąglone rogi lub inny kształt — rozmiar elementu to prostokąt wokół konturu. Konturem może być krzywa lub kształt narysowany bezpośrednio w LightBurn (koło, elipsa, prostokąt, wielokąt); grupa może zawierać kolejne grupy (np. brelok: koło z otworem + tekst).
3. Zapisz projekt (**Save As**) jako `.lbrn2`. Aplikacja czyta tylko zapisany plik — nie widzi niezapisanych zmian w LightBurn.
4. Zapisuj projekt dla lasera, na którym będziesz ciąć. Aplikacja sama rozpoznaje z projektu laser i jego punkt zerowy (w lewym górnym, prawym górnym, lewym dolnym lub prawym dolnym rogu — np. lasery diodowe). **Po zmianie lasera w LightBurn zapisz projekt ponownie** i otwórz go jeszcze raz.

Obsługiwane: LightBurn 2.2, projekty `.lbrn2`, lasery z punktem zerowym w dowolnym rogu. Starsze pliki `.lbrn` są odrzucane — zapisz projekt w LightBurn jako `.lbrn2`.

## Projekt dla innego lasera

Projekt zapisany dla jednego lasera można przygotować dla innego, np. z lasera z punktem zerowym w prawym górnym rogu dla lasera z punktem zerowym w lewym górnym rogu — bez przełączania urządzenia i ręcznego odbijania projektu w LightBurn. W sekcji **Projekt** wybierz **Przygotuj dla:** laser z katalogu. Aplikacja zaproponuje jego płytę, wypełni siatkę od jego punktu zerowego, a zapisany plik (`…__Nazwa_lasera__grid_001.lbrn2`) będzie od razu dla niego: plik wskazuje docelowy laser, a elementy są odbite lustrzanie tak, aby wyglądały na nim tak samo (teksty czytelne).

- Katalog laserów: **Ustawienia → Lasery** (lub *Zarządzaj laserami…* na liście). Lasery z otwartych projektów są dodawane automatycznie; kolejne (np. diodowy) dodaj ręcznie — **nazwa musi odpowiadać urządzeniu w LightBurn**; wybierz róg punktu zerowego i płytę.
- Przy innym punkcie zerowym muszą być zaznaczone **wszystkie elementy**, a projekt nie może zawierać innych obiektów (na drugim laserze pozostałyby odbite lustrzanie). Dotyczy to tylko obiektów pozostawionych w wyniku — niezaznaczone i pominięte obiekty nie trafiają do wyniku (ustawienie domyślne), więc nie przeszkadzają.
- **Ustawienia warstw (moc, prędkość) nie są przeliczane** — pozostają jak w oryginalnym projekcie. Otwórz wynik w LightBurn z docelowym laserem i sprawdź warstwy.

[← Wprowadzenie](index.md) · [Dalej: elementy →](items.md)

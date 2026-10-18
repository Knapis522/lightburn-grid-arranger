# Wybór i kolejność elementów

Po otwarciu projektu (ikona **Otwórz projekt** na pasku narzędzi, **Plik → Otwórz projekt** lub Ctrl+O) lista pokazuje wszystkie grupy najwyższego poziomu:

- **Zaznaczone** elementy są rozmieszczane w siatce. Liczba przed nazwą to ich pozycja w siatce.
- **Niezaznaczone** elementy nie trafiają do wyniku: nie ma ich w zapisanym projekcie, a siatka ich nie uwzględnia. Jeśli wolisz zostawić je na miejscu, wybierz **Ustawienia → Zapisywanie → Niezaznaczone obiekty → Zostaw na miejscu** — siatka będzie je wtedy omijać.
- **Szare** elementy („nie można przesunąć”) zostały odrzucone — najedź na nie myszą, aby zobaczyć powód. Nigdy nie są przesuwane.
- ⚠ oznacza ostrzeżenie (np. tekst, którego nie można zmierzyć) — element można użyć, ale sprawdź go w Preview.
- **Pomijanie obiektów:** zaznacz pozycje na liście (również szare) i naciśnij **Delete** (albo **Edycja → Pomiń w wyniku** lub prawy przycisk myszy). Trafiają przekreślone na koniec listy i nie ma ich w zapisanym projekcie — przydatne, gdy z dużego projektu potrzebujesz tylko części. **Edycja → Przywróć pominięte obiekty** przywraca zaznaczone. Zaznaczone kopie są po prostu usuwane. Oryginalny projekt nigdy się nie zmienia.

Kolejność: **chwyć element w podglądzie myszą i przeciągnij go na miejsce innego elementu** — zielona ramka pokazuje, gdzie wyląduje; **oba elementy zamieniają się miejscami**, pozostałe zostają, a lista jest numerowana od nowa. Puszczenie poza elementami anuluje przeciąganie. Albo zaznacz element na liście i użyj **W górę / W dół**. Nowo zaznaczony element trafia na koniec. **Kolejność domyślna** przywraca kolejność z pliku. **Zaznacz wszystko / Odznacz wszystko** zmieniają zaznaczenie naraz.

**Obrót:** obrócony element ma na liście strzałkę i kąt (↻ zgodnie z ruchem wskazówek zegara, ↺ przeciwnie). Zaznacz element **klikając go w podglądzie** (pomarańczowa ramka) lub na liście; **Ctrl+klik** dodaje kolejne, **Esc** czyści zaznaczenie. Dla zaznaczonych elementów:

- **↺ 90° / ↻ 90°** — obrót o 90° (np. aby wszystkie breloki miały otwór u góry);
- **Kąt zaznaczonych** — wpisz dowolny kąt w stopniach (dodatni = zgodnie z ruchem wskazówek zegara);
- **Nie obracaj** — element zostaje jak w projekcie (kierunek tekstu, usłojenie materiału);
- **Auto** — usuwa kąt ręczny; aplikacja znów obraca element sama.

Kąt ręczny jest na liście oznaczony „(ręcznie)”; aplikacja nigdy go nie zmienia i obowiązuje również przy obrocie *Nie obracaj*. Kąt jest mierzony od położenia w oryginalnym projekcie. Otwarcie innego projektu usuwa kąty ręczne. Zobacz [siatkę](grid.md).

**Kopie (wypełnienie płyty):** zaznacz elementy i naciśnij **Ctrl+C** i **Ctrl+V** — zostanie dodana jedna kopia każdego. Więcej kopii naraz: ikona **Utwórz kopie** na pasku narzędzi (lub **Ctrl+D**, menu Edycja) i wpisz liczbę, np. 5. Kopie trafiają na koniec kolejności, są na liście oznaczone „(kopia G5)”, przejmują kąt ręczny i można je obracać i przesuwać jak inne elementy. Kopię usuniesz klawiszem **Delete** lub odznaczając ją. Kopie są zapisywane w zapisanym projekcie jako nowe grupy; oryginalny projekt się nie zmienia.

**Liczba sztuk** (pole obok *Kąta zaznaczonych*): ile sztuk zaznaczonego elementu rozmieścić — np. 5 = oryginał + 4 kopie tuż za nim (elementy pozostają pogrupowane według wariantów). Zmniejszenie usuwa najnowsze kopie, **0** pomija element. Gdy zaznaczona jest kopia, pole zmienia liczbę sztuk jej oryginału; lista pokazuje „×5” przy elemencie.

**Wypełnij płytę kopiami** (ikona płyty z elementami na pasku narzędzi, **Ctrl+Shift+D**, menu Edycja): dodaje tyle kopii zaznaczonych elementów, ile jeszcze zmieści się na płycie przy układzie przechodzącym kontrolę. Przy kilku zaznaczonych elementach kopie występują na przemian (A, B, A, B…). Najlepiej działa z *automatyczną* liczbą kolumn; przy stałej liczbie kolumn przybywają tylko wiersze.

Element numer **1** leży w rogu siatki wyznaczonym przez *Kolejność wypełniania* (zobacz [siatkę](grid.md)).

[← Przygotowanie](prepare.md) · [Dalej: siatka →](grid.md)

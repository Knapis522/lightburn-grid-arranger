# Siatka i umieszczenie

**Profil układu** — ustawienia zapisane pod nazwą (np. „Breloki 3 mm”): liczba kolumn (lub *Automatycznie*), odstępy, kolejność wypełniania, obrót i umieszczenie. Wybór profilu w sekcji **Profil układu** ustawia wartości; **Zapisz…** zapisuje bieżące ustawienia jako profil (ta sama nazwa = zastąpienie), **Usuń** go usuwa. Gdy zmienisz wartość, wybór przełącza się na *bez profilu* — sam profil się nie zmienia. Płyta nie jest częścią profilu; należy do lasera (Ustawienia → Lasery).

**Liczba kolumn** — ile elementów jest w jednym wierszu. Liczba wierszy jest obliczana. Z zaznaczonym **Automatycznie** aplikacja używa tylu kolumn, ile zmieści się na szerokości płyty (obszar użyteczny wewnątrz marginesów); pole pokazuje wtedy obliczoną liczbę. Przydatne razem z kopiami i *Wypełnij płytę kopiami*.

**Odstęp X / Y** — odległość między konturami cięcia sąsiednich elementów w wybranych jednostkach (poziomo / pionowo). Odstęp 0 jest dozwolony, ale aplikacja ostrzega o ryzyku przy cięciu. Liczby dziesiętne wpisuj tak, jak przyjęto w języku aplikacji (po polsku z przecinkiem).

Jeśli elementy mają **różne rozmiary**, kolumna jest tak szeroka jak jej najszerszy element, a wiersz tak wysoki jak najwyższy. Odstęp jest wtedy **minimalny** — między mniejszymi elementami jest większy.

**Kolejność wypełniania**

- *Od punktu zerowego lasera* (domyślnie) — element nr 1 leży w rogu przy punkcie zerowym lasera; przy punkcie zerowym po prawej wiersze są wypełniane od prawej do lewej; przy punkcie zerowym u dołu pierwszy wiersz jest na dole, a kolejne nad nim.
- *Kolejność czytania* — element nr 1 jest zawsze w lewym górnym rogu, wiersze od lewej do prawej.

**Umieszczenie**

- *W rogu płyty przy punkcie zerowym lasera* (domyślnie) — róg siatki przy punkcie zerowym leży w rogu płyty plus margines.
- *Na środku płyty*.
- *Ręcznie* — wpisz współrzędne X/Y LightBurn (odległość od punktu zerowego) rogu siatki przy punkcie zerowym.
- *W pierwotnym położeniu elementów*.

Pola **Róg X / Y** można edytować tylko w trybie *Ręcznie*. W pozostałych trybach są wyszarzone i pokazują róg, który aplikacja właśnie obliczyła (zmienia się np. z marginesami). Po przełączeniu na *Ręcznie* zachowują bieżący róg, więc siatka się nie przesuwa i można ją tylko dostroić.

Podgląd pokazuje płytę, obszar użyteczny (linia przerywana), punkt zerowy lasera (●), przesuwane elementy z prawdziwą grafiką i tekstami w kolorach warstw i z numerami oraz nieprzesuwane obiekty na szaro. Elementy z błędem są czerwone. **Pokaż grafikę** w nagłówku sekcji Elementy wyłącza rysunek i zostawia tylko prostokąty elementów. Kółko myszy (lub touchpad) płynnie przybliża, przeciąganie pustego miejsca przesuwa widok (przeciąganie elementu zmienia kolejność), ikona **Dopasuj widok** na pasku narzędzi (Ctrl+0) lub dwuklik w puste miejsce pokazuje wszystko.

## Obrót dla oszczędności materiału

Opcja **Obrót** w sekcji Siatka:

- *Dowolny kąt (najmniejsza powierzchnia)* — domyślnie. Każdy element jest obracany tak, aby otaczający go prostokąt był jak najmniejszy (oszczędza miejsce przy ukośnych lub nieregularnych kształtach, np. brelokach). Prostokątne karty pozostają proste.
- *Co 90°* — elementy są obracane tylko o ćwierć obrotu (poziomo / pionowo).
- *Nie obracaj* — elementy są tylko przesuwane.

We wszystkich trybach aplikacja dodatkowo sprawdza, czy siatka nie byłaby mniejsza, gdyby wszystkie elementy leżały poziomo lub pionowo, i wybiera mniejszy wariant — najlepiej taki, który mieści się na płycie. Jeśli obrót nie zmniejszyłby siatki, elementy zostają bez zmian; okrągłe elementy nigdy nie są obracane o 90°. Obrót jest widoczny w podglądzie i na liście elementów. Element obraca się wokół swojego środka razem z tekstami i grafiką; po zapisie sprawdź Preview w LightBurn. Wyjątki dla pojedynczych elementów: przycisk **Nie obracaj** w sekcji Elementy.

[← Elementy](items.md) · [Dalej: płyta i kontrola →](board.md)

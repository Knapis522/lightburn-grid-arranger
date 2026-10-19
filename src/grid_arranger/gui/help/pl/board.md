# Płyta, marginesy i kontrola kolizji

**Płyta** to prostokąt materiału we współrzędnych LightBurn. Domyślnie leży przy punkcie zerowym lasera (róg płyty X 0, Y 0). Jej rozmiar jest wstępnie wypełniany według lasera zapisanego w projekcie; **Zapisz jako domyślne dla tego lasera** zapamiętuje Twoje wartości. **Marginesy** (domyślnie 5 mm) to pas wzdłuż krawędzi płyty, w którym nic nie może zostać umieszczone.

> Płyta w aplikacji nie jest obszarem roboczym maszyny. Sprawdź rzeczywiste położenie materiału i ramkę na maszynie.

Przed zapisem aplikacja sprawdza, czy:

- wszystkie przesuwane elementy leżą w użytecznym obszarze płyty,
- elementy nie nachodzą na siebie i zachowują odstęp,
- elementy zachowują odstęp również od **nieprzesuwanych** grup i luźnych obiektów, jeśli pozostają w wyniku (Ustawienia → Zapisywanie); pominięte obiekty nie są brane pod uwagę,
- obiekt, którego rozmiaru nie da się określić, **blokuje** zapis (nie można potwierdzić bezpieczeństwa).

Błędy (✖) blokują zapis i wskazują dotknięte elementy. Ostrzeżenia (⚠) nie. Aplikacja nigdy sama nie skaluje, nie obraca ani nie przesuwa niezaznaczonych obiektów.

Kontrola pracuje na konturach w projekcie, a nie na rzeczywistym overscanie przy grawerowaniu, kompensacji szerokości cięcia czy ruchu głowicy — dlatego **Preview w LightBurn jest obowiązkowe**.

## Kilka płyt

Gdy elementy nie mieszczą się na jednej płycie, aplikacja dzieli je na kilka płyt. Sposób wybierasz w sekcji Płyta w polu **Gdy się nie mieści**:

- *Podziel na płyty po kolei* (domyślnie) — płyta 1 pełna, potem płyta 2 …; najmniej płyt.
- *Podziel na płyty równomiernie* — na każdej płycie tyle samo sztuk (np. 50 → 17/17/16).
- *Podziel na płyty według elementów* — na każdej płycie tylko sztuki jednego elementu (oryginał i jego kopie).
- *Nie dziel (błąd)* — jak dotąd: gdy układ się nie mieści, jest zablokowany.

**Uzupełnij ostatnią płytę kopiami** dodaje kopie, aż ostatnia płyta będzie pełna (przy *według elementów* ostatnia płyta każdego elementu jest uzupełniana kopiami tego elementu).

Nad podglądem karty pokazują płyty, jak strony w LightBurn; karta z błędem jest oznaczona ✖, a komunikaty podają płytę. Zapis jest możliwy tylko wtedy, gdy wszystkie płyty przejdą kontrolę. Wszystkie płyty mają te same ustawienia siatki i tę samą płytę; obiekty zostawione na miejscu (Ustawienia → Zapisywanie) są tylko na płycie 1.

Przy kilku płytach lista Elementy pokazuje sztuki wyświetlanej płyty (numerowane na niej), a pod nimi niezaznaczone i pominięte obiekty; automatycznie dodane kopie są szare. **Ctrl+A** zaznacza wszystkie elementy — przy kilku płytach tylko na wyświetlanej płycie.

**Zapis:** płyta 1 zostaje na rozmieszczanej stronie, a płyty 2 … są dodawane jako nowe strony zaraz za nią („Strona 1 – płyta 2“ …). W LightBurn przełączaj strony (**Window → Pages**) i wycinaj płyty po kolei — Preview i Frame działają tylko z aktywną stroną. Alternatywnie **Ustawienia → Płyty → Jako osobne pliki** zapisuje jeden plik na płytę (`…__plyta1.lbrn2` …). Wartości domyślne (sposób podziału, uzupełnianie, ostrzeżenie powyżej liczby płyt) są w **Ustawienia → Płyty**.

[← Siatka](grid.md) · [Dalej: zapis →](save.md)

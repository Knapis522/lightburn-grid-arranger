# Płyta, marginesy i kontrola kolizji

**Płyta** to prostokąt materiału we współrzędnych LightBurn. Domyślnie leży przy punkcie zerowym lasera (róg płyty X 0, Y 0). Jej rozmiar jest wstępnie wypełniany według lasera zapisanego w projekcie; **Zapisz jako domyślne dla tego lasera** zapamiętuje Twoje wartości. **Marginesy** (domyślnie 5 mm) to pas wzdłuż krawędzi płyty, w którym nic nie może zostać umieszczone.

> Płyta w aplikacji nie jest obszarem roboczym maszyny. Sprawdź rzeczywiste położenie materiału i ramkę na maszynie.

Przed zapisem aplikacja sprawdza, czy:

- wszystkie przesuwane elementy leżą w użytecznym obszarze płyty,
- elementy nie nachodzą na siebie i zachowują odstęp,
- elementy zachowują odstęp również od **nieprzesuwanych** grup i luźnych obiektów,
- obiekt, którego rozmiaru nie da się określić, **blokuje** zapis (nie można potwierdzić bezpieczeństwa).

Błędy (✖) blokują zapis i wskazują dotknięte elementy. Ostrzeżenia (⚠) nie. Aplikacja nigdy sama nie skaluje, nie obraca ani nie przesuwa niezaznaczonych obiektów.

Kontrola pracuje na konturach w projekcie, a nie na rzeczywistym overscanie przy grawerowaniu, kompensacji szerokości cięcia czy ruchu głowicy — dlatego **Preview w LightBurn jest obowiązkowe**.

[← Siatka](grid.md) · [Dalej: zapis →](save.md)

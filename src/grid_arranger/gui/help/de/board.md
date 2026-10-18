# Platte, Ränder und Kollisionsprüfung

Die **Platte** ist das Materialrechteck in LightBurn-Koordinaten. Standardmäßig liegt sie am Laser-Nullpunkt (Plattenecke X 0, Y 0). Ihre Größe wird nach dem im Projekt gespeicherten Laser vorausgefüllt; **Als Standard für diesen Laser speichern** merkt sich Ihre Werte. **Ränder** (Standard 5 mm) sind ein Streifen entlang der Plattenkanten, in dem nichts platziert werden darf.

> Die Platte in der Anwendung ist nicht der Arbeitsbereich der Maschine. Prüfen Sie die tatsächliche Materiallage und den Rahmen an der Maschine.

Vor dem Speichern prüft die Anwendung, dass:

- alle verschobenen Objekte innerhalb der nutzbaren Plattenfläche liegen,
- sich die Objekte nicht überlappen und den Abstand einhalten,
- die Objekte den Abstand auch zu **nicht verschobenen** Gruppen und losen Objekten einhalten,
- ein Objekt, dessen Größe nicht bestimmt werden kann, das Speichern **blockiert** (die Sicherheit lässt sich nicht bestätigen).

Fehler (✖) blockieren das Speichern und nennen die betroffenen Objekte. Warnungen (⚠) nicht. Die Anwendung skaliert, dreht oder verschiebt nicht ausgewählte Objekte nie von selbst.

Die Prüfung arbeitet mit den Konturen im Projekt, nicht mit dem tatsächlichen Overscan beim Gravieren, der Schnittbreitenkorrektur oder der Kopfbewegung — deshalb ist die **Preview in LightBurn Pflicht**.

[← Raster](grid.md) · [Weiter: Speichern →](save.md)

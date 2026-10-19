# Platte, Ränder und Kollisionsprüfung

Die **Platte** ist das Materialrechteck in LightBurn-Koordinaten. Standardmäßig liegt sie am Laser-Nullpunkt (Plattenecke X 0, Y 0). Ihre Größe wird nach dem im Projekt gespeicherten Laser vorausgefüllt; **Als Standard für diesen Laser speichern** merkt sich Ihre Werte. **Ränder** (Standard 5 mm) sind ein Streifen entlang der Plattenkanten, in dem nichts platziert werden darf.

> Die Platte in der Anwendung ist nicht der Arbeitsbereich der Maschine. Prüfen Sie die tatsächliche Materiallage und den Rahmen an der Maschine.

Vor dem Speichern prüft die Anwendung, dass:

- alle verschobenen Objekte innerhalb der nutzbaren Plattenfläche liegen,
- sich die Objekte nicht überlappen und den Abstand einhalten,
- die Objekte den Abstand auch zu **nicht verschobenen** Gruppen und losen Objekten einhalten, sofern diese in der Ausgabe bleiben (Einstellungen → Speichern); weggelassene Objekte werden ignoriert,
- ein Objekt, dessen Größe nicht bestimmt werden kann, das Speichern **blockiert** (die Sicherheit lässt sich nicht bestätigen).

Fehler (✖) blockieren das Speichern und nennen die betroffenen Objekte. Warnungen (⚠) nicht. Die Anwendung skaliert, dreht oder verschiebt nicht ausgewählte Objekte nie von selbst.

Die Prüfung arbeitet mit den Konturen im Projekt, nicht mit dem tatsächlichen Overscan beim Gravieren, der Schnittbreitenkorrektur oder der Kopfbewegung — deshalb ist die **Preview in LightBurn Pflicht**.

## Mehrere Platten

Passen die Teile nicht auf eine Platte, verteilt die Anwendung sie auf mehrere Platten. Wie, wählen Sie im Abschnitt Platte unter **Wenn es nicht passt**:

- *Nacheinander auf Platten aufteilen* (Standard) — Platte 1 voll, dann Platte 2 …; die wenigsten Platten.
- *Gleichmäßig auf Platten aufteilen* — auf jeder Platte gleich viele Teile (z. B. 50 → 17/17/16).
- *Nach Objekten auf Platten aufteilen* — jede Platte enthält nur Teile eines Objekts (Original und seine Kopien).
- *Nicht aufteilen (Fehler)* — wie bisher: passt das Layout nicht, ist es blockiert.

**Letzte Platte mit Kopien auffüllen** fügt Kopien hinzu, bis die letzte Platte voll ist (bei *nach Objekten* wird die letzte Platte jedes Objekts mit Kopien desselben Objekts aufgefüllt).

Über der Vorschau zeigen Registerkarten die Platten, wie Seiten in LightBurn; eine Registerkarte mit Fehler ist mit ✖ markiert, und die Meldungen nennen die Platte. Speichern ist nur möglich, wenn alle Platten die Prüfung bestehen. Alle Platten haben dieselben Rastereinstellungen und dieselbe Platte; an Ort und Stelle gelassene Objekte (Einstellungen → Speichern) sind nur auf Platte 1.

**Speichern:** Platte 1 bleibt auf der angeordneten Seite, Platten 2 … werden direkt danach als neue Seiten eingefügt („Seite 1 – Platte 2“ …). Wechseln Sie in LightBurn die Seite (**Window → Pages**) und schneiden Sie eine Platte nach der anderen — Preview und Frame arbeiten nur mit der aktiven Seite. Alternativ speichert **Einstellungen → Platten → Als separate Dateien** eine Datei pro Platte (`…__platte1.lbrn2` …). Die Standardwerte (Art der Aufteilung, Auffüllen, Warnung ab einer Anzahl Platten) finden Sie unter **Einstellungen → Platten**.

[← Raster](grid.md) · [Weiter: Speichern →](save.md)

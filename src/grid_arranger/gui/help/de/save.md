# Speichern und Prüfen in LightBurn

Das Symbol **Als neues Projekt speichern** in der Werkzeugleiste (oder **Datei → Als neues Projekt speichern**, Strg+S) ist nur aktiv, wenn das Layout die Prüfung bestanden hat. Ein Speicherdialog öffnet sich mit dem vorgeschlagenen Namen `original__grid_001.lbrn2` (dann `_002`, …) im Ordner des Originals — **Ordner und Name können Sie ändern**. Nach dem Bestätigen:

1. bereitet die Anwendung eine neue Datei vor, in der sich nur die Positionen der ausgewählten Gruppen (und ihrer Texte) ändern, weggelassene Objekte werden entfernt,
2. prüft sie unabhängig, dass sich nichts anderes geändert hat (Ebenen, Leistung, Texte, andere Objekte),
3. prüft sie, dass sich das Original seit dem Öffnen nicht geändert hat,
4. speichert sie eine **neue** Datei unter dem gewählten Namen.

**Speicherprotokoll** (`.json`) — eine Aufzeichnung, woraus und wie die Ausgabe entstanden ist: Prüfsummen, Laser, Rastereinstellungen, Objektverschiebungen und Prüfergebnis (keine Motive oder Texte der Objekte). Nützlich zur Nachverfolgung oder Fehlermeldung. **Einstellungen → Speichern → Speicherprotokoll**: *Nicht speichern* (Standard), *Neben dem gespeicherten Projekt* (`<Name>.json`) oder *Im Protokollordner der Anwendung* (dort mit **Protokollordner öffnen** öffnen).

**Nach dem Speichern arbeiten Sie mit dem Original weiter.** Die gespeicherte Datei ist eine eigene neue Kopie; das ursprüngliche Projekt bleibt in der Anwendung geöffnet, sodass Sie ein anderes Layout probieren und eine weitere Variante speichern können (`_002`, …). Titelleiste und Bereich Projekt zeigen *zuletzt gespeichert als …*. Um stattdessen mit der gespeicherten Datei weiterzumachen (wie „Speichern unter“), aktivieren Sie in der Speichermeldung **Hier mit der gespeicherten Datei weiterarbeiten** — sie wird anstelle des Originals geöffnet, ihre Kopien und Drehungen sind nun fest, und Rückgängig beginnt neu. Das nächste Speichern setzt dann die Nummerierung des Originals fort (`_002`, nicht `__grid_001__grid_001`).

Vorhandene Dateien und das Original werden nie überschrieben — existiert die gewählte Datei (oder ihr Protokoll daneben) bereits, fragt die Anwendung nach einem anderen Namen. Schlägt etwas fehl, entsteht keine Ausgabe.

**Dann in LightBurn:**

1. Öffnen Sie die Ausgabe: in der Speichermeldung mit **In LightBurn öffnen** (oder Werkzeugleistensymbol, **Datei → Gespeichertes Projekt in LightBurn öffnen**, Strg+L). Die Anwendung öffnet die Datei wie ein Doppelklick im Explorer: Ein laufendes LightBurn ersetzt sein geöffnetes Projekt — bei ungespeicherten Änderungen fragt LightBurn selbst; sonst startet LightBurn. Manuell öffnen Sie über **File → Open** (nicht Import — Import lädt die Projekteinstellungen nicht).
2. Prüfen Sie Ebenen, Leistung und Geschwindigkeit.
3. Starten Sie die **Preview** und prüfen Sie die Bahnen.
4. Prüfen Sie die Position an der Maschine (**Frame**). Erst dann schneiden, unter Aufsicht.

**Ungespeicherte Änderungen:** Wenn sich das Layout seit dem Öffnen oder dem letzten Speichern geändert hat, zeigt die Titelleiste ein Sternchen nach dem Projektnamen (`karty.lbrn2*`). Beim Schließen der Anwendung, beim Öffnen eines anderen Projekts oder beim Installieren eines Updates fragt die Anwendung, ob das Layout als neues Projekt gespeichert, verworfen oder die Aktion abgebrochen werden soll. Hat das Layout die Prüfung nicht bestanden, bietet sie nur Verwerfen oder Abbrechen an.

[← Platte](board.md) · [Problemlösung →](troubleshooting.md)

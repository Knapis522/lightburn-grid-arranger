# Raster und Platzierung

**Layoutprofil** — unter einem Namen gespeicherte Einstellungen (z. B. „Schlüsselanhänger 3 mm“): Spaltenanzahl (oder *Automatisch*), Abstände, Füllreihenfolge, Drehung und Platzierung. Die Auswahl eines Profils im Bereich **Layoutprofil** setzt die Werte; **Speichern…** speichert die aktuellen Einstellungen als Profil (gleicher Name = überschreiben), **Löschen** entfernt es. Wenn Sie einen Wert ändern, wechselt die Auswahl zu *kein Profil* — das Profil selbst bleibt unverändert. Die Platte ist nicht Teil eines Profils; sie gehört zum Laser (Einstellungen → Laser).

**Spalten** — wie viele Objekte in einer Zeile liegen. Die Zeilenanzahl wird berechnet. Mit angehaktem **Automatisch** verwendet die Anwendung so viele Spalten, wie auf die Plattenbreite passen (die nutzbare Fläche innerhalb der Ränder); das Feld zeigt dann die berechnete Anzahl. Nützlich zusammen mit Kopien und *Platte mit Kopien füllen*.

**Abstand X / Y** — Abstand zwischen den Schneidkonturen benachbarter Objekte in den gewählten Einheiten (waagerecht / senkrecht). Abstand 0 ist erlaubt, die Anwendung warnt aber vor dem Risiko beim Schneiden. Dezimalzahlen geben Sie wie in der Sprache der Anwendung üblich ein (auf Deutsch mit Komma).

Haben die Objekte **unterschiedliche Größen**, ist eine Spalte so breit wie ihr breitestes Objekt und eine Zeile so hoch wie ihr höchstes. Der Abstand ist dann ein **Mindestabstand** — zwischen kleineren Objekten ist er größer.

**Füllreihenfolge**

- *Ab dem Laser-Nullpunkt* (Standard) — Objekt Nr. 1 liegt in der Ecke am Laser-Nullpunkt; bei Nullpunkt rechts werden die Zeilen von rechts nach links gefüllt; bei Nullpunkt unten liegt die erste Zeile unten und die nächsten darüber.
- *Lesereihenfolge* — Objekt Nr. 1 liegt immer oben links, Zeilen von links nach rechts.

**Platzierung**

- *In der Plattenecke am Laser-Nullpunkt* (Standard) — die Rasterecke am Nullpunkt liegt in der Plattenecke plus Rand.
- *In der Plattenmitte*.
- *Manuell* — geben Sie die LightBurn-X/Y-Koordinaten (Abstand vom Nullpunkt) der Rasterecke am Nullpunkt ein.
- *An der ursprünglichen Position der Objekte*.

Die Felder **Ecke X / Y** lassen sich nur im Modus *Manuell* bearbeiten. In den anderen Modi sind sie ausgegraut und zeigen die Ecke, die die Anwendung gerade berechnet hat (sie ändert sich z. B. mit den Rändern). Nach dem Umschalten auf *Manuell* behalten sie die aktuelle Ecke, sodass sich das Raster nicht verschiebt und Sie es feinjustieren können.

Die Vorschau zeigt die Platte, die nutzbare Fläche (gestrichelt), den Laser-Nullpunkt (●), die verschobenen Objekte mit ihren echten Motiven und Texten in Ebenenfarben und mit ihren Nummern sowie nicht verschobene Objekte in Grau. Objekte mit Fehler sind rot. **Motive anzeigen** im Kopf des Bereichs Objekte schaltet die Zeichnung aus und lässt nur die Objektrechtecke. Das Mausrad (oder Touchpad) zoomt stufenlos, Ziehen auf leerer Fläche verschiebt die Ansicht (Ziehen eines Objekts ändert die Reihenfolge), das Symbol **Ansicht einpassen** in der Werkzeugleiste (Strg+0) oder ein Doppelklick auf leere Fläche zeigt alles.

## Drehung zur Materialeinsparung

Die Option **Drehung** im Bereich Raster:

- *Beliebiger Winkel (kleinste Fläche)* — Standard. Jedes Objekt wird so gedreht, dass das Rechteck um es möglichst klein ist (spart Platz bei schrägen oder unregelmäßigen Formen wie Schlüsselanhängern). Rechteckige Karten bleiben gerade.
- *In 90°-Schritten* — Objekte werden nur um eine Vierteldrehung gedreht (quer / hoch).
- *Nicht drehen* — Objekte werden nur verschoben.

In allen Modi prüft die Anwendung zusätzlich, ob das Raster kleiner wäre, wenn alle Objekte quer oder hoch lägen, und verwendet die kleinere Variante — bevorzugt eine, die auf die Platte passt. Würde die Drehung das Raster nicht verkleinern, bleiben die Objekte, wie sie sind; runde Objekte werden nie um 90° gedreht. Die Drehung ist in der Vorschau und in der Objektliste zu sehen. Ein Objekt wird um seinen Mittelpunkt samt Texten und Motiven gedreht; prüfen Sie nach dem Speichern die Preview in LightBurn. Ausnahmen für einzelne Objekte: die Schaltfläche **Nicht drehen** im Bereich Objekte.

[← Objekte](items.md) · [Weiter: Platte und Prüfung →](board.md)

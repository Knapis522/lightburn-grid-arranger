# Objekte auswählen und anordnen

Nach dem Öffnen eines Projekts (Symbol **Projekt öffnen** in der Werkzeugleiste, **Datei → Projekt öffnen** oder Strg+O) zeigt die Liste alle Gruppen der obersten Ebene:

- **Angehakte** Objekte werden im Raster angeordnet. Die Zahl vor dem Namen ist ihre Position im Raster.
- **Nicht angehakte** Objekte werden nicht in die Ausgabe geschrieben: Sie sind nicht im gespeicherten Projekt und das Raster berücksichtigt sie nicht. Wenn sie stattdessen an Ort und Stelle bleiben sollen, wählen Sie **Einstellungen → Speichern → Nicht angehakte Objekte → An Ort und Stelle lassen** — das Raster weicht ihnen dann aus.
- **Graue** Objekte („kann nicht verschoben werden“) wurden abgelehnt — fahren Sie mit der Maus darüber, um den Grund zu sehen. Sie werden nie verschoben.
- ⚠ kennzeichnet eine Warnung (z. B. einen Text, der nicht vermessen werden kann) — das Objekt kann verwendet werden, prüfen Sie es aber in der Vorschau.
- **Objekte weglassen:** Objekte in der Liste auswählen (auch graue) und **Entf** drücken (oder **Bearbeiten → Aus der Ausgabe weglassen** bzw. Rechtsklick). Sie wandern durchgestrichen ans Ende der Liste und sind nicht im gespeicherten Projekt — praktisch, wenn Sie aus einem großen Projekt nur einen Teil brauchen. **Bearbeiten → Weggelassene Objekte wiederherstellen** holt die ausgewählten zurück. Ausgewählte Kopien werden einfach entfernt. Das ursprüngliche Projekt ändert sich nie.

Reihenfolge: **Greifen Sie ein Objekt in der Vorschau mit der Maus und ziehen Sie es auf die Stelle eines anderen Objekts** — ein grüner Rahmen zeigt, wo es landet; **die beiden Objekte tauschen die Plätze**, alle anderen bleiben, und die Liste wird neu nummeriert. Loslassen außerhalb der Objekte bricht das Ziehen ab. Oder wählen Sie ein Objekt in der Liste und nutzen Sie **Nach oben / Nach unten**. Ein neu angehaktes Objekt kommt ans Ende. **Standardreihenfolge** stellt die Reihenfolge aus der Datei wieder her. **Alle auswählen / Keine auswählen** ändern die Auswahl auf einmal.

**Drehung:** Ein gedrehtes Objekt zeigt in der Liste einen Pfeil und den Winkel (↻ im Uhrzeigersinn, ↺ gegen den Uhrzeigersinn). Wählen Sie ein Objekt durch **Klicken in der Vorschau** (orangefarbener Rahmen) oder in der Liste; **Strg+Klick** fügt weitere hinzu, **Esc** hebt die Auswahl auf. Für die ausgewählten Objekte:

- **↺ 90° / ↻ 90°** — um 90° drehen (z. B. damit alle Schlüsselanhänger das Loch oben haben);
- **Winkel der Auswahl** — beliebigen Winkel in Grad eingeben (positiv = im Uhrzeigersinn);
- **Nicht drehen** — das Objekt bleibt wie im Projekt (Textrichtung, Materialmaserung);
- **Auto** — entfernt den manuellen Winkel; die Anwendung dreht das Objekt wieder selbst.

Ein manueller Winkel ist in der Liste mit „(manuell)“ gekennzeichnet; die Anwendung ändert ihn nie, und er gilt auch bei Drehung *Nicht drehen*. Der Winkel wird von der Lage im ursprünglichen Projekt aus gemessen. Das Öffnen eines anderen Projekts löscht manuelle Winkel. Siehe [Raster](grid.md).

**Kopien (Platte füllen):** Objekte auswählen und **Strg+C** und **Strg+V** drücken — von jedem wird eine Kopie hinzugefügt. Für mehrere Kopien auf einmal das Symbol **Kopien erstellen** in der Werkzeugleiste (oder **Strg+D**, Menü Bearbeiten) verwenden und die Anzahl eingeben, z. B. 5. Kopien kommen ans Ende der Reihenfolge, sind in der Liste mit „(Kopie von G5)“ gekennzeichnet, übernehmen den manuellen Winkel und lassen sich wie jedes andere Objekt drehen und verschieben. Eine Kopie entfernen Sie mit **Entf** oder durch Abhaken. Kopien werden als neue Gruppen in das gespeicherte Projekt geschrieben; das ursprüngliche Projekt wird nicht verändert.

**Stückzahl** (Feld neben *Winkel der Auswahl*): wie viele Stück des ausgewählten Objekts platziert werden — z. B. 5 = das Original + 4 Kopien direkt dahinter (die Objekte bleiben nach Varianten gruppiert). Verringern entfernt die neuesten Kopien, **0** lässt das Objekt weg. Ist eine Kopie ausgewählt, ändert das Feld die Stückzahl ihres Originals; die Liste zeigt „×5“ neben dem Objekt.

**Platte mit Kopien füllen** (Plattensymbol in der Werkzeugleiste, **Strg+Umschalt+D**, Menü Bearbeiten): fügt so viele Kopien der ausgewählten Objekte hinzu, wie noch auf die Platte passen, sodass das Layout die Prüfung besteht. Bei mehreren ausgewählten Objekten wechseln sich die Kopien ab (A, B, A, B…). Funktioniert am besten mit der *automatischen* Spaltenanzahl; bei fester Spaltenanzahl kommen nur Zeilen hinzu.

Objekt Nummer **1** liegt in der Rasterecke, die die *Füllreihenfolge* bestimmt (siehe [Raster](grid.md)).

[← Vorbereitung](prepare.md) · [Weiter: Raster →](grid.md)

# Problemlösung

**„Diese Anwendung unterstützt nur .lbrn2-Projekte“** — speichern Sie das Projekt in LightBurn als `.lbrn2`.

**„Nicht unterstützte LightBurn-Version“** — das Projekt wurde mit einer LightBurn-Version gespeichert, mit der die Anwendung nicht überprüft wurde. Die Ausgabe wäre möglicherweise nicht sicher, daher wird sie abgelehnt.

**Objekt „kann nicht verschoben werden“** — fahren Sie mit der Maus darüber. Meistens: Die Gruppe hat keine geschlossene Schneidkontur, etwas ragt über die Kontur hinaus, sie ist gesperrt, oder sie enthält einen Objekttyp, den die Anwendung noch nicht sicher verschieben kann (z. B. eine Bitmap).

**„Die Textgeometrie stimmt nicht mit ihrer Position überein“** — öffnen Sie das Projekt in LightBurn und speichern Sie es erneut.

**Speichern ist blockiert** — lesen Sie die Fehler (✖) unter der Vorschau: Überschreitung der Platte, Kollision, zu kleiner Abstand oder ein Objekt, das nicht vermessen werden kann. Ändern Sie Spalten, Abstände, Platte oder Auswahl.

**„Die Originaldatei wurde seit dem Öffnen geändert“** — das Projekt wurde zwischenzeitlich erneut gespeichert. Öffnen Sie es in der Anwendung neu.

**Windows meldet „Der Computer wurde durch Windows geschützt“** — die Anwendung ist noch nicht digital signiert. Wenn das Installationsprogramm aus den Versionen dieses Projekts auf GitHub stammt, klicken Sie auf **Weitere Informationen → Trotzdem ausführen**. Deaktivieren Sie Ihren Virenschutz nicht.

**Die Anwendung startet nicht oder meldet eine fehlende Datei** — höchstwahrscheinlich fehlt der Ordner `_internal` neben `GridArranger.exe` (z. B. wurde nur die EXE kopiert). Entpacken Sie das ganze ZIP erneut. Zur Prüfung der Installation führen Sie `GridArranger.exe --self-test report.json` in der Eingabeaufforderung aus; das Ergebnis steht in `report.json`.

**Ein Problem melden** — aktivieren Sie Einstellungen → Speichern → Speicherprotokoll, speichern Sie erneut und senden Sie das `.json`-Protokoll (es enthält Prüfsummen und Parameter, nicht die Objektinhalte) und die Schritte. Kundenprojekte nur mit Erlaubnis senden.

[← Einführung](index.md)

# Projekt in LightBurn vorbereiten

1. **Gruppieren Sie jedes Objekt einzeln** (Strg+G). Eine Gruppe = ein Objekt.
2. Jede Gruppe braucht eine **geschlossene Schneidkontur**, die alles andere enthält (Texte, Motive). Die Kontur darf abgerundete Ecken oder eine andere Form haben — die Objektgröße ist das Rechteck um die Kontur. Die Kontur kann eine Kurve oder eine direkt in LightBurn gezeichnete Form sein (Kreis, Ellipse, Rechteck, Vieleck); eine Gruppe darf weitere Gruppen enthalten (z. B. ein Schlüsselanhänger: Kreis mit Loch + Text).
3. Speichern Sie das Projekt (**Save As**) als `.lbrn2`. Die Anwendung liest nur die gespeicherte Datei — ungespeicherte Änderungen in LightBurn sieht sie nicht.
4. Speichern Sie das Projekt für den Laser, auf dem Sie schneiden werden. Die Anwendung erkennt den Laser und seinen Nullpunkt (oben links, oben rechts, unten links oder unten rechts — z. B. Diodenlaser) aus dem Projekt. **Nach einem Laserwechsel in LightBurn das Projekt erneut speichern** und neu öffnen.

Unterstützt: LightBurn 2.2, `.lbrn2`-Projekte, Laser mit dem Nullpunkt in jeder Ecke. Alte `.lbrn`-Dateien werden abgelehnt — speichern Sie das Projekt in LightBurn als `.lbrn2`.

## Projekt für einen anderen Laser

Ein für einen Laser gespeichertes Projekt lässt sich für einen anderen vorbereiten, z. B. von einem Laser mit Nullpunkt oben rechts für einen Laser mit Nullpunkt oben links — ohne Gerätewechsel und Spiegeln des Designs in LightBurn. Wählen Sie im Bereich **Projekt** unter **Vorbereiten für:** einen Laser aus dem Katalog. Die Anwendung bietet seine Platte an, füllt das Raster ab seinem Nullpunkt, und die gespeicherte Datei (`…__Lasername__grid_001.lbrn2`) ist direkt für ihn bestimmt: Die Datei nennt den Ziellaser, und die Objekte sind so gespiegelt, dass sie auf ihm gleich aussehen (Texte lesbar).

- Laserkatalog: **Einstellungen → Laser** (oder *Laser verwalten…* in der Liste). Laser aus geöffneten Projekten werden automatisch hinzugefügt; weitere (z. B. einen Diodenlaser) fügen Sie manuell hinzu — **der Name muss dem Gerät in LightBurn entsprechen**; wählen Sie die Nullpunkt-Ecke und die Platte.
- Bei einem anderen Nullpunkt müssen **alle Objekte** ausgewählt sein, und das Projekt darf keine anderen Objekte enthalten (sie blieben auf dem anderen Laser gespiegelt). Das betrifft nur Objekte, die in der Ausgabe bleiben — nicht angehakte und weggelassene Objekte sind nicht in der Ausgabe (Standard) und stören daher nicht.
- **Ebeneneinstellungen (Leistung, Geschwindigkeit) werden nicht umgerechnet** — sie bleiben wie im ursprünglichen Projekt. Öffnen Sie die Ausgabe in LightBurn mit dem Ziellaser und prüfen Sie die Ebenen.

[← Einführung](index.md) · [Weiter: Objekte →](items.md)

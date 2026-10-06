# ManuCreator-Editor integrationsbereit machen (für die Zusammenführung mit der Website)

Der Editor wird so umgebaut, dass er seine Produkt-, Preis-, Schrift- und Gravurbereich-Daten von außen übernehmen kann, statt sie fest im Code zu haben.
So nutzt er nach dem Zusammenführen in den Website-Job automatisch die Daten aus der Verwaltung.

## Für wen

Für dich als Betreiber: Du willst, dass der Editor wieder Teil der ManuCreator-Website wird und dort die in der Verwaltung gepflegten Produkte, Preise und Vorgaben anzeigt – nicht mehr die fest eingebauten Beispielwerte.

## Ausgangslage (warum der Editor aktuell keine Verwaltungsdaten nutzt)

Dieser Editor ist ein eigenständiges Projekt. Es wurde komplett neu aus Bildvorlagen gebaut und war nie mit dem Website-/Verwaltungs-Projekt (Job 3da14c59-…) verbunden. Deshalb sind hier alle Daten fest hinterlegt:

- Produkt „Holzscheibe · Birkenholz · Ø 22 cm" und Preis „24,90 €"
- Liste der Schriftarten, Grundformen und Motive
- Form und Größe des Gravurbereichs (fester Kreis)

Von diesem Projekt aus gibt es keinen Zugriff auf den anderen Job oder dessen Datenbank. Eine echte Zusammenführung passiert im anderen Job (per „Save to GitHub" und anschließendem Übernehmen dort). Dieser Plan sorgt dafür, dass der Editor dafür vorbereitet ist.

## Was gebaut wird (Kernidee)

Der Editor bekommt eine klare, dokumentierte „Daten-Eingangsstelle". Die Website/Verwaltung übergibt beim Einbinden ein einziges Daten-Paket, und der Editor richtet sich komplett danach:

- **Produkt**: Name, Material, Maße, Produktbild
- **Gravurbereich**: Form und Größe der bedruckbaren Fläche je Produkt (statt immer fester Kreis)
- **Preis**: Anzeige aus den Vorgaben
- **Schriften, Motive, Vorlagen**: nur die, die in der Verwaltung freigegeben sind

Werden keine Daten übergeben (z. B. beim isolierten Testen in diesem Job), zeigt der Editor weiterhin die bisherigen Beispielwerte. So funktioniert er allein und im Website-Verbund.

## Ablauf

1. Website/Verwaltung übergibt dem Editor beim Laden das Daten-Paket des gewählten Produkts.
2. Der Editor zeigt Produktleiste, Produktdetails und Preis anhand dieser Daten.
3. Der Gravurbereich (Form/Größe der bedruckbaren Fläche) richtet sich nach dem Produkt; Beschneidung, Hilfslinien und Snap passen sich automatisch an.
4. In den Werkzeugen stehen nur die freigegebenen Schriften, Motive und Vorlagen zur Auswahl.
5. Das fertige Design lässt sich wie bisher in der Vorschau ansehen und als SVG herunterladen; der Gravurbereich des jeweiligen Produkts wird dabei berücksichtigt.

## Aussehen und Bedienung

Unverändert gegenüber heute: gleiches olivgrün/cremefarbenes Erscheinungsbild, gleiche mobile-first Bedienung, gleiche Werkzeuge. Es ändert sich nur die Herkunft der Inhalte (aus den übergebenen Daten statt fest im Code). Für einen Nutzer ist kein Unterschied sichtbar, außer dass jetzt das echte Produkt, der echte Preis und der korrekte Gravurbereich erscheinen.

## Umsetzungsphasen

**Phase 1 – MVP (wird jetzt gebaut):**
- Zentrale Daten-Eingangsstelle im Editor mit sauberen Beispiel-/Standardwerten als Rückfallebene.
- Produktname, Material, Maße, Produktbild und Preis kommen aus den übergebenen Daten.
- Gravurbereich (Form + Größe) wird datengetrieben; Beschneidung, Smart Guides und Snap-Raster passen sich an.
- Schriften-, Motiv- und Vorlagenliste aus den übergebenen Daten (mit heutigen Werten als Standard).
- Kurze Dokumentation des erwarteten Daten-Pakets, damit der Agent im Website-Job es einfach befüllen kann.

**Phase 2 (später):**
- Nachladen der Produktdaten direkt über eine Schnittstelle der Website/Verwaltung (API-Anbindung), inkl. Produktauswahl.
- Mehrere Produktformen über den Kreis hinaus (z. B. rechteckige oder ovale Gravurflächen).

**Phase 3 (später):**
- Speichern des fertigen Designs beim jeweiligen Produkt/Bestellvorgang und Übergabe an Warenkorb/Checkout der Website.
- Druckfertiger Export mit eingebetteten Schriften.

## Annahmen

- Die eigentliche Zusammenführung erfolgt im Website-Job (Job 3da14c59-…) über „Save to GitHub" und anschließendes Übernehmen dort; dieser Plan macht den Editor nur dafür bereit.
- Von diesem Projekt aus besteht kein Zugriff auf den anderen Job oder dessen Datenbank; es wird hier keine Verbindung zum anderen Job hergestellt.
- Solange keine externen Daten übergeben werden, bleiben die heutigen Beispielwerte (Holzscheibe, 24,90 €, kreisförmiger Gravurbereich) als Standard sichtbar.
- Der bestehende Funktionsumfang und das Design des Editors bleiben erhalten; es wird nichts entfernt.
- Es werden keine neuen Pflicht-Zugangsdaten oder Konten eingeführt.

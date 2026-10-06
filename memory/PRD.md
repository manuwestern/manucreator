# ManuCreator – sichtbare Arbeitsfläche und bedienbarer Bogen-Regler

## Originalauftrag
„In Bild 1 erkennt man dass das Objekt kaum sichtbar ist, es wird zu viel verdeckt. Das betrifft auch die anderen Bereiche. Halte dich an das Mockup in Bild 2. außerdem ist der slider für den Bogen teilweise zu klein bzw. der Knopf lässt sich nicht gut packen bzw swipen“

Bestätigte Entscheidung: „Ja, die Arbeitsfläche passend verkleinern; Preis und Hauptnavigation dürfen während der Bearbeitung ausgeblendet werden (empfohlen).“

## Ausgangslage und Architektur
- Repository enthielt ausschließlich das unveränderte React/FastAPI/MongoDB-Grundgerüst. Kein ursprünglicher Editor vorhanden. Nutzer darüber informiert; Editor anhand seiner beiden Bildvorlagen umgesetzt.
- Frontend: React 19, vorhandene Radix/shadcn-Komponenten für Dialog/Slider, Lucide, Sonner. Keine zusätzlichen Abhängigkeiten.
- Komponenten unter `frontend/src/components/editor/`; Zustand/History/Speicherung in `hooks/useEditor.js`.
- SVG-Arbeitsfläche mit realem Holzfoto, auswählbaren/verschiebbaren Texten und Motiven, textPath für Wölbung. ResizeObserver passt SVG an tatsächlich verfügbaren Platz an.
- Mobile bis 760px: Header, Produktleiste, flexibler Canvas und Werkzeugfeld im normalen Layoutfluss; keine überlagernden Bottom-Sheets. Werkzeugfeld begrenzt und intern scrollbar. Während Bearbeitung Navigation/Preis ausgeblendet.
- Desktop: linke Werkzeugnavigation, mittlere Arbeitsfläche, rechter Inspektor, Fußleiste.
- Lokale Speicherung unter `manucreator-design-v1`. Keine Anmeldung und keine neuen Backend-Endpunkte; bestehendes Backend unverändert. Kein Checkout angebunden (UI zeigt vorhandene Beispielpreis-/Testmodus-Kennzeichnung aus Referenz).
- Holzfoto lokal unter `public/images/wood-slice.webp`, Quelle Unsplash photo-1587132117816-061b35073a4e. Schriftarten DM Sans, Cormorant Garamond und Italianno.

## Implementiert
- Referenznaher olivgrüner/cremefarbener Editor mit deutscher Oberfläche.
- Vollständig sichtbare Holzscheibe in Wölbung, Objektaktionen, Ebenen und weiteren Werkzeugen; dynamische Verkleinerung statt Verdeckung.
- Bogen -180° bis +180°, positiver/negativer/gerader Modus, Zurücksetzen, Plus/Minus in 5°-Schritten, Tastatur in 1°-Schritten.
- Sichtbarer Griff 29px, echte Grifffläche 44x44px, 48px hohes Sliderfeld. Pointer Capture und touch-action:none; eigene Fingerpositionszuordnung berücksichtigt 22px halbe Griffbreite. Ganze Wischgeste ergibt einen Undo-Schritt.
- Texte bearbeiten/Schriftart ändern, duplizieren, löschen mit Wiederherstellung, sperren/entsperren, direkt verschieben und über Griffe skalieren/drehen.
- Ebenen sortieren (Buttons, Desktop Drag & Drop), auswählen, Sichtbarkeit umschalten, sperren.
- Herz-/Zweigmotive, drei Vorlagen, lokale Bilduploads PNG/JPG/WebP bis 2MB.
- Rückgängig/Wiederholen, lokales Autosave, Produktdetails/Hilfe, erweiterte Arbeitsfläche, Vorschau ohne Auswahlrahmen und SVG-Download.

## Verifikation
- Frontend-Testagent: `/app/test_reports/iteration_1.json`; alle Kernabläufe bestanden bis auf Touch-Endpunktpräzision, danach korrigiert.
- Hauptagent-Nachprüfung mit echten CDP-Touch-Ereignissen, mobile Iframes 390x844, 375x667, 320x568: exakte Endpunkte -180/+180, Undo/Redo der kompletten Wischgeste, Tastaturschritt +180→+179, vollständig sichtbarer Canvas, kein horizontaler Overflow bestanden.
- Ergänzendes Ergebnis: `/app/test_reports/slider_regression.json`.
- `yarn build` nach Sliderkorrektur erfolgreich ohne Fehler/Warnungen.
- Öffentliche Vorschau: Wert von `frontend/.env` REACT_APP_BACKEND_URL. Es werden für diesen UI-Auftrag keine API-Aufrufe benötigt.
- Keine Zugangsdaten erstellt oder erforderlich.

## Priorisierter Backlog / nächste mögliche Schritte
- P0: keine offenen Fehler im angefragten Umfang.
- P1: Optional Zwei-Finger-Zoom/Pan mit einfacher Zurück-auf-Gesamtansicht-Funktion.
- P2: Original-Produktdaten und -Bilder anbinden, falls bereitgestellt; optional kontobasiertes Speichern und druckfertiger Export mit eingebetteten Schriftarten.
- Kein zusätzlicher Funktionsumfang ohne neuen Nutzerauftrag begonnen.

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
- Lokale Speicherung unter `manucreator-design-v1`; hochgeladene Originalbilder separat als Blobs in IndexedDB `manucreator-assets` / `images`. Keine Anmeldung und keine neuen Backend-Endpunkte; bestehendes Backend unverändert. Kein Checkout angebunden (UI zeigt vorhandene Beispielpreis-/Testmodus-Kennzeichnung aus Referenz).
- Holzfoto lokal unter `public/images/wood-slice.webp`, Quelle Unsplash photo-1587132117816-061b35073a4e. Schriftarten DM Sans, Cormorant Garamond und Italianno.

## Implementiert
- Referenznaher olivgrüner/cremefarbener Editor mit deutscher Oberfläche.
- Vollständig sichtbare Holzscheibe in Wölbung, Objektaktionen, Ebenen und weiteren Werkzeugen; dynamische Verkleinerung statt Verdeckung.
- Bogen -180° bis +180°, positiver/negativer/gerader Modus, Zurücksetzen, Plus/Minus in 5°-Schritten, Tastatur in 1°-Schritten.
- Sichtbarer Griff 29px, echte Grifffläche 44x44px, 48px hohes Sliderfeld. Pointer Capture und touch-action:none; eigene Fingerpositionszuordnung berücksichtigt 22px halbe Griffbreite. Ganze Wischgeste ergibt einen Undo-Schritt.
- Texte bearbeiten/Schriftart ändern, duplizieren, löschen mit Wiederherstellung, sperren/entsperren, direkt verschieben und über Griffe skalieren/drehen.
- Ebenen sortieren (Buttons, Desktop Drag & Drop), auswählen, Sichtbarkeit umschalten, sperren.
- Herz-/Zweigmotive, fünf Grundformen, drei Vorlagen, lokale Bilduploads PNG/JPG/WebP bis 10MB.
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

## Folgeauftrag: Schriften, Formen und Bearbeitungsparameter
Nutzer: „Also zum einen fehlen natürlich jetzt wieder die Schriften. Am besten also diese Google-Standardschriften, wo man aber auch direkt bei der Auswahl des Schrifts vielleicht die Schrift sehen kann, weil anhand des Namens alleine weiß man ja nicht, wie die Schrift dann aussieht. Dann fehlen aber noch wieder die Standardelemente wie Linie, ähm, Kreis, ähm, Rechteck, Stern, keine Ahnung was. Wichtig ist, dass man die Objekte auch vernünftig bearbeiten kann. Wenn die Linie relativ dünn ist, ähm, muss man die trotzdem auch mit dem Finger gut selektieren können. Und natürlich die Standardparameter dazu: Strichstärke. Dann auch bei dem Text hatten wir ja so was von nur Umriss war, das fehlt auch. Ähm, aber es muss halt gemäß dem bestehenden, bestehenden optischen Konzept und Bedienoberfläche integriert sein und se-sehr gut nutzbar und leicht zu bedienbar vom Smartphone sein“

Bestätigt: Google-Schriften mit Vorschau; Linie, Kreis, Rechteck, Dreieck, Stern; Strichstärke, Füllung/Umriss, Größe, Drehung; Umrisstext; großzügige unsichtbare Touchflächen.

Zusatzauftrag während Umsetzung: „Also man kann Objekte soll man auch beliebig groß ziehen können. Wenn sie halt außerhalb des Gravurbereiches wird halt der Bereich außerhalb abgeschnitten beziehungsweise nicht angezeigt. Ähm, dann soll man so Orientierungslinien haben, wenn man das Objekt zum Beispiel verschiebt, dass das dann angezeigt wird an den Linien. Okay, jetzt bin ich in der Mitte horizontal oder vertikal. Ebenso Hilfslinien, die einem helfen, Objekte, ähm, füreinander aus, gegeneinander auszurichten. Ähm, oder so 'ne Art Snap Grid, was man ein- und ausschalten kann. Und ja, die Bildgrößenbegrenzung beim Upload soll erhöht werden auf zehn Megabyte.“

### Umgesetzt
- Bestehende Gestaltung erhalten. „Elemente“ ersetzt Navigationsbezeichnung „Motive“; Unterteilung Grundformen/Naturmotive.
- 14 tatsächlich geladene Google Fonts plus bestehende Georgia. Vorschaukarten zeigen den eigenen Text; Suche und Kategorien Alle/Klar/Klassisch/Handschrift. Auswahl direkt auf Holz sichtbar.
- Text → Schriftart öffnet Schriftkarten. Text → Stil & Größe öffnet Gefüllt/Nur Umriss, Umrissstärke, Größe und Drehung. Wölbung bleibt kombinierbar. Schriftbreiten werden gemessen, damit keine Endbuchstaben verloren gehen.
- Linie/Kreis/Rechteck/Dreieck/Stern mit passenden Layer-Symbolen, Duplikation, Sperren, Löschen, Undo/Redo und Persistenz.
- Strichstärke 0,2–6mm; Breite/Länge/Durchmesser/Höhe, Proportionensperre, Drehung. Größe auch direkt numerisch eingebbar. Keine künstliche Obergrenze mehr bei Ziehen, Größenangaben oder Plus-Steuerung; Sliderbereich wächst mit. Mindestgröße nur zur Vermeidung degenerierter Geometrie.
- Mindestens 44 CSS-Pixel Hit-Fläche für dünne/kleine Objekte, unabhängig von Canvas-Skalierung. Greifflächen der Skalierungs-/Drehgriffe ebenso 44px. Kleine Auswahlrahmen halten Griffe auseinander. Pointer Capture auf stabiler SVG-Wurzel.
- Alle tatsächlichen Gravur-Elemente in SVG-Clip-Gruppe; kreisförmiger Gravurbereich in `alignment.js` (cx=300, cy=300, radius=250 im 600er ViewBox). Sichtbarer gestrichelter Rand nur im Editor. Vorschau und SVG-Export behalten Beschneidung, ohne Hilfslinien. Auswahlgriffe dürfen im Editor außerhalb liegen, damit Übergröße bearbeitbar bleibt.
- Smart Guides beim Verschieben: Mitte horizontal/vertikal sowie Kanten/Mittelpunkte anderer sichtbarer Objekte. Magnet schaltet Einrasten. Rastertaste zeigt Raster, Schritt 20 SVG-Einheiten.
- Eindeutige Priorität: Ohne Raster hat Produktmitte Vorrang vor nahen Objektankern. Mit Raster+Magnet sind beide Positionsachsen strikt rastergebunden; Objektguides sind dann nur Anzeigen tatsächlich passender Anker, sie verschieben nicht vom Raster weg. Ohne Magnet freie Bewegung, Orientierungshilfen bei naher Ausrichtung.
- Upload bis einschließlich 10*1024*1024 Bytes. Echte Bilddekodierung verwirft beschädigte Dateien. Originalblob wird in IndexedDB gespeichert, im Design nur assetId; beim Laden neuer Blob-URL. So überschreiten 10MB-Bilder nicht das localStorage-Limit. Alte Data-URI-Bilder weiter lesbar.
- IDs aus getRandomValues statt ausschließlich randomUUID, damit Erstellung auch in eingebetteten Vorschauen funktioniert.

### Dateien / Architekturergänzungen
- `editorCatalog.js`: Fonts, Shapes, Einheiten, Icons.
- `ObjectArtwork.jsx`: tatsächliche Gravur und Bounds; `SelectionHandles.jsx`: Bearbeitungsgriffe getrennt von Clip-Gruppe.
- `FontPicker.jsx`, `TextPanel.jsx`, `PropertyControls.jsx`, `EditorTools.css`: Erweiterungen der vorhandenen Bedienoberfläche.
- `TouchSlider.jsx`: wiederverwendete, touch-optimierte Slidersteuerung für Wölbung und Eigenschaften.
- `alignment.js`: Gravurregion, Raster und deterministische Smart-Guide-Prioritäten.
- `lib/imageStorage.js` / `lib/newId.js`: lokale Originalbildablage und browserkompatible IDs.
- `data-panel` auf App und Werkzeugfeld erlaubt eindeutige UI-Zustandsprüfung.

### Tests dieser Erweiterung
- Testagent-Bericht `/app/test_reports/iteration_2.json`: Google Fonts (14/14 geladen), 15 Auswahlmöglichkeiten, Formtypen, Textumriss, große Größen, 44px-Hitfläche, Uploads >2MB, Ablehnung >10MB/kaputter Bilder, IndexedDB-Wiederherstellung, Vorschau/Export geprüft.
- Gemeldete Konflikte zwischen Mitte/Objektankern bzw. Raster behoben. Mobile Navigationspfade vollständig nachgeprüft; zusätzlich aufgefallenen randomUUID-Kompatibilitätsfehler behoben.
- Eigene Regression mit echten CDP-Touch-Ereignissen: 390x844, 375x667, 320x568. Schriftansicht, Umrisstext, Formen; Holz bleibt vollständig sichtbar, kein horizontaler Overflow. Mittelsnap exakt (300,300), Rastersnap exakt (340,340) auf beiden Achsen; Snap-Schalter und ganzer Drag als Undo/Redo funktionieren.
- Separat echte Skalierungsgriffe: Text auf 250%, Linie auf 270mm gezogen. Wölbung nach Wiederverwendung der Sliderkomponente auf 320x568 bis exakt -180/+180 samt Undo/Redo geprüft.
- Ergänzender Bericht `/app/test_reports/editor_tools_regression.json`. Keine Konten/Zugangsdaten erforderlich; `test_credentials.md` entsprechend aktualisiert.

### Nächste optionale Schritte
- P0: keine verbleibenden Fehler aus den geprüften Kernabläufen.
- P1: Gruppierung/Mehrfachauswahl; Zwei-Finger-Zoom.
- P2: Produktspezifische Gravurbereiche aus realem Produktkatalog; Fonts im SVG-Export einbetten statt nur Font-Familien zu referenzieren.

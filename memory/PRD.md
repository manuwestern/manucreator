# ManuCreator — One-Page-Webseite

## Aktueller Stand — 2026-10-05 · P0 Gravurmaske und Aussparungen abgeschlossen

### Auftrag und Freigabe
- Aktueller Nutzerauftrag: **„Gravurmaske und Aussparungen am Artikel“**, anschließend explizit **„P0 los“**. Ausschließlich diesen Umfang umsetzen. Deutschsprachige Kommunikation.
- **Diese Entscheidung ersetzt sämtliche älteren verbindlichen Gravurgrenzen weiter unten:** Elemente dürfen die äußere Gravurfläche und Aussparungen überschreiten. Nur die Darstellung wird maskiert; keine Fehlermeldung wegen Überschreitung, keine automatische Einpassung, Löschung oder Veränderung des Motivs. Fachliche Grenzen wie Vorlagenfreigaben, Zeichenlimit, gültige Formen, zwölf Ebenen und technische Modellgrenzen bleiben bestehen.

### Implementiert
- Artikel besitzen `exclusions: [{id,shape,x,y,w,h}]`, Rechteck/Kreis, bis24 Bereiche. Vorhandene Produkte ohne Feld erhalten `[]`. Größen ab2px, innerhalb des800×800-Produktbilds, eindeutige IDs, endliche Zahlen, gleiche Kreisseiten. Aussparungen dürfen überlappen und die Gravurfläche schneiden. Produktversionen und Snapshots enthalten die Maske.
- Verwaltung → Artikel → **Gravurfläche**: Bereiche auswählen, Rechteck/Kreis hinzufügen, direkt auf Foto zeichnen/verschieben/skalieren, Zahlenwerte bearbeiten, Form wechseln, Aussparung löschen. Grüne Außenfläche und rote Aussparungen; Liste zur Auswahl überlagernder Bereiche. Fotokoordinaten bleiben getrennt von realen Millimetermaßen. Alle neuen DOM-Bedienelemente mit Test-IDs.
- Konva: äußere Clip-Gruppe plus separat geschnittene Komplementgruppen für Aussparungen. Überlappende Löcher bleiben eine gemeinsame Ausschlussfläche, kein XOR-Wiedereinblenden. Auswahl/Transformer außerhalb der Maskengruppe. Vollständig maskierte Elemente weiterhin in Ebenenliste auswählbar und zurückholbar; Undo/Redo erhalten.
- Pillow: gemeinsame4×-Maske mit BOX-Downsampling in `render_layers` UND Legacy-Renderpfaden. Nur Gravur-Overlay wird maskiert; Produktfoto unverändert. Text inklusive Kontur/Versatz, Fotos, Dekorationen und Formen verwenden dieselbe Produktmaske. Kundenvorschau, Vorlagenvorschau,800×800-Download, gespeicherte Entwürfe und Testbestellung enthalten die Maskierung.
- `isValidElement` prüft nur technische Werte/Proportionen; `isInside` nur noch initiale oder bewusst ausgelöste Einpassung. Keine automatische Einpassung bei Duplikat/Zuschnitt/Bearbeitung. Backend weist grenzüberschreitende Elemente nicht mehr zurück. Geschützte Vorlagenfelder und feste Inhalte bleiben unverändert geschützt.
- Bestehende Speicher-/Produktversionsprüfung bleibt: bei geändertem Artikel neu prüfen/speichern; historische Bestellsnapshots bleiben erhalten. Keine Änderung an Authentifizierung, Konten, geschützten Env-Werten, externen Anbietern oder Website/Hero.

### Robustheit und bekannte Infrastrukturgrenzen
- Während Tests zeitweise503 am Vorschau-Gateway (`unconditional drop overload`), Schrift-/Vorschauabrufen und externer Bildablage beobachtet. Speicherlogging bestätigt einen upstream500; die zuvor vermutete genaue Überlastungsursache ist **nicht** bewiesen. Kein dauerhafter Maskenfehler festgestellt und keine Zusage, externe Ausfälle beseitigt zu haben.
- Begrenzte Wiederholungen ausschließlich für nicht kostenpflichtige lesende Vorschau-/Bildabrufe: höchstens3Versuche pro Anfrage, HTTP408/500/502/503/504 bzw. Netzwerkfehler.422 und andere fachliche Fehler nicht automatisch wiederholen. Dauerhafte Fehler sichtbar; **Erneut laden** stellt Vorschau ohne Entwurfsverlust wieder her. Schriftwiederherstellung lädt dieselbe vorhandene CSS-Fontquelle, keinen Ersatzfont.
- Nach Speicher-Playbook bestehende `httpx`-Verbindungen wiederverwendet (12Verbindungen/6Keepalive), sauberer Lifespan-Abschluss; datensparsame Fehlerlogs nur Typ/Status. **Keine neuen automatischen Schreibwiederholungen**, unveränderte Speicher-API und Credentials.
- Optionale Hintergrundentfernung weiterhin ohne geeigneten OpenAI-Schlüssel deaktiviert. Checkout bleibt echter gespeicherter **Testabschluss ohne Zahlung/Fertigung**. Keine gemockten Geschäfts-APIs.

### Verifiziert
- Testing-Agent `/app/test_reports/iteration_23.json`:7/7 neue Backendtests zu Modell, Persistenz, Maskenpixeln, Legacy-Rendering und Vorlagenschutz; Admin-UI und responsive320/768/1024/1440 ohne horizontalen Überlauf.
- Testing-Agent `/app/test_reports/iteration_24.json`: **8/8 Backendtests bestanden**, JUnit `pytest/pytest_results_iteration24_backend.xml`; zentraler Kundenablauf, Admin-Canvasgesten, Maskenpixel, Export, Wiederöffnen/Testabschluss und Produktversionsänderung geprüft.
- Anschließender eigener Lauf des wiederverwendbaren Scripts `/app/tests/studio_iteration24_customer_flow.py` vollständig bestanden; `/app/test_reports/masks-selftest.log` und `iteration24_customer_flow_checks.json` enthalten12 erfolgreiche Checks. Zusätzliche echte Drag-Assertion prüft die Grenzüberschreitung **vor Mouseup** (live Mittelpunkt796,035px), erhaltene Position nach Loslassen. Größen/Rotation zusätzlich über Eigenschaften geprüft; kein physischer Smartphone-/WebKit-Test behauptet.
- Letzter Testbeleg **TEST-DF6B5AB3**, Entwurf `b944c2e6-8443-49c2-87cf-2d7821f12c37`: Elemente und Aussparungen über Speichern → Wiederöffnen → Warenkorb → Testabschluss unverändert. Vollständiger800×800-Export bei100% und250%+Pan pixelgleich, RGB-Hash `331c7b2bc9894ad40991316f5a17148db057ed89b44f872787d557334670bdfd`.
- Zusätzliche flächige Pixelprüfung des tatsächlichen Browserexports gegen serverseitige Maske: alle vollständig ausgeschlossenen Pixel (2px Abstand zum geglätteten Rand) entsprechen dem Rohlingfoto, auch überlappende Löcher/Kreisecken. Nicht nur einzelne Stichproben.
- Lade-Wiederherstellung getestet mit **TEST-ONLY Fehler-Injektion**: einmaliger503 samt Fontfehler, dauerhaft503 mit manueller Wiederherstellung,422 ohne automatische Fehlerschleife. Nachtest verwendet unterschiedliche503-Texte inklusive `unconditional drop overload`; Entscheidung jetzt statusbasiert. Mehrere verschiedene Motivanfragen können insgesamt mehr als3Requests auslösen; Limit gilt pro Anfrage.
- Letzter `yarn build` erfolgreich ohne Compilewarnungen, `/app/test_reports/masks-build.log`; Python compileall bestanden. Smoke1920×800 `/app/test_reports/masks-smoke.jpg`.
-17 eindeutig isolierte UI-Testartikel archiviert (16 `TEST_iter24_customer_flow_*`,1 `TEST_UI_MASK_371874544`); nur vier originale Musterartikel aktiv. Keine Nutzerartikel verändert oder Entwürfe/Bestellungen gelöscht, Testhistorie bleibt erhalten. Keine Zugangsdaten erstellt/geändert.

### Nächste Schritte / priorisierter Backlog
- **P0 Nutzerabnahme:** echte Rohlingfotos mit realen Gravurflächen/Aussparungen einrichten und prüfen; keine offenen reproduzierbaren Quellfehler im geprüften P0-Umfang.
- **P1 separat freizugeben:** Verwaltungsübersicht für Anfragen/Testbestellungen; echte Zahlungen statt Testabschluss. Hintergrundentfernung erst nach geeignetem API-Zugang aktivieren/testen.
- **P2 separat:** Ellipsen/Polygone als Aussparungen, reale Anwendungsszenen, Produktionsdateien/erweiterter Vektorexport. Sinnvolle Ergänzung: Masken als wiederverwendbare Artikel-Presets.
- Alter Online-CORS-Secretstatus unten bleibt **separater, nicht erneut geprüfter Betriebsstatus**. Nutzer meldete während Abschluss einen asynchron gestarteten Veröffentlichungsvorgang; kein Ergebnis/Live-Erfolg bestätigt. Keine weitere Veröffentlichung ausgelöst und keine Produktionskonfiguration verändert.

## Offener Betriebsstatus vor P0-Maskenausbau — 2026-10-05 · Produktionsanmeldung wartet auf Secretänderung
- Neueste Nutzermeldung: „Wie kann ich mich in die Verwaltung einloggen ? In der deployteb Version steht Nicht erlaubter Ursprung der Anfrage.“ Genaue Seite vom Nutzer bestätigt: `https://manucreator.de/verwaltung`.
- **Produktions-RCA bestätigt:** bestehender Deployment-Secret `CORS_ORIGINS` hat den Wert `*`. Admin-CSRF-Prüfung erlaubte nur exakte Einträge, daher403 vor jeder Passwortprüfung. Runtime-Log: `Admin origin rejected: received='https://manucreator.de' configured='*'`. Frontend-Backend-Adresse ist korrekt `https://manucreator.de`, Backend erreichbar, Cookie-Eigenschaften nicht Ursache. RCA: `/app/deployer-agent-docs/RCA_c9ec455d-e9ee-401e-a1f5-caa30af83000.MD`.
- **Wichtig:** vorhandene Produktions-Secrets werden bei erneuter Veröffentlichung nicht durch Änderungen an backend/.env überschrieben. Hauptagent/Produktionsdiagnose können diesen vorhandenen Secretwert nicht direkt ändern. Nutzer muss im Veröffentlichungspanel → Secrets den bestehenden Schlüssel `CORS_ORIGINS` ändern auf: `https://manucreator.de,https://www.manucreator.de,https://subtle-motion-8.emergent.host`, speichern und eine erneute Veröffentlichung freigeben/auslösen. Danach Live-Anmeldung testen. Bis dahin ist die Online-Verwaltung weiterhin blockiert; nicht als live behoben bezeichnen.
- **Quellkorrektur umgesetzt:** `studio/origins.py` liefert eine gemeinsame explizite Domainliste für `admin_auth.same_origin` und `server.py` CORSMiddleware. Leerzeichen/abschließender Slash/Standardport/Hostschreibung normalisiert, Duplikate entfernt; `*`, `null`, fremde Protokolle, Credentials, Pfade/Queries/Fragmente und Wildcard-Domains bleiben unzulässig. Kein beliebiger Origin/Host/Forwarded-Header wird vertraut. Cookie-Attribute/JWT/Seed/Passwörter unverändert.
- Backend/.env um die drei konkreten Live-Ursprünge ergänzt, bestehende zwei Vorschau-Ursprünge erhalten. Geschützte DB-/Frontend-Variablen unverändert. Backend nach Env-Änderung neu gestartet; keine Veröffentlichung oder Produktions-Secretänderung durch den Hauptagenten durchgeführt.
- **Testing-Agent-Verifikation (vom Nutzer ausdrücklich verlangt):** `/app/test_reports/iteration_22.json`,10/10 Tests in `backend/tests/test_admin_origin_policy_iteration21.py` bestanden; JUnit `test_reports/pytest/pytest_results_iteration22_admin_origin.xml`. Zulässige Origins mit echtem Vorschau-Login/Me/Refresh-Rotation/Logout, sichere Cookies, fremde/fehlende/null Origins, manipulierte Forwarded-Header, Sperrgrenze und Wildcard-fail-closed geprüft. Vorschau-Browserlogin und Navigation bestanden. Keine neuen Benutzerkonten oder Anmeldeinformationen.
- Zusätzliche scheinbare Fehler aus Iteration21 als Vorschau-Infrastruktur eingegrenzt: Gateway normalisiert nur die eigene Alias-Origin zum ebenfalls freigegebenen Cluster-Ursprung. Direkte ASGI-Tests erzwingen exaktes Echo für alle Domains; externe Tests berücksichtigen ausschließlich diese bestätigte gleichnamige Vorschauzuordnung. Keine Lockerung am Anwendungscode. Troubleshooting hat10Schritte dokumentiert; Iteration22 ohne offene Quellfehler.
- **Noch offen:** Betreiber muss bestehenden Online-Secretwert ersetzen und Aktualisierung freigeben; danach Produktionsveröffentlichung und einmaliger Testing-Agent-Livetest Login → `/me` → Refresh → Logout. Nicht automatisch weitere Features beginnen. Bisher weiterhin403 in Live, von Iteration22 bestätigt. Keine echten Produktionsdaten ändern.
- Auth-Prüfleitfaden erweitert: `/app/auth_testing.md`. Nächste Nutzerfrage soll konkret die Secretänderung und anschließende Aktualisierung bestätigen lassen; falls Nutzer die Oberfläche nicht findet, Plattformhilfe heranziehen. Keine Cache-/Inkognito-Empfehlung als Ersatzfix, kein Passwortreset ohne Bedarf.

## Funktionsstand vor Produktions-Authfehler — 2026-10-05 · Eigene Artikelvorlagen und sechs Formenwerkzeuge

### Aktuelle Freigaben / Originalanforderungen
Diese Zusammenfassung ersetzt den weiter unten archivierten 40-Vorlagen-Stand. Nutzerkommunikation ausschließlich Deutsch.
1. **„ManuCreator – Eigene Artikelvorlagen und Dekorationen“**, Phase1: zurück zu sechs schlichten Grundvorlagen; eigene artikelbezogene Vorlagen mit festen Inhalten/freigegebenen Kundenfeldern, Entwurf/Veröffentlichung/Archivierung, einstellbarer freier Bearbeitung; eigene transparente PNG-/statische SVG-Dekorationen und vorhandene geschützte Verwaltung/Dateiablage weiterverwenden. Rechteck/Kreis und reale Millimetermaße direkt am Artikel. Keine integrierte Pfadbearbeitung oder echten Zahlungen.
2. Konkrete UI-Korrektur: **Vorlagenbilder nur halb sichtbar**, Schriftgröße als **Dropdown plus freie Zahleneingabe in derselben Zeile wie Stärke/Stil**, redundante Textmuster-Vorschau entfernen. Nutzer verlangte ausdrücklich Testing-Agent-Verifikation; diese erfolgte in Iteration19 und Regression20.
3. **„ManuCreator – Einfache Formenwerkzeuge für Gravurmotive“**, Phase1: genau **Linie, Kreis, Rechteck, Herz, gleichseitiges Dreieck, fünfzackiger Stern**, Klick-Einfügung in Admin-Vorlageneditor UND freiem Kundenstudio. Gefüllt/Kontur, passende Größenfelder, verbindliche Grenzen, zwölf Ebenen, geschützte Vorlagen und unveränderte Übernahme in Vorschau/Speicherung/Download/Testabschluss. Kein Aufziehen, Freihand-, Boolescher- oder Pfadeditor.

**IMPLEMENTIERT UND GEPRÜFT:** aktueller Phase1-Umfang abgeschlossen; keine bekannten offenen funktionalen Blocker. Die vom Nutzer später gestartete Veröffentlichung läuft außerhalb dieser Feature-Verifikation; hier wird kein Produktionsstatus behauptet.

### Aktuelles Kundenerlebnis und Verwaltung
- Die neue Kundenauswahl enthält ausschließlich sechs schlichte Grundlagen (Name/Monogramm, Hochzeit, Geburtstag/Jubiläum, Foto, Firma/Verein, Widmung) plus eigene veröffentlichte Vorlagen des gewählten Artikels. Keine ungefragten Ornamente/Effekte in den Grundlagen. Die 40 Materialkompositionen und die Sammlung18 sind **nicht** wieder zum Hinzufügen verfügbar. Alte gespeicherte Motive bleiben renderbar.
- Eigene veröffentlichte Vorlagen stehen zuerst; Grundlagen lassen sich pro Artikel abschalten. Namenssuche, tatsächliche Produktbilder, Ersatzbestätigung und Undo/Redo bleiben vorhanden. Neue Vorlagen werden nur bei passender aktueller Fläche/Inhaltsfreigabe angeboten.
- Verwaltung unter `/verwaltung`: Artikel auswählen → **Artikeldaten / Gravurfläche / Vorlagen**. Material und Materialgruppe bleiben artikelbezogen, keine globale Materialverwaltung. Eine aktive Rechteck- oder Kreisfläche, Direktmanipulation auf Foto plus Zahlenwerte; Kreis mit Durchmesser statt separater Höhe. Pixelpositionen und manuell erfasste reale mm getrennt. Änderungen prüfen Vorlagen und Cart erneut; keine automatische Umgestaltung gespeicherter Entwürfe.
- Adminvorlageneditor `/verwaltung/artikel/:productId/vorlagen/:templateId` (`neu` für neue Vorlage): benennen, platzieren, Ebenen, Texte/Foto- oder Logofelder/eigene Dekorationen/Formen, 25 vorhandene Schriftfamilien, Textbogen/Kontur/harter Versatz. Kundenfelder mit Label, Beispiel, Pflicht/optional, Zeichenlimit und reserviertem Slot; feste Inhalte getrennt. „Frei bearbeiten“ pro Vorlage, standardmäßig erlaubt. Echte Kundenvorschau, Speichern, Veröffentlichen, Duplikat, Sortierung, Archivieren.
- Veröffentlichungen sind unveränderliche Revisionen. Draft-Änderungen überschreiben die aktive Gestaltung nicht; erst erneute Veröffentlichung. Einfacher Kundenmodus zeigt ausschließlich freigegebene Felder. Bei eingeschränkten Vorlagen verhindert Backendvergleich Manipulation fester Inhalte, Geometrie, Ebenenliste, Modus und Freigaben. Bewusst freie Entwürfe bleiben erlaubt.
- Originaldateien und Entwurfsmotive sind adminprivat. Bibliothek `/verwaltung/dekorationen`: PNG mit Transparenz oder statisches SVG, höchstens8MB, PNG höchstens20MP; Original bleibt erhalten. Einfarbige Rasterdarstellung benötigt ausdrückliche Bestätigung samt Nutzungsrechten. SVG-Allowlist ohne Text, Skripte, Animation, Fremdquellen, Bilder, HTML, Filter oder nicht unterstützte Effekte; klare Ablehnung statt Teilübernahme. Keine automatische Vektorisierung/Freistellung.
- Eigene Dekorationen werden separat veröffentlicht/archiviert und pro Artikel für die freie Kundengestaltung freigegeben. Bestätigte Entwurfsmotive sind im Admineditor verwendbar, für eine Vorlagenveröffentlichung müssen verwendete Motive veröffentlicht sein. Hochgeladene Linien/Pfadpunkte bleiben nicht einzeln bearbeitbar. Gastgebundene Nutzungsfreigaben erhalten historische Darstellungen auch nach Archivierung; kein endgültiges Löschen verwendeter Motive in der Oberfläche.

### Sechs Grundformen — Verhalten
- Kompakter **Formen**-Popover, sechs erkennbare Symbole, keine dauerhafte Zusatzspalte. Ein Klick erzeugt eine passende zentrierte Form und wählt sie aus; keine Veröffentlichung/Freigabeliste wie bei hochgeladenen Motiven notwendig.
- Linie: gerade mit stumpfen Enden; Länge und Strichstärke unabhängig. `h == stroke_width`; direkte Transformation nur an den beiden seitlichen Griffen. Länge/Rotation verändern die Dicke nicht.
- Kreis: Durchmesser, immer `w == h`; Außenkreis wird für Kreis- UND Rechteckgrenzen geprüft, unabhängig von Rotation. Gefüllt oder Kontur. Rasterrandreserve verhindert Glättungspixel außerhalb der deklarierten Kreisfläche.
- Rechteck: getrennte Breite/Höhe; Proportionssperre schaltbar. Acht Griffe frei bzw. vier Griffe proportional. Herz, gleichseitiges Dreieck und fünfzackiger Stern behalten ihr Verhältnis und haben vier proportionale Griffe.
- Alle geschlossenen Formen: Gefüllt/Kontur, freier Innenraum bei Kontur, einstellbare Konturstärke. Zu starke Konturen für eine kleine Form werden abgelehnt statt zu einem gefüllten Klumpen. Monochrom im Artikel-Gravurfarbton; keine Farben/Verläufe/Schatten für Formen.
- Jede Form eine Ebene; alle Ebenenaktionen und Undo/Redo, maximal12 insgesamt. Formen sind in Vorlagen feste Elemente, keine Kunden-Eingabefelder. Einfacher Modus hat keine Formwerkzeuge. Eingeschränkte Vorlage erlaubt weder neue Formen noch Formänderung/-löschung; serverseitig abgesichert. Bei freigegebener freier Bearbeitung bleiben Sperrstatus und sämtliche Elemente zunächst unverändert.
- Live-Grenzprüfung schon während Drag/Scale/Rotate sowie bei numerischen Eingaben, Länge, Kontur/Füllung und Strichstärke. Ungültig → letzter gültiger Stand, sichtbare Grenzmeldung. Kreisformen nicht gegen Quadrat-Ecken prüfen. Kein automatisches Beschneiden/Verzerren zum Erzwingen ungültiger Werte.

### Korrigierte UI-Probleme
- Ursache der halb sichtbaren Vorlagenbilder: implizite Grid-Zeilen wurden kleiner als ihre Karten. Jetzt inhaltsgroße Zeilen, eigener quadratischer Bildbereich mit `object-fit:contain` und begrenztem Scrollcontainer; keine Kartenüberlappung.
- Stärke, Stil und Schriftgröße haben identische Label-/Feldraster. Schriftgröße über Popover-Presets oder freie Dezimalzahl4–200px; keine zusätzliche Textmusterbox. Beschriftung/Dropdown bleiben mobil bedienbar.
- Doppelte React-Keys im Admin-Eigenschaftenbereich durch getrennte `fields-…` und `properties-…` Schlüssel behoben. Zurück führt unmittelbar zum Vorlagenbereich des Artikels (`?tab=templates`).
- „Als Kundenfeld bearbeiten“ bleibt während laufender Textvorschau bedienbar. Funktionale Updates gegen aktuellen Design-Ref und gezielte Text-/Geometriepatches verhindern das Überschreiben gleichzeitig geänderter Freigaben. Explizites `template_slot:null` bei festem Text wird respektiert.
- Grenzmeldungen für Formen beziehen sich jetzt auf Fläche/Formproportionen und nicht auf Schriftgröße.

### Architektur / wichtige Dateien und Endpunkte
- Backend neu: `studio/article_templates.py`, `decoration_library.py`, `decoration_uploads.py`, `svg_worker.py`, `shapes.py`. Erweitert: models/products/templates/storage/layer_rendering/transform_geometry/router/cart/setup/server. Bestehende Auth-Dependencies unverändert weiterverwendet, keine Konten-/Passwortänderungen.
- SVG: `defusedxml`-Allowlist, CairoSVG in separatem Prozess mit Laufzeit-/Speicherlimit, danach einfarbiges transparentes PNG. CairoSVG/defusedxml via pip installiert, requirements durch pip freeze aktualisiert. Originale im bestehenden Objektspeicher bleiben privat; keine neuen Anbieter.
- Collections: `studio_article_templates` (änderbarer Entwurf, veröffentlichte Revisionreferenz, Sortierung/Archiv), `studio_template_revisions` (unveränderliche Designs), `studio_template_uses` (Gast+Revision), `studio_decorations` (Metadaten, private Original-/PNG-Datei-IDs, Status/Bestätigung), `studio_decoration_grants` (Gast+Motiv). Eindeutige Indizes; ObjectIds werden nicht an Clients ausgegeben.
- Produkt erweitert um `show_basic_templates` und `decoration_ids`. Element erweitert um `decoration_id`, `field_required`, `field_max_length`, sowie `kind='shape'`, `shape_type`, `shape_mode`, `shape_proportional`. Design erweitert um `template_revision_id`, `allow_free_edit`. Alte Designs bekommen neutrale Defaults, keine neu sichtbaren Elemente.
- Admin: `/api/admin/article-templates` CRUD/duplicate/publish/archive/preview; `/api/admin/decorations` upload/confirm/publish/archive/sprite/private-original. Kundenseitig `/api/studio/article-templates/{id}/apply|preview`, `/own-decorations`, `/own-decorations/{id}/use`, `/decoration-assets/{id}`; vorhandene `/templates` kombiniert Grundlagen/eigene Artikelvorlagen.
- `POST /api/studio/shape-preview`: validierter gemeinsamer Formrenderer. Servervalidierung und Browsergeometrie stimmen hinsichtlich Verhältnis/Strich/Fläche überein. Shapes brauchen weder Motivgrant noch KI/Storage-Upload.
- Frontend: `AdminTemplateEditor`, `AdminTemplateToolbar`, `AdminDecorationLibrary`, `AdminAssetImage`, `ArticleTemplates`, `AdminCustomerPreview`, `TemplateFieldSettings`, `FontSizeControl`, `ShapePicker`, `ShapeProperties`; Canvas/Ebenen/Properties/TemplateFields/BlankForm/BlankAreaEditor/StudioPage und `studioShapes.js`, `transformGeometry.js`, `textPreview.js` erweitert. Styles `studio-admin-templates.css`, `studio-controls-fixes.css`, `studio-shapes.css`.
- Website/Hero,25Fonts, Kundenbild-Upload/Zuschnitt, Zoom50–400%, Handwerkzeug, große Produktvorschau, optionale GPT-Freistellung unverändert. **GPT-Freistellung weiterhin nicht eingerichtet** ohne geeigneten eigenen OpenAI-Zugang; keine Fallback-KI. Testabschluss0€, keine Zahlung/Fertigung/Freigabe. Keine Aussage zu Materialtauglichkeit oder Mindestlinienbreite.

### Tests und Nachweise — 2026-10-05
- `/app/test_reports/iteration_18.json`:14 Backendtests eigener Vorlagen/Dekorationen sowie ursprünglicher UI-Bug geprüft; danach gemeldete Frontendpunkte behoben.
- `/app/test_reports/iteration_19.json`: Bilder, exakt gemeinsame Schriftzeile/Preset/manuelle Zahl/entfernte Zusatzvorschau, Navigation und React-Keys bestätigt; positiver geschützter eigener-Motiv-Template→Speichern→Checkout→Archivwiedergabe-Lauf bestanden. Damals verbleibende Kundenfeld-Umschaltung anschließend korrigiert.
- `/app/test_reports/iteration_20.json`: Formen-Backend und UI,16/16 Gesamttests der Kombination; alle sechs Formen und Modi, proportionale/nicht-proportionale Änderung, konstante Linienbreite, Schutzeinstellungen,12Ebenen, Live-Grenzen bei250%+Pan inkl.399px-Kreis in400px-Fläche, UI320/390/768/1024/1440 ohne Überlauf. Vorheriger Umschaltfehler ausdrücklich durch Testing-Agent nachgeprüft: während der Vorschau ausgeschaltet, nach Rendern weiterhin fest.
- Letzter Backendlauf16/16 grün: `/app/test_reports/shapes-final-pytest.log`, JUnit `/app/test_reports/pytest/shapes-final.xml`. Fixture-basierter Test für feste/Pflichttexte wurde präzisiert: personalisierbares Feld wird über `template_field` erkannt (Veröffentlichung ersetzt Element-IDs).
- Abschließende Prüfdatei-Bereinigung: geteilte pytest-Fixtures in beiden Iteration20-Testmodulen über `pytest_plugins` statt gleichnamiger Imports eingebunden; damit die zwei F811-Abschlussblocker entfernt. Anschließend dieselben16 Tests nochmals vollständig bestanden (57,09s). Keine Änderung am Anwendungscode oder an Zugangsdaten.
- `/app/tests/shapes_final_flow.py` → `/app/test_reports/shapes-final-flow.json`: neun erfolgreiche echte Browser-End-to-End-Prüfungen ohne Mock-API. Admin veröffentlicht Vorlage mit Konturkreis, Linie, Konturherz und Pflichttext; Kunde kann nur Vorname ändern; real speichern, vollständige Exporte, große Vorschau, Wiederöffnen, Warenkorb/Testabschluss, Archivieren und historische Wiedergabe/erlaubte erneute Personalisierung.
- Formen-Downloads100% und250%+Pan sind800×800 und RGBA-pixelidentisch; auch nach Wiederöffnen und Archivieren identisch. SHA256 `ad2c7223e2a2539dea00fe57638ab8ed7f3dbe8f0d26e00edb5ff66af8b333a4`. Testbeleg `TEST-8DA366DE`,0€, keine Produktionsfreigabe. Snapshots enthalten alle Formeigenschaften unverändert.
- Build erfolgreich ohne Compilewarnungen: `/app/test_reports/shapes-build.log`. Smoke `/app/test_reports/shapes-smoke.jpg`. Browserautomatisierung ersetzt keinen physischen iPhone-/Android-Test; WebKit wurde in dieser Umgebung nicht vollständig geprüft.
- Nur erkannte eigene Testvorlagen archiviert (keine Nutzerartikel geändert): `a204a85f-d31e-48af-b4fc-c85f82c40de8`, `f5a15141-6410-46a8-b141-d091853c2baf`; eigene End-to-End-Testvorlagen ebenfalls archiviert, historische Belege erhalten. Abschlusskontrolle Holz: genau sechs schlichte öffentliche Grundlagen; alte Dekorationsliste leer. Keine Auth-Zugangsdaten geändert, keine kostenpflichtigen KI-Aufrufe.

### Nächste Schritte / priorisierter Backlog
- **P0:** keine bekannten offenen Fehler im freigegebenen aktuellen Umfang. Keine zusätzlichen Funktionen ohne neue Freigabe beginnen.
- **P1 Nutzerabnahme:** eigene Artikelmaße/Gravurflächen kontrollieren, eigene reale Motive/Vorlagen veröffentlichen, Formen und Schriftbedienung auf physischem Smartphone prüfen. Reale Betreiber-/Rechts-/Speicherangaben bleiben separat zu finalisieren.
- **P1 optional blockiert:** GPT-Freistellung nur nach geeignetem eigenem OpenAI-Zugang aktivieren und echt testen; sonst unverändert deaktiviert.
- **P2 nur nach Freigabe:** weitere Formvarianten (z.B.Pfeile/abgerundete Rechtecke), Bibliotheksorganisation/Vorlagenfavoriten, artikelübergreifender Vorlagentransfer. Keine automatische Rückkehr zu40Templates/18Ornamenten.
- **P2/Phase3 nur separat:** Freihand-/Pfadwerkzeuge, Aufziehen, Verbinden/Ausschneiden, mehrere Gravurflächen/Seiten, geeignete Produktionsdateien und Auftragsbearbeitung. Echte Zahlungen/automatische Fertigung nicht Teil dieses Ausbaus.
- Passende spätere Verbesserung: wiederverwendbare Kombinationen eigener Formen in Artikelvorlagen, um häufige Geschenkgestaltungen schneller vorzubereiten.

## Archivstand — 2026-10-05 · frühere 40 Materialvorlagen / abgelöste neue Auswahl

### Originalauftrag / aktuelle Freigabe
Der Nutzer hat den Plan **„ManuCreator – Materialvorlagen, Rahmen und Gravureffekte“** ausdrücklich freigegeben und mit **„Ok los“** zur Ausführung bestätigt. Nur Phase 1: insgesamt 40 eigenständige Vorlagen (16 Holz / 14 Metall / 10 universell, einschließlich der bisherigen sechs Themen), passende gefilterte Vorlagenwahl, vorbereitete editierbare Rahmen/Ornamente, Konturtext und scharf versetzter Gravurschatten. Einfacher Modus, bewusster Wechsel zur freien Bearbeitung, verbindliche Rechteck-/Kreisgrenzen einschließlich sämtlicher Striche/Effekte und durchgängige Speicherung/Vorschau/Download/Testabschluss bleiben maßgeblich.

**UMGESETZT UND VERIFIZIERT:** Der freigegebene Ausbau ist fertig. Keine bekannten offenen funktionalen Blocker in diesem Umfang. Optionale GPT-Freistellung weiterhin mangels eigenem geeignetem OpenAI-API-Schlüssel nicht eingerichtet. Keine neuen externen Dienste, Schriftfamilien, KI-Aufrufe, echten Zahlungen oder Produktionsaufträge.

### Implementierter Umfang
- **40 Kompositionen, nicht 40 zusätzliche Vorlagen:** Holz16, Metall14, Universell10; Themen exakt gemäß Freigabe. Die IDs der bisherigen sechs Vorlagen bleiben bestehen. Neue Auswahl liefert Version2; gespeicherte ältere Designs werden nicht nachträglich umgestaltet.
- Materialfilter serverseitig: Holz+Universell für Holz, Metall+Universell für Metall, nur Universell für andere Materialien. Form, tatsächliche Fläche, Textlänge und freigegebene Text-/Foto-/Logoinhalte bestimmen die Auswahl. Auf Musterrohlingen aktuell Holz26, Metall23, Glas9; nicht jedes Produkt bekommt alle40.
- Anlass-/Verwendungszweckfilter und Namenssuche im bestehenden kompakten Vorlagendialog. Jede Vorschau zeigt die echte gerenderte Gestaltung auf dem aktuellen Rohling. Keine zusätzliche dauerhafte Seitenspalte. Für kleine/schmale Flächen reduzierte Kompositionen mit weniger Sekundärdekorationen/optionalen Feldern; auf kleinen Holzflächen werden ungeeignete dekorative Holzvorlagen ausgefiltert.
- **18 vorbereitete Dekorationen:** einfacher/doppelter Rechteck- und Kreisrahmen, Linie, Rautentrenner, technische Ecken, Blätterzweig, Blätterkranz, Lorbeer, Blumenkranz, Namensband, Herz, Stern, Berge, Wald, Pfote, Sternengruppe. Monochrome tatsächliche Motive, keine Sticker-/Foto-/KI-Generierung. Mehrteilige Ornamente bleiben jeweils eine Ebene.
- Vorlagendekorationen stehen vor Textebenen in der Zeichenreihenfolge (hinten), sind zunächst gesperrt und fangen keine Textauswahl ab. Freie Dekorationen über Dialog hinzufügbar; Ebenenliste mit Namen, proportionalem Skalieren, Bewegen, Drehen, Sichtbarkeit, Sperre, Reihenfolge, Duplikat und Löschen. Strichstärke berücksichtigt Außenmaße. Maximal12 Ebenen inklusive Dekorationen.
- **Texteffekte:** gefüllter Text oder ungefüllte Kontur mit Stärke; scharfe versetzte Textsilhouette mit Abstand/Richtung; beide kombinierbar mit Bogen und Rotation. Eine gemeinsame Textebene, keine weichen Schatten, Leuchteffekte, Farben oder Tiefensimulationen. Schriften und Schriftvarianten unverändert.
- Einfacher Modus zeigt nur benannte Text- und Motivfelder, keine Dekorationseinstellungen. Zu lange Texte werden nicht gekürzt/abgeschnitten. Echte Bildplatzhalter müssen vor Speicherung/Download/Testabschluss ersetzt werden. Bewusster Wechsel „Frei bearbeiten“ übernimmt Elemente unverändert. Ersetzen bestätigt; Undo/Redo stellt auch den Modus wieder her.
- Textsprites enthalten die gesamte Kontur und den gesamten Versatz. Browser und Backend verwenden denselben Renderer. Live-Transformationen skalieren Text-/Effektparameter bzw. Dekorationsstriche proportional und stoppen bei Ungültigkeit. Kreisrahmen werden über die äußere Kreisfläche statt die Ecken des umgebenden Quadrats geprüft.
- Zusätzlich Rasterfilter-Randreserve für Kreisrahmen: auch schwache Glättungspixel nach Rasterung/Rotation bleiben innerhalb der deklarierten Kreisfläche. Kein stilles automatisches Verzerren/Beschneiden, um ein Motiv passend zu machen.
- Zoom/Pan bleiben reine Ansicht. Große Produktvorschau, vollständiger 800×800-Download, gespeicherter Entwurf und Testbestellung enthalten dieselben Elemente und Effekte. Testmodus mit0€ und ohne Fertigung bleibt ausdrücklich erhalten. Website/Hero unverändert.

### Architektur / Dateien
- Backend neu: `studio/template_catalog.py` (40 authored compositions), `ornaments.py` (18 zusammenhängende Rastermotive), `decorations.py` (Katalog/Thumbnails/Sprites), `engraving_effects.py` (monochrome Masken, kein Provider). `templates.py`, `models.py`, `text_engine.py`, `transform_geometry.py`, `layer_rendering.py`, `server.py` erweitert.
- Element erweitert: `kind='decoration'`, `ornament`, `stroke_width`, sowie `text_mode`, `outline_width`, `shadow_enabled`, `shadow_distance`, `shadow_angle`. Alte Elemente erhalten nur neutrale Standardwerte; keine sichtbaren Effekte werden automatisch aktiviert.
- Neue APIs: `GET /api/studio/decorations`, `GET /api/studio/decorations/{id}/thumbnail`, `POST /api/studio/decoration-preview`. Bestehende Vorlagen- und Textvorschau-APIs erweitert. Keine neue DB-Collection; neue Eigenschaften bleiben in bestehenden Entwurfs-/Bestellsnapshots. Mongo-IDs bleiben ausgeschlossen; keine Secrets/URLs in Anwendungscode ergänzt.
- Frontend neu: `DecorationPicker`, `DecorationProperties`, `TextEffects`, `studio-ornaments.css`. Bestehende Vorlagenwahl, Inhaltsfelder, Canvas, Ebenen, Eigenschaften, Geometry/Sprite-Cache und StudioPage erweitert.
- Keine Änderung an Auth-Logik, Admin-Zugangsdaten, Upload-Backend, Hintergrundentfernung oder geschützten Env-Schlüsseln.

### Verifikation / 2026-10-05
- Testing-Agent `/app/test_reports/iteration_17.json`: Katalog40/16/14/10, passende Listen, Apply und Vorschau sämtlicher kompatibler Vorlagen auf Musterprodukten, synthetische Kreisflächen, Dekorationen18, unterschiedliche Textmasken, Auth-Regression und API-Testabschluss bestanden. UI-Vorlagenwechsel/Filter/Undo/Redo, einfache Felder und Ebenenaktionen bestätigt.
- Nach Testbefund behoben: übergroße Schatten-Checkbox durch spezifische Checkbox-Regel auf16×16; anschließend im Browser gemessen. Gemeldete langsame Warenkorb-Navigation nicht reproduziert: Nachtest0,09s nach gespeicherten Entwurf; tatsächliches Speichern0,62s (keine garantierte Laufzeit).
- Zusätzlicher Grenztest fand Range-Input-Rundung bei proportional skalierten Strichstärken: Browser-Schrittwert und React-Kontrollwert jetzt synchron, ohne präzise Modellwerte ungefragt zu ändern. Ungültige Rahmenstärke lässt Gestaltung UND Fehlermeldung stabil bestehen.
- `/app/test_reports/materials-final-verification.json`: zehn erfolgreiche Checks – ungültiger Textschatten unverändert abgelehnt, tatsächliche Konva-Live-Transformation vor Abschluss bei250%+Pan, Maus-Drag von gebogenem/gedrehtem Konturtext mit Schatten,399px-Kreisrahmen in400px-Kreisfläche, unzulässige Strichstärke/Position/Skalierung, Drehung137°, zwölf Ebenen; responsive320/768/1024/1440 ohne horizontalen Überlauf, Canvas und Dialoge begrenzt. Script `/app/tests/materials_final_verification.py` erwartet temporäre Kreis-Fixture `TEST_material_round_final`; diese samt Testbild nach allen Läufen gezielt entfernt.
- `/app/test_reports/materials-checkout-verification.json`: durchgängiger UI-Lauf von Kontur+Schatten+Bogen50°+Drehung15° über tatsächliche Speicherung/Wiederöffnung bis Testabschluss; Element-Snapshots exakt gleich. Große Vorschau identisch. Exporte100% und250%+Pan800×800 und **RGBA-pixelidentisch**, Hash im Bericht. Testbeleg `TEST-273057E2`, Zahlbetrag0€, keine Fertigung.
- Abschließender Backendlauf: **12/12 Tests bestanden**, `/app/test_reports/materials-final-pytest.log`, JUnit `pytest/materials-final.xml`. Enthält dauerhaften Pixeltest für einfache/doppelte Kreisrahmen bei8/50/256/399px und0°/45°/137°: keine Alphapixel außerhalb des deklarierten Außenkreises. Alte Sechs-Vorlagen-Testerwartung bewusst auf neuen Katalog aktualisiert.
- Letzter Frontend-Produktionsbuild erfolgreich ohne Compilewarnungen: `/app/test_reports/material-templates-build.log`. Keine gemockten Anwendungs-APIs oder kostenpflichtigen Provideraufrufe. Browserautomatisierung ist kein physischer Smartphone-Test.

### Aktuelle nächste Aufgaben / priorisierter Backlog
- **P0:** keine bekannten offenen Fehler im freigegebenen Phase1-Umfang.
- **P1 Nutzerabnahme:** Holz-/Metallvorlagen mit echten Namen, Fotos und Logos ausprobieren; Bedienung auf einem physischen Smartphone prüfen. Reale Rohlingfotos/Gravurmaße und offene Betreiber-/Rechts-/Speicherangaben weiterhin finalisieren.
- **P1 optional, unverändert blockiert:** GPT-Freistellung nur mit geeignetem eigenem OpenAI-Zugang aktivieren und dann separat echt prüfen; kein Ersatzanbieter und keine automatische Aktivierung.
- **P2 nur nach gesonderter Freigabe:** Glas-/Schieferkollektionen, saisonale Reihen, Vorlagenfavoriten (Phase2). Produktionsdateien, Fertigungsprüfungen, Auftragsbearbeitung und reale Tisch-/Anwendungsszenen separat (Phase3). Echte Zahlungen bleiben außerhalb dieses Auftrags.
- Sinnvolle spätere Verbesserung: Vorlagenfavoriten für wiederkehrende Namen-/Geschenkgestaltungen. Kein Vorlagenbaukasten in diesem Ausbau.

## Archivstatus — 2026-10-04 · Zoom, Grenzen, 25 Schriften, sechs Vorlagen

### Neueste Freigabe / Originalanforderung dieses Ausbaus
„ManuCreator – Zoom, sichere Gravurgrenzen und einfache Gestaltungsvorlagen“: 50–400 % Ansichtszoom mit Handwerkzeug und großer Produktvorschau; während jeder Bearbeitungsbewegung verbindliche Rechteck-/Kreisgrenzen; genau 25 gebündelte Standard-Schriftfamilien statt großem Katalog; sechs Gestaltungsvorlagen mit einfachem Inhaltsmodus und ausdrücklichem Übergang in den freien Editor. Nur Phase 1 wurde beauftragt. Echte Zahlung, automatische Fertigung, Beratung, allgemeine Bild-KI und Tischszenen gehören NICHT dazu.

**ABGESCHLOSSEN UND GETESTET:** Alle beauftragten Kernfunktionen sind umgesetzt. Die optionale GPT-Freistellung bleibt mangels eigenem OpenAI-API-Schlüssel absichtlich nicht eingerichtet. Keine bekannten offenen funktionalen Blocker für Zoom, Vorlagen, Schriften oder freie Gestaltung.

### Aktuelle Funktionen und verbindliche Entscheidungen
- `/gestalten`: Desktop-Arbeitsplatz mit Ebenen links, Canvas mittig, Objekteigenschaften rechts; eigenständig scrollende Seitenbereiche. Rohling- und Vorlagenauswahl kompakt oben. Mobile Vorschau bleibt über begrenztem Werkzeugbereich sichtbar, inklusive Querformat/kleiner Bildschirmhöhe. Freie Gestaltung hat Ebenen-/Eigenschaften-Tabs; einfache Vorlagen zeigen Inhaltsfelder.
- Kamera: 50–400 %, 100 % = Einpassen. Zoom-Schaltflächen, Prozentanzeige, Handwerkzeug, Strg/⌘-Mausrad, Mehrfinger-Pinch. Kamera bleibt separater UI-Zustand und verändert keine Elemente/Gravurmaße. Große Produktvorschau zeigt tatsächlichen Rohling samt aktuellem Entwurf, ohne Auswahlrahmen/Hilfslinien; unabhängig zoombar/verschiebbar und nicht editierbar.
- Exporte: vollständige kanonische 800×800-PNG, unabhängig von Zoom/Pan; Kameratransformation und Hilfsmittel werden für Export kurz ausgeblendet/zurückgesetzt und in `finally` vollständig wiederhergestellt. Speicher-/Warenkorb-/Bestellabbildungen ebenso vollständig.
- Live-Grenzen: `CanvasElement` kontrolliert die tatsächliche Konva-Geometrie bereits in `onTransform`, setzt ungültiges Skalieren/Drehen auf den letzten gültigen Stand zurück; Drag-Begrenzung arbeitet über Kamera-Koordinatenumrechnung. Gedrehte Bildecken und vollständige Text-Boundingbox werden berücksichtigt. Bilder bleiben proportional; kein automatischer Zuschnitt/Verzerren. Unmögliche Zahlen-/Texteinstellungen melden Fehler statt stiller Veränderung.
- Ältere ungültige Elemente und bei Rohlingwechsel unpassende Inhalte bleiben erhalten und werden sichtbar markiert. Keine automatische Textkürzung, Löschung oder versteckte Einpassung. Nutzer kann bewusst proportional einpassen/korrigieren. Speichern/Abschluss gesperrt, bis gültig. `cart.check_available` validiert jetzt auch alte Bestandsentwürfe erneut – nicht nur Produktversionen.
- 25 Standardfamilien, 177 tatsächlich verfügbare statische Schriftschnitte mit lokal gebündelten TTF/WOFF2 und Lizenztexten. Alle Varianten auf ÄÖÜäöüß geprüft. Direktes gruppiertes Dropdown, passende Stärke/Kursiv, eigene Textvorschau, keine Installation/Vorschau-laden-Schritte oder externe Schriftbeschaffung im Kundenfluss.
- Familien: Open Sans, Montserrat, Nunito, Raleway; Merriweather, Lora, Playfair Display, Cormorant Garamond, Noto Serif; Oswald, Bebas Neue, Anton, Cinzel; Great Vibes, Dancing Script, Allura, Pacifico, Lobster; Caveat, Kalam, Permanent Marker, Amatic SC; Roboto Mono, Space Mono, Special Elite.
- Großkatalog-Dialog entfernt. `GET /api/studio/fonts` liefert jetzt das gebündelte Manifest; frühere Install-Route liefert 404. Ältere `fs:<id>`-Schriften bleiben über ihre bestehenden gespeicherten Dateien/Lizenzen lesbar und im betroffenen Entwurf als bisherige Schrift erkennbar. Fehlende Alt-Schriften erzeugen eine klare Meldung; kein stiller Ersatz.
- Rotation für Text/Bild, eine Textzeile auf positivem/negativem Kreisbogen, neutrale Krümmung 0. Gemeinsamer serverseitiger Textsprite sorgt für identische Glyphen/Varianten in Canvas und gespeicherter Darstellung. Textbearbeitung hat keine Bild-KI-Aufrufe.
- Vorlagen: `monogram` Name/Monogramm; `wedding` Hochzeit; `birthday` Geburtstag/Jubiläum; `photo` Fotogeschenk; `company` Firma/Verein; `dedication` schlichte Widmung. Nur passende Vorlagen gemäß Bild-/Textmöglichkeiten, Textlimit und tatsächlicher Fläche werden angeboten. Vorschau-Thumbnails auf dem echten Rohling, keine Szenen-/Bild-KI.
- Neue Vorlage ersetzt nach Bestätigung den bisherigen Entwurf; Undo stellt ihn inklusive Modus wieder her. Vorlage startet mit festen Slots/Schriften/Positionen im einfachen Modus. Benannte Textfelder und tatsächliches eigenes Foto/Logo ersetzen, optional zuschneiden; optionale Textzeilen können leer bleiben. Nicht passende Inhalte erhalten Fehlermeldung. Platzhalter sperren Speichern/Download/Abschluss, bis ein echtes Motiv eingesetzt oder bewusst frei weiterbearbeitet wird.
- „Frei bearbeiten“ übernimmt Elemente unverändert und schaltet die vollständigen Werkzeuge frei. Kein automatischer Rückweg in ein eingeschränktes Layout. Zwölf Ebenen, Auswahl, Sperren, Sichtbarkeit, Reihenfolge, Duplizieren, Löschen und 30-Schritte Undo/Redo bleiben erhalten. Gesperrte Bilder intercepten keine Textauswahl.
- Admin `/verwaltung`, Website/Hero, Referenzen, Kontakt und Rechtstexte bleiben erhalten. Testabschluss weiterhin ohne Zahlung/Fertigung oder automatische Bestell-E-Mail. Daten werden wirklich gespeichert; keine gemockten Anwendungs-APIs.

### GPT-Freistellung: aktueller Status, kein lokaler Rückfall
- Auf vorherige ausdrückliche Freigabe ist `background.py` auf OpenAI Images **edit** mit tatsächlichen hochgeladenen PNG-Bytes, transparentem PNG, expliziter Einwilligung, Tageslimits, Request-Idempotenz und Quellbild-Sperre umgestellt. `max_retries=0`, keine unsichtbaren kostenpflichtigen Wiederholungen.
- UI: Original/Ergebnis direkt auf derselben Ebene vergleichen, übernehmen/verwerfen, Original wiederherstellen; Ebene/Reihenfolge/Rotation bleiben erhalten. Abweichende Ausgabeseitenverhältnisse werden proportional mit Transparenz aufgefüllt, niemals gestreckt. GPT kann Motivdetails ändern; keine Pixelidentitätszusage.
- **OPENAI_API_KEY fehlt.** Capabilities zeigen configured=false, Schaltfläche mit Hinweis deaktiviert; explizite Requests geben 503 ohne Anbieteraufruf. Kein Rückfall auf rembg/U2Net/anderen Anbieter. Früher gebündeltes lokales Modell ist nur historischer Bestand.
- Neue Env-Werte: OPENAI_API_BASE_URL, OPENAI_IMAGE_MODEL (derzeit gpt-image-2.5-sunburst nach geprüftem Plan), STUDIO_BG_GLOBAL_DAILY_LIMIT; kein Schlüsselwert erfunden. Bestehender universeller Speicherschlüssel wird NICHT für diesen unbestätigten Edit-Weg eingesetzt. Live-OpenAI-Erfolg kann erst nach Einrichtung separat geprüft werden.

### Architektur / Dateien / Datenmodell
- Neue Backend-Module: `studio/templates.py`, `curated_fonts.py`, `text_engine.py`, `transform_geometry.py`; `fonts.py` ist nur noch Curated-Manifest und lesender Legacy-Zugriff. `background.py` ist optionale direkte OpenAI-Bildbearbeitung. `layer_rendering.py`, `models.py`, `router.py`, `cart.py` erweitert. Keine Änderungen am Hero.
- `bundle_curated_fonts.py` ist ein einmaliges Maintainer-Assetwerkzeug, NICHT Laufzeitcode für Kunden. Pinnt Fontsource-Familienversionen, prüft deutsche Glyphen, erzeugt TTF/WOFF2+SHA256+Lizenzen. Assets: backend/studio/assets/curated-fonts/, frontend/public/fonts/curated/, frontend/src/data/curatedFonts.json. Aktuell 25 Familien/177 Faces, Manifestversion manucreator-curated-1.
- Frontend: `useCanvasCamera`, `CameraControls`, `DesignCanvas` mit Kamera-Group, `CanvasElement` mit Live-Limits, `ProductPreview`, `FontSelector`, `TemplatePicker`, `TemplateFields`, `ElementTools`, `TextProperties`, `ImageProperties`; `studio-precision.css` und `studio-templates.css` ergänzen bestehendes Design. `FontBrowser.jsx` entfernt.
- Design ergänzt `editor_mode` free/simple, `template_id`, `template_version`, `font_catalog_version`. Element ergänzt `font_size`, `rotation`, `curvature`, `image_ratio`, `placeholder`, `template_field`, `field_label`, `template_slot`. Fonts `curated:<family>:<weight>:<style>`, bestehende Built-ins sowie `fs:<32hex>` kompatibel. Kamera NICHT Teil von Design/Layout.
- Neue API: `GET /api/studio/templates?product_id=...`, `GET /templates/{id}/preview`, geschütztes `POST /templates/{id}/apply`; `POST /api/studio/text-preview`; Curated-Manifest und Legacy-Fontdatei-/Lizenzrouten.
- MongoDB ergänzt aus vorherigem Ausbau studio_font_assets, studio_font_catalog, studio_font_installs (nun historisch/Legacy), studio_bg_requests, studio_bg_locks. Schriften-Altdateien über bestehenden Objektspeicher; neue gebündelte Fonts benötigen keinen Laufzeit-Objektspeicherdownload. Personenbezogene Bilddateien weiterhin privat.
- Frühere Admin-/Gast-Authentifizierung bleibt unverändert. Kamera/Font-/Vorlagenoperationen sind keine kostenpflichtigen KI-Aufrufe. Server-URLs/DB-/Zugangsdaten weiterhin aus geschützter env-Konfiguration.

### Verifikation / 2026-10-04
- `/app/test_reports/iteration_15.json`: **48 Backendtests bestanden, 1 historischer realer Gemini-Test bewusst übersprungen**. Fontmanifest/25 Familien/177 Faces, deutsche Glyphen/Lizenzen, alle sechs Templates/Previews/Apply, private Daten, Admin, Checkout und Legacy-Gating geprüft. UI-Fonts ohne Google/CDN/Fontsource-Kundenaufrufe; Vorlagenfelder/Fotoersatz/Zuschnitt, Simple→Free, Bestätigung/Undo/Redo, responsive Workspaces bestanden.
- `/app/test_reports/iteration_16.json`: 5 gezielte Backendtests bestanden. Legacy-Invalid-Fixture liest aktuelle Produktversion und trifft nachweislich die Bounds-Korrekturprüfung statt bloß den Versionskonflikt.
- Vor-Mouseup-Skalierung/Rotation bei 250 %+Pan auf Rechteck UND temporärem Kreis: tatsächliche Konva-Knoten/Ecken und Live-Telemetrie geprüft; unzulässige Transformation bleibt beim letzten gültigen Stand.
- **RGBA-Pixelhash identisch** für vollständige Exporte bei 100 % sowie 250 %+Pan; 800×800-Ausgabe, Kamerazustand wiederhergestellt. Schnelles Speichern→Warenkorb teilt laufende Speicherung und erzeugt einen einzelnen Warenkorbposten.
- Mehrfinger-Pinch im Browser per CDP emuliert: 100→400 %, Bereich 50–400 eingehalten, Elemente unverändert. KEIN physischer Touch-Hardwaretest durchgeführt; Geräteabnahme bleibt sinnvoll.
- Letzter Build nach allen Anpassungen: ohne Fehler/Warnungen, `/app/test_reports/templates-build.log`. Harmlose Ladeansicht heißt jetzt studio-canvas-status, echte Fehler separat is-error; falsche Error-Scan-Signale behoben.
- Temporäre Kreis-Testrohlinge mit IDs aus Report16 nach Archivierung gezielt aus der Vorschau-Testdatenbank entfernt, zugehörige unreferenzierte öffentliche Testbilder als gelöscht markiert. Vier aktive echte Muster-Seeds bleiben. Keine Nutzerentwürfe/Bestellungen entfernt.

### Nächste Aufgaben / Prioritäten (nur diese Liste ist aktuell)
- **P0:** keine bekannten offenen Blocker im freigegebenen Kernumfang. Optionaler GPT-Edit bleibt wie vereinbart ohne eigenen Schlüssel deaktiviert.
- **P1 Nutzerabnahme:** Vorlagen mit echten Fotos/Namen ausprobieren; Pinch/Handwerkzeug zusätzlich auf einem physischen Smartphone prüfen. Eigene Rohlingfotos/Gravurmaße einpflegen und rechtliche Betreiber-/Speicher-/Löschangaben final prüfen.
- **P1 nur bei gewünschter Aktivierung:** geeigneten eigenen OpenAI-API-Zugang sicher hinterlegen; danach echten Edit-Erfolg, Transparenz/Motivtreue und Ergebnisübernahme kontrolliert prüfen. Kein Key vorhanden, kein Live-Erfolg behaupten.
- **P2 separat freizugeben:** echte Anwendungsszenen/Tischvorschau (Phase 2); Produktionsfreigaben/-dateien/Auftragsbearbeitung (Phase 3). Kein automatisches Weiterbauen. Eventuell später Kantenpinsel, Favoriten oder Gruppierung nur nach eigener Freigabe.

## Historie vor dem Zoom-/Vorlagenausbau — 2026-10-04 (nachfolgende ältere Pläne sind NICHT maßgeblich)
- ABGESCHLOSSEN UND GETESTET: Admin-Rohlingverwaltung und freier Ebeneneditor. Hero/Website-Slideshows unverändert.
- NEUESTE NUTZERENTSCHEIDUNG: „Alles entfernen, einschließlich Beratung.“ Statt KI-Vorschau/Assistent: Bild hochladen, zuschneiden, Hintergrund entfernen, mehr reguläre Fonts, zusätzliche Textelemente und Ebenen gegen versehentliche Bildauswahl. Für Freistellung: „Nutze KI wo notwendig“.
- Generative KI-Bildvorschau, freie Text-KI UND geführter Dialog entfernt. Alte `/api/studio/quota`, `/assistant/*` und `POST /drafts/{id}/preview` liefern 404. Keine Gemini/Claude-Aufrufe. Historische Daten werden nicht gelöscht; Legacy-ai_status-Felder bleiben nur zur Datenkompatibilität.
- Editor `/gestalten`: maximal 12 unabhängige Text-/Bildebenen; auswählen, ziehen, skalieren, numerisch positionieren, zentrieren, sperren/entsperren, aus-/einblenden, sortieren, duplizieren, löschen, 30-Schritte Undo/Redo. Gesperrte Bilder fangen keine Zeigerereignisse ab. Rechteck-/Kreisgrenzen identisch in Browser und Backend validiert.
- Zehn lokal geladene Schriftvarianten: Nimbus Sans/Roman/Bold und Liberation Sans/Bold/Italic/Serif/SerifItalic/Mono/Narrow. Font-Dateien für Browser und Pillow identisch; Liberation-Lizenz im öffentlichen licenses-Verzeichnis.
- Eigene JPG/PNG/WebP, Rechtebestätigung, max8MB; Bildzuschnitt frei/1:1/4:3, Ziehgriffe und Prozentfelder; Original und Zuschnitt getrennt, Zuschnitt zurücksetzbar. PNG-Download der Direktvorschau.
- Explizite Hintergrundentfernung: rembg2.0.85 + ONNX Runtime CPU + gebündeltes Apache-2.0-u2netp-Modell (4.57MB). SERVERSEITIG lokal, NICHT browserlokal. Keine Übertragung an externe KI-Anbieter und keine generativen APIs. Original bleibt erhalten; Ergebnis privat, wiederverwendbar und rückgängig machbar. Eine parallele Verarbeitung pro Prozess, 2 CPU-Threads, Tageslimit12 pro Gast. Qualität/Kanten motivabhängig.
- Admin `/verwaltung`: JWT/Secure-HttpOnly-Cookies, Passwort-Hash, Refresh-Rotation/Logout, persistente Login-Limits; Zugang in memory/test_credentials.md. Produktfoto normalisiert800×800, Produktdaten, Maße, Beispielpreise, erlaubte Vorlagen, Rechteck-/Kreisfläche per Zeichnen/Transformieren/Zahlen, archivieren/reaktivieren. Idempotente Muster-Seeds; echte CRUD-Daten in MongoDB.
- Rohlingversionen/Entwurfs-Snapshots verhindern unbemerkte Änderungen. Veraltete Rohlinge im gespeicherten Entwurf werden beim Öffnen erkannt und an gültige Grenzen angepasst; vor Checkout neu speichern. Archivierte Rohlinge nicht bestellbar.
- Test-Warenkorb/Testabschluss bleiben OHNE echte Zahlung oder Fertigung. Kein automatischer E-Mail-Versand. APIs sind nicht gemockt; Kontakt, Fotos, Entwürfe und Testbestellungen werden real gespeichert.

### Architektur der Erweiterung
- Backend: `studio/admin_auth.py`, `products.py`, `geometry.py`, `layer_rendering.py`, `background.py`, `guest_limiter.py`; bestehende `router.py`, `models.py`, `cart.py`, `storage.py`, `session.py`, `setup.py`. `ai.py`/`assistant.py` gelöscht.
- MongoDB: `studio_products`, `studio_admins`, `studio_admin_sessions`, `studio_login_attempts`, `studio_guest_counters`, `studio_processed`; bestehende Gäste/Dateien/Entwürfe/Warenkorb/Orders/Inquiries. Produkte enthalten area{x,y,w,h,shape}, version, image_file_id, active, is_sample. Design.elements[]{id,kind,text,font,x,y,w,h,asset_id,original_asset_id,crop,locked,hidden,image_type} ist kanonisch; Altentwürfe werden migriert.
- Bildablage: bestehender privater Emergent Object Storage, öffentliche Produktfotos ausschließlich kind=product_blank. Kundenbilder nie über öffentliche Produktfoto-URL zugänglich. Objektpfade statt Bild-Base64 in MongoDB.
- Frontend: react-konva19.0.10/konva10, react-image-crop11; `DesignCanvas`, `CanvasElement`, `LayerList`, `LayerProperties`, `LayerUpload`, `CropDialog`, `ElementTools`, `BlankForm`, `BlankAreaEditor`, `AdminProductsPage`; `studioLayers.js`, `studioGeometry.js`, `adminApi.js`, `studio-layers.css`. Unbenutzte generative Beratungskomponenten und alte CSS-Zeichenvorschau entfernt.
- Konfiguration: bestehende Env-Schlüssel unverändert erhalten. Neue ADMIN_EMAIL/ADMIN_PASSWORD, REMBG_HOME, STUDIO_BG_MODEL=u2netp, STUDIO_BG_DAILY_LIMIT, STUDIO_GUEST_NETWORK_HOURLY_LIMIT=500, STUDIO_GUEST_GLOBAL_HOURLY_LIMIT=2000. Modelldatei gebündelt unter backend/studio/ml/models/u2netp; kein Laufzeitdownload bei Kundenanfragen.
- CORS_ORIGINS enthält exakte externe Preview-Origin und deren intern umgeschriebene Alias-Origin. Fremde Origin weiter403, kein Wildcard. Andere Domain-Konfiguration benötigt passende env-Werte. Vorschau ausschließlich frontend/.env entnehmen, nicht aus älteren Abschnitten unten.
- Gastgrenzen: atomare MongoDB-Stunden-Zähler pro beobachtetem Peer UND global; geteilter Ingress nicht als einzelner Kunde behandelt; keine Übernahme frei manipulierbarer X-Forwarded-For-Werte. Refresh zählt nicht als Gastneuanlage.

### Verifiziert — 2026-10-04
- Testbericht `/app/test_reports/iteration_13.json`: 32 aktive Backendtests bestanden, 1 veralteter realer Gemini-Test bewusst übersprungen. Tests prüfen entfernte APIs explizit auf404. Kein generativer Aufruf im neuen Testumfang.
- Echte u2netp-Freistellung: Transparenzvarianz, privater Abruf, Cache-Wiederverwendung und unverändertes Original bestanden. Strikte Ebenen-Validierung, Fonts, Grenzen, Eigentümerschutz, Speicherung, Warenkorb/Checkout ebenfalls bestanden.
- Frontend: Mehrfachtexte, Upload, Zuschnitt, Freistellen/Original wiederherstellen, Sperren/Entsperren, Duplizieren, Sichtbarkeit, Speichern und kompletter Testabschluss bestanden. Responsive320/768/1024/1440 ohne horizontales Überlaufen.
- Nach Testbericht behoben: Adminliste übernimmt den bestätigten Rohling direkt aus der Mutation, alte Listenanfragen können sie nicht überschreiben. Gastlimit vorher40/sharedPeer auf konfigurierbare atomare Peer-/Globallimits umgestellt.
- Vollständiger Backend-Nachtest nach Korrekturen: erneut32 bestanden/1 historischerTest übersprungen. Produktionsbuild erfolgreich, keine Compilewarnungen, `/app/test_reports/layers-build.log`.
- Gezielter Browser-Nachtest: frischer Gast ohne429-Blockade; Rohlingfoto hochgeladen, neu angelegt, archiviert, reaktiviert, Status sofort korrekt, nach Reload persistent, erneut archiviert. Letzter temporärer Testrohling anschließend exakt per ID entfernt, vier aktive Musterrohlinge übrig.
- Eigener Abschlussbericht `/app/test_reports/layers_final_verification.json`; keine bekannten offenen Blocker im beauftragten Studio-Umfang.

### Nächste Aufgaben / Prioritäten
- P0 im beauftragten Funktionsumfang: keine bekannten offenen Fehler. Nutzer soll mit echten Fotos und überlagernden Texten ausprobieren.
- P1 Inhalt/Betrieb: echte Rohlingfotos und genaue Gravurgrenzen einpflegen; rechtliche Betreiber-/Hosting-/Löschinformationen finalisieren (siehe rechtlicher Backlog). Bestehender Anfrageprozess braucht reale Bearbeitung, kein automatischer E-Mail-Versand.
- P2 optional: manueller Kantenpinsel zur Korrektur schwieriger Freistellungen; Verwaltungsansicht für Kontaktanfragen/Testbestellungen; echte Zahlungen nur nach separater Beauftragung. KI-Beratung/-Bildgenerierung NICHT wieder einplanen.

## Originale Aufgabenstellung
„Kannst du basierend auf diesem Mockup eine schöne One-Page-Webseite machen mit schönen dezenten Animationen. Die weiteren Bilder, die du auf dem Bild siehst, die werde ich dir noch mitgeben. Und im Hero soll so ein Effekt sein, dazu gebe ich dir aber auch noch mal drei, vier separate Bilder, ähm, wo wenn man so scrollt, sich so ein bisschen so dieser Parallax-Effekt beziehungsweise so perspektivischer Effekt reinkommt.“

Der Nutzer stellte ein vollständiges ManuCreator-Mockup bereit und bat: „Start the task now“.

## Explizite Entscheidungen des Nutzers
- „Starte mit passenden vorläufigen Bildern; die Originale liefere ich später“
- „Ein Kontaktformular, das Anfragen auf der Webseite speichert“
- Deutschsprachige One-Page nahe der bereitgestellten visuellen Vorlage. Keine zusätzliche Rückfrage erforderlich.
- Aktuell: geliefertes Video als Hero-Hintergrund nutzen; Scrollen abwärts steuert die Bilder vorwärts, aufwärts rückwärts. Kein zeitgesteuertes Autoplay.
- Nach Fehlermeldung des Nutzers wird derselbe Effekt mit echten extrahierten Video-Einzelbildern statt browserabhängigem Video-Seeking dargestellt. Bewegungsreduktion bleibt standardmäßig respektiert, kann ausdrücklich im Hero übersteuert werden.
- Neueste Klarstellung: Die Seite muss ab dem ersten Scrollschritt normal mitscrollen. Der Hero darf NICHT festgehalten werden und darf keine zusätzliche Scrollstrecke für das Video erzeugen. Frames bewegen sich nur begleitend zum normalen Scrollen.
- Betreiber: Manuel Bayer, ManuCreator, Büttgerwald 16, 47877 Willich, info@manucreator.de. Einzelunternehmer ohne Handelsregistereintrag; Kleinunternehmer nach § 19 UStG. Privat- und Geschäftskunden, personalisierte und Standardwaren sowie kundeneigene Gegenstände. Vertrag erst durch ausdrückliche Auftragsbestätigung; Vorkasse/Überweisung und PayPal als außerwebsitebezogene Zahlungsarten.

## Nutzergruppen
- Privatpersonen auf der Suche nach individuellen Geschenken und Einzelstücken.
- Unternehmen und Vereine mit Bedarf an gravierten Kleinserien und bedruckten Textilien.
- Betreiber von ManuCreator als Empfänger gespeicherter Projektanfragen.

## Kernanforderungen (statisch)
1. Dunkler fotografischer Hero mit Original-Logo, Headline und Anfrage-/Beispiel-Buttons.
2. Dezente Scroll- und perspektivische Animation; Bewegungsreduktion berücksichtigen.
3. Sechs Leistungsbereiche: Holz, Kunststoff, Glas, Metall, Schiefer, Textildruck.
4. Drei Schritte: Idee teilen, Angebot erhalten, Umsetzung.
5. Kontaktabschluss und Footer; mobile Darstellung ohne horizontales Scrollen.
6. Kontaktformular mit realer Speicherung und nachvollziehbarer Bestätigung.
7. Originalbilder und separate Hero-Ebenen später austauschen bzw. ergänzen.

## Architekturentscheidungen
- React + vorhandene Shadcn/Radix-Komponenten; Framer Motion für Scroll-Parallax und einmalige Abschnitts-Reveals.
- FastAPI mit `POST /api/inquiries` und `GET /api/health`.
- MongoDB aus bestehenden `MONGO_URL`-/`DB_NAME`-Werten, Collection `inquiries`.
- API-URL ausschließlich aus `REACT_APP_BACKEND_URL`. Keine Änderungen geschützter Umgebungswerte.
- Ursprüngliche One-Page ohne Login; inzwischen geschützte Rohlingverwaltung und privater Studioupload vorhanden (siehe aktuellen Stand oben). Weiterhin kein automatischer E-Mail-Versand. Anfragen werden tatsächlich gespeichert, keine gemockte API.
- Keine öffentliche Liste oder Abrufmöglichkeit für personenbezogene Anfragedaten.
- Pydantic validiert UUID, Name, E-Mail, Material, Stückzahl, Nachricht und Honeypot. Einmalige Request-ID verhindert doppelte Speicherung bei Retry. Seit Rechtsanpassung ist keine gesonderte Einwilligung für die vorvertragliche Anfrage erforderlich; alte `consent`-Felder werden optional akzeptiert, aber nicht als neue Einwilligung gespeichert.
- `created_at` ist der Eingang als UTC-ISO-Zeitstempel, Status initial `new`; neue Anfragen enthalten `privacy_notice_version`. Dies ist kein Einwilligungsnachweis. Alte Bestandsdaten wurden nicht nachträglich verändert.
- Statische Bilder unter `frontend/public/images/`, Materialdaten zentral unter `src/data/services.js`.
- Vom Nutzer bereitgestellte Vorlage ist Designgrundlage, deshalb kein eigener Design-Agent benötigt. Palette Anthrazit, gebrochenes Weiß, warmer heller CTA-Akzent; lokal gehostete variable Schrift Manrope.
- Stockbilder waren nicht passend zur Materialdarstellung. Vorläufige Produktmotive wurden generiert. Original-Logo aus der vom Nutzer bereitgestellten Mockup-Bilddatei extrahiert.
- Kontakt-, Material-, Beispiel- und Über-mich-Ansichten als zugängliche Dialoge. Rechtstexte seit neuestem als eigene direkt verlinkbare, druckbare React-Router-Seiten `/impressum`, `/agb`, `/datenschutz`, `/widerruf`.

## Implementiert — 2026-10-02
- Vollständige responsive One-Page entsprechend dem Mockup.
- Sticky Header mit mobil aufklappbarer Navigation, Ankern, Tastaturbedienung und Skip-Link.
- Fotografischer Hero mit Scroll-Verschiebung, Skalierung und dezenter perspektivischer Neigung. Für echte voneinander unabhängige Produktebenen fehlen noch die angekündigten Bilddateien.
- Sechs interaktive Materialkacheln, Materialdetails, Beispielgalerie, Über-mich-Ansicht und passend vorausgewähltes Anfragematerial.
- Ablaufsektion, bildbasierter Anfrageabschluss und Footer.
- Kontaktformular mit Name, E-Mail, Material, Mengen-Stepper, Nachricht und Einwilligung; deutsche Fehlermeldungen, Ladezustand, Netzwerkfehlerbehandlung und Bestätigung mit Referenz.
- Reale MongoDB-Speicherung, Eingabevalidierung, Honeypot und idempotente Wiederholungen.
- `prefers-reduced-motion`, lokale Schriftdatei, deutsche Metadaten, beschreibende Test-IDs.
- Impressum/Datenschutz öffnen transparente Informationsdialoge; vollständige rechtliche Texte sind mangels Betreiberangaben noch nicht vorhanden.

## Verifiziert — 2026-10-02
- Testing-Agent: 13/13 Backendtests bestanden, einschließlich echter MongoDB-Persistenz, Idempotenz, Validierung und fehlender öffentlicher Anfrage-Liste.
- Frontend: erfolgreiche Übermittlung und Wiederholung nach simulierter Netzstörung, alle sechs Materialzuordnungen, Galerie, Über-mich, Ankernavigation, Parallax und Reduced Motion.
- Responsives Layout vom Testing-Agent bei 390, 360 und 768 Pixeln ohne horizontales Overflow geprüft.
- Vom Testing-Agent gemeldete Probleme behoben: browserabhängige Einwilligungs-Validierung durch deutsche Formularvalidierung ersetzt; blockierende Radix-Exit-Animation entfernt; nicht-statischen Scrollcontainer für Motion eingerichtet.
- Abschließender Browsercheck: Einwilligungsfehler deutsch, unmittelbare Wechsel Kontakt → Über mich → Beispiele → Leistungsanker erfolgreich, Kontakt/Footer erreichbar, Reduced Motion ohne Hero-Transform. Scrollcontainer-Warnung nicht mehr in Console vorhanden.
- Produktionsbuild erfolgreich (`/app/test_reports/build.log`).
- Berichte: `/app/test_reports/iteration_1.json`, `/app/test_reports/pytest/pytest_results.xml`, `/app/test_reports/fix_verification.json`.
- Testdaten wurden bereinigt. Keine Benutzerkonten oder Zugangsdaten angelegt.

## Priorisierter Backlog
### P0 — Nutzerangaben erforderlich
- Geschäftliche Telefonnummer für vollständige Fernabsatzinformationen und Widerrufsmuster erhalten. Ggf. bereits zugeteilte USt-ID/Wirtschafts-ID erfragen, nicht persönliche Steuernummer veröffentlichen.
- Rechtstext-Entwürfe anwaltlich prüfen; Annahmen zur Nichtteilnahme an Schlichtung und vom Kunden getragenen Widerrufs-Rücksendekosten bestätigen.
- Konkrete Hosting-/Datenbank-/E-Mail-Anbieter, Vertrags- und Datenregionen, Protokoll-/Aufbewahrungsfristen, AV-Verträge und Löschkonzept final bestätigen. Öffentliches DPA ist recherchiert, konkrete Kontokonfiguration nicht geprüft.
- Verlässlichen Prozess zur Bearbeitung gespeicherter Anfragen sicherstellen: weiterhin KEINE automatische E-Mail-Weiterleitung vorhanden.
### P1 — Vom Nutzer angekündigt
- Noch ausstehende Originalbilder für Holzgravuren und Kunststoffgravuren einbauen, sobald hochgeladen. Glas, Metall, Schiefer, Textildruck und Kontaktmotiv sind bereits ersetzt.
- Ursprünglich angekündigte separate Hero-Ebenen sind durch den später gewünschten, gelieferten Scroll-Video-Hero ersetzt; keine weiteren Hero-Bilder für den aktuellen Effekt erforderlich.
### P2 — Optionale sichtbare Erweiterungen
- Wunschtext-Gravurvorschau ist inzwischen als vollständiger Ebeneneditor umgesetzt; optional später manueller Kantenpinsel für Freistellungen.
- Optional später eine geschützte Anfrageverwaltung, nur nach ausdrücklicher Beauftragung; vor Auth-Code zwingend Integrations-Playbook einholen.
- Weitere Referenzbilder insbesondere für Kunststoff, Schiefer und Textilien ergänzen, sobald der Nutzer zusätzliche Motive bereitstellt; die Kategorie-Slideshow ist bereits implementiert.

## Nächste Aufgaben
1. Weitere Originalbilder für Holz/Kunststoff vom Nutzer entgegennehmen.
2. Fehlende Telefonnummer und Betriebsdetails ergänzen; Rechtstext-Entwürfe nach fachlicher Prüfung freigeben.
3. Aktuellen Ebeneneditor mit echten Rohlingen ausprobieren und bei Bedarf Freistell-Kantenkorrektur ergänzen.

## Bildaktualisierung — 2026-10-02
Nutzerauftrag: „Kannst du diese Bilder schon einmal verwenden“, mit fünf angehängten Produktbildern.

### Eingebaut
- Whiskyglas mit Hirsch-/Good-Times-Gravur → Glasgravuren, Galerie und Materialdetail.
- Built-Different-Metallschild mit Bergmotiv → Metallgravuren, Galerie und Materialdetail; Alt-Text an Schild statt bisherigen Anhänger angepasst.
- Schieferherz „Schön, dass es dich gibt“ → Schiefergravuren, Galerie und Materialdetail.
- Schwarzes ManuCreator-Shirt „Good Ideas Wear Better“ → Textildruck, Galerie und Materialdetail.
- Holzblock „Make it Real“ → Kontaktbereich; mobil vollständiges Foto unter Text und Anfragebutton.
- Hero sowie Holz- und Kunststoffmaterialbilder bewusst unverändert; dafür wurden noch keine passenden Originale geliefert.

### Dateien und Bildschutz
- Originale unverändert unter `/app/assets/originals/` gesichert.
- Optimierte, neu benannte WebP-Versionen unter `/app/frontend/public/images/{glas,metall,schiefer,textil,contact}-original.webp`, jeweils 1448 × 1086 Pixel; ca. 230–327 KB statt bis zu 3,4 MB.
- Glasquelle: `9FF0AF24-0CE0-41F3-A52F-69272BC01C6F.png`.
- Metallquelle: `52DDA854-73D3-4269-90F4-528BD8D384D8.png`.
- Schieferquelle: `5575EB9B-E2FA-4509-83F2-B002EB25258D.png`.
- Textilquelle: `2B785094-465D-4524-B6BB-1A67EB25785C.png`.
- Kontaktquelle: `7CF32BA0-337D-4DCB-9E9D-AEF8EF6ADD82.webp`.
- Bilddaten zentral in `src/data/services.js`; gezielte responsive Bildregeln in `src/styles/product-images.css`.
- Gelieferte Produktbilder in Detailansichten und Galerie mit `contain`, mobil natürliche 4:3-Darstellung der Materialbilder, damit Produktkanten und Schriftzüge nicht abgeschnitten werden.

### Verifizierung
- Desktop-Browserprüfung bei 1920 × 800: vier Originalmotive in Galerie geladen, Metallschild vollständig, Materialübergabe an Anfrageformular korrekt, Kontaktfoto korrekt.
- Gezielter Frontend-Test bei 390 × 844, 360 × 800 und 768 × 1024: 100 % bestanden, kein horizontales Overflow, keine Bild-/Textüberlagerungen, Detail-CTAs und Materialvorauswahl weiterhin funktional.
- Bericht: `/app/test_reports/iteration_2.json`; mobile Screenshots unter `/app/test_reports/artifacts/iteration_2/`.
- Keine Backendänderungen, keine neuen Integrationen oder Konten, keine offenen Fehler aus dieser Bildaktualisierung.

## Scroll-Video-Hero — 2026-10-02
Nutzerauftrag: „Kannst du dieses Video für den Hero Hintergrund benutzen (animiertes Video des Bilds) und mit dem runterschicken bzw hochscrollen soll das Video quasi Frame für Frame abgespielt werden um diesen Motion Effekt zu haben“.

### Umsetzung
- Geliefertes Video ersetzt das bisherige statische Hero-Bild und dessen zusätzliche CSS-Perspektivbewegung.
- Original erhalten unter `/app/assets/originals/hero-motion-original.mp4`; tatsächliche Metadaten: 736 × 400, 24 fps, 241 Frames, 10,041667 Sekunden (automatische Videoanalyse schätzte fälschlich 8 Sekunden).
- Scrolloptimierte Exporte: `/media/hero-scroll.mp4` (H.264, ca. 6 MB, faststart) sowie `/media/hero-scroll.webm` (VP9, ca. 10,6 MB) als native Browser-Alternative. Beide ohne Audiospur, jeder Frame als Keyframe.
- Passendes Standbild aus Originalframe 0: `/images/hero-video-poster.webp`.
- `ScrollVideo.jsx` und `useScrollVideo.js` halten das Video dauerhaft pausiert und setzen `currentTime` anhand des auf 24 fps quantisierten Scrollfortschritts. RAF fasst Ereignisse zusammen; nach laufendem Seek wird immer die aktuellste Sollposition übernommen.
- Kein Autoplay, kein Loop, keine sichtbaren Playercontrols. `muted`, `playsInline`, deaktiviertes Picture-in-Picture. HTML-Video dekodiert die Originalframes; keine simulierten Hintergrundanimationen.
- Framer-Motion `useScroll` auf äußerem Hero-Abschnitt mit `start start`/`end end`; CSS-Sticky hält den Hero während der Sequenz sichtbar, danach setzt sich normales Seitenscrollen fort.
- Responsive Layout in `src/styles/hero-video.css`: Desktop mit Hintergrundbild rechts; Tablet-Hochformat und Smartphone trennen Text/Buttons klar von der kompletten Produktansicht. Native Touch-/Ankerscrollnavigation bleibt erhalten.
- `prefers-reduced-motion`: nur Standbild, kein Video-Download, kein verlängerter Sticky-Bereich.
- Quellenfehler (letztes Source-Element), Medienfehler und 15-Sekunden-Ladezeitlimit führen zum Standbild und entfernen den verlängerten Scrollbereich; kein dauerhaft leerer Hero.
- Vorhandene Kontakt-, Galerie-, Material- und Navigationsfunktionen unverändert.

### Verifizierung und behobene Probleme
- Desktop mit 0/25/50/100 % Scrollfortschritt → ca. 0/2,5/5/10 Sekunden getestet. Rückwärtsscrollen und schnelle Richtungswechsel funktionieren; ohne Scrollen bleibt das Bild stehen.
- Tatsächlich wechselnde dekodierte Frames vom Testing-Agent über Canvas-Pixel-Hashes bestätigt (Canvas nur im Test, nicht in der App).
- Vorschau-Testbrowser unterstützt H.264 nicht, deshalb WebM-Fallback zusätzlich eingebaut und erfolgreich geprüft; normale Browser können MP4 auswählen.
- Ersttest fand Quellenfehler ohne Medienfehler-Event und Überlagerungen bei 768 × 1024 / 320 × 568. Explizites Fehlerhandling und passende Layoutregeln beheben diese.
- Gezielter Nachtest 100 % erfolgreich: 768 × 1024, 320 × 568, 390 × 844, gesperrte beide Videoquellen, Rückwärtslauf und Standbild. Erster Test zusätzlich 360 × 800, Reload/Resize-Synchronisierung, Anker und Dialoge sowie Reduced Motion erfolgreich.
- Berichte: `/app/test_reports/iteration_3.json`, `/app/test_reports/iteration_4.json`; Screenshots in `/app/test_reports/artifacts/iteration_4/`.
- Produktionsbuild erfolgreich: `/app/test_reports/hero-video-build.log`.
- Keine offenen Fehler im getesteten Umfang; keine Backend-/Umgebungsänderungen oder neuen Integrationen.

## Fehlerbehebung Scroll-Effekt — 2026-10-02
Nutzer meldete: „Irgendwie funktioniert der Video scroll Effekt nicht“.

### Untersuchung
- Bisheriges Video-Seeking ließ sich im Chromium-Test bewegen, der genaue Auslöser auf dem nicht angegebenen Nutzergerät konnte nicht unmittelbar reproduziert werden.
- Nachweisbarer stiller Standbild-Fall: aktivierte Systemeinstellung `prefers-reduced-motion`, bislang ohne manuelle Einschaltmöglichkeit. Außerdem hing die alte Lösung von Videoformat-Unterstützung, pausierter Videodekodierung und einem 15-Sekunden-Ladetimeout ab.
- Deshalb keine Behauptung eines bestätigten spezifischen Browserfehlers auf dem Nutzergerät; stattdessen Abhängigkeit vom nativen Videoplayer vollständig entfernt.

### Aktuelle Implementierung (ersetzt vorheriges Video-Seeking)
- Alle 241 Originalframes bei 24 fps aus dem gelieferten Video extrahiert, Motiv und Bewegung unverändert.
- 31 WebP-Bildtafeln mit jeweils bis zu 8 Einzelbildern (4 × 2). Desktop-Frames 736 × 400, mobile Frames 552 × 300; unter `/media/hero-sequence/{desktop,mobile}-00.webp` bis `-30.webp`.
- `HeroFrameSequence.jsx` zeichnet den exakt zur Scrollposition passenden Frame in ein Canvas. HTML-Video, Medienfreigaben, Codecs, Audio und Autoplay werden nicht mehr benötigt. Kein Mock-Effekt.
- `useHeroFrames.js` folgt dem vorhandenen Framer-Motion-Scrollfortschritt und zeichnet bei RAF; verspätet geladene Bilder zeichnen automatisch den neuesten Ziel-Frame ohne weiteres Scrollereignis.
- `heroFrames.js`: priorisiert aktuelle Bildtafel, hält komprimierte Bilddaten im Speicher, maximal drei dekodierte Tafeln; Objekt-URLs werden freigegeben, Requests beim Abschalten abgebrochen.
- `frameDownloads.js`: gemeinsame Download-Warteschlange über mehrere Loader-Lebenszyklen, strikt höchstens zwei aktive Downloads; korrigiert beim ersten Stresstest gemeldete erhöhte Parallelität.
- Ein-/Ausschaltknopf im Hero: „Bewegung einschalten/ausschalten“, mobil Play-/Pause-Symbol mit zugänglicher Beschriftung. Bei Bildladefehlern Standbild und „Animation erneut laden“, Wiederherstellung ohne Seitenreload möglich.
- Reduzierte Bewegung: initial keine Canvas-/Frame-Anfragen und keine Sticky-Zusatzstrecke. Explizites Einschalten aktiviert den Effekt trotzdem; dafür störende pauschale Reduced-Motion-CSS-Regeln entfernt.
- Vorherige `ScrollVideo.jsx` und `useScrollVideo.js` entfernt. Originalvideo und ältere Exporte bleiben archiviert, werden aber nicht mehr vom Hero angefragt.

### Prüfung
- Chromium: echte Mausradbewegung, exakte Zuordnung 0/25/50/100 % → Frame 0/60/120/240, Rückwärtslauf, Pixel-Hash-Vergleich, kein schwarzes Bild, kein zeitabhängiges Abspielen.
- Systemeinstellung reduzierte Bewegung einschließlich explizitem Opt-in und wiederholtem Aus-/Einschalten bestanden.
- Gesperrte Bildquellen: Standbild, Wiederholen-Schaltfläche und Wiederherstellung nach Freigabe bestanden.
- Reale Playwright-WebKit-Engine zusätzlich in isolierter Testumgebung installiert (keine Änderung der Anwendungsabhängigkeiten). Desktop 1920 × 800 und Mobilviewport 390 × 844: wechselnde Canvas-Pixel und Frame-Zielwerte, vorwärts/rückwärts, Stillstand bestätigt. Dies ist ein Safari-Engine-Test, kein Test auf einem physischen iPhone.
- Verzögerte Bildanfragen (1200 ms) + schnelle Richtungswechsel + Aus/Ein: maximal zwei aktive Downloads, sauberer Abschluss.
- Responsiv zusätzlich 320 × 568 und 768 × 1024 geprüft; Buttons und Anfrageabläufe erreichbar, kein horizontales Overflow.
- Berichte: `/app/test_reports/iteration_5.json` (initialer Parallelitätsbefund), `/app/test_reports/iteration_6.json` (behoben, Nachtest bestanden), strukturierte WebKit-Messwerte und Screenshots unter `/app/test_reports/artifacts/iteration_6/`.
- Wiederholbarer Engine-Test: `/app/.browser-testing/bin/python /app/tests/webkit_smoke.py`; isolierte Testumgebung via `.gitignore` ausgeschlossen.
- Build erfolgreich: `/app/test_reports/hero-frames-build.log`.
- Keine noch offenen Fehler im geprüften Umfang. Falls die Nutzerumgebung weiterhin betroffen ist, konkreten Browser/Gerät und Vorschauzustand erfragen, statt dieselbe Chromium-Prüfung zu wiederholen.

## Normales Seitenscrollen mit begleitender Hero-Bewegung — 2026-10-02
Nutzerpräzisierung: „Die Seite soll aber trotzdem schon scrollen also nicht erst wenn das Video durchgescrollt ist?!“.

- Frühere Sticky-/Pin-Entscheidung ausdrücklich aufgehoben. Der Hero bleibt vollständig im normalen Dokumentfluss (`position: relative`, `top: 0`). Nur der bereits bestehende Navigationsheader bleibt wie zuvor sticky/fixed.
- Äußere Hero-Höhe entspricht genau der sichtbaren Hero-Höhe; `--scrub-distance` und die zusätzliche Videostrecke entfernt, auch mobil. Leistungen folgen unmittelbar auf den Hero.
- Scrollfortschritt für die Frames jetzt von `start start` bis `end start`: Frames laufen vorwärts, während der Hero nach oben aus dem Bildschirm scrollt; beim Zurückscrollen rückwärts. Kein Warten auf das Videoende.
- Ein-/Ausschalten des Effekts verändert die Dokumenthöhe nicht mehr. Bestehende Frame-Ladelogik, Mobiloptimierung, Bewegungsreduktion und Wiederholen-Funktion unverändert.
- Desktop-Messung: nach 200 px Scrollen Hero bei −200 px, Leistungen bei 600 px sichtbar, Videoframe 60. Nach 400 px Frame 120, Rückwärtsbewegung auf 150 px ergibt Frame 45.
- Gezielter Testing-Agent-Nachtest: normale Bewegung, fehlende Zusatzstrecke, Frame-Vorwärts/Rückwärtslauf, stabiler Seitenumfang beim Umschalten und Leistungen-Anker bestanden. Desktop, Mobilviewport 390 × 844 und echte WebKit-Engine geprüft.
- Bericht: `/app/test_reports/iteration_7.json`; wiederholbarer Test `/app/tests/webkit_quick_hero_scroll.py`; Messwerte `/app/test_reports/artifacts/iteration_7/webkit_quick_results.json`.
- Keine offenen Fehler dieses Änderungsumfangs. Keine Backend-, Integrations- oder weiteren Designänderungen.

## Impressum, AGB und rechtliche Grundlagen — 2026-10-02
Originalauftrag: „Impresssum Manuel Bayer Büttgerwald 16 47877 Willich info@manucreator.de Erzeuge auch eine sinnvolle AGB und was mich rechtlich wichtig ist“.

Klärung durch Nutzer: „1a, 2a, 3b, 4a,c,d,e,f Paypal“ = Einzelunternehmer ohne Handelsregister, Kleinunternehmer §19 UStG, ausdrückliche Auftragsbestätigung als Vertragsschluss, Privat-/Geschäftskunden, personalisierte/Standardwaren und kundeneigene Gegenstände, Überweisung/Vorkasse und PayPal.

### Implementiert
- Anbieterkennzeichnung mit den tatsächlichen Nutzerangaben auf `/impressum`, keine erfundenen Register-/Steuer-/Telefonangaben.
- Individueller AGB-Entwurf `/agb`: klare unverbindliche Anfrage und Vertrag erst durch ausdrückliche Auftragsbestätigung; Gestaltung/Freigaben, Kundengegenstände, Motivrechte, Kleinunternehmerpreise, Vorkasse/PayPal, Lieferung, Verbraucherwiderruf, Werkvertragsrechte, Mängelrechte, ausgewogene Haftung und keine Zwangs-Gerichtsstandsklausel für Verbraucher.
- Datenschutz-Entwurf `/datenschutz` anhand tatsächlicher Datenflüsse, Betreiber, Anfrage-DB, lokal ausgelieferter Schrift/Medien, PayPal nur bei separat vereinbarter Zahlung, Betroffenenrechte/LDI NRW. Hostingdaten und Drittlandsbezug aus offiziellem DPA übernommen, konkrete Betriebsdetails ausdrücklich noch offen.
- Widerrufs-Entwurf `/widerruf`: getrennte Abschnitte für Standardwaren und Dienst-/Bearbeitungsleistungen; personalisierte Waren nur bei gesetzlichen Voraussetzungen ausgenommen. Keine pauschale Ausnahme für mitgebrachte Gegenstände; kein Erlöschen bei bloßem Arbeitsbeginn. Freiwilliges Musterformular mit Download.
- Alle Rechtsseiten mit direkter URL, Titel, Inhaltsnavigation, Druck-/PDF-Funktion und Volltextdownload; Footerlinks, Rückkehr zur Startseite, mobile Lesbarkeit.
- Alle Rechtstexte sichtbar als nicht abschließend geprüfte Entwürfe markiert. Fehlende Telefonnummer im Impressum/Widerruf ausdrücklich genannt. Keine Garantie der Rechtskonformität.
- Betreiber-Checkliste unter `/downloads/ManuCreator-Rechtliche-Checkliste.txt`: AGB-Einbeziehung vor verbindlicher Kundenerklärung, Vertragsunterlagen, vollständige Verbraucherinformationen, vorzeitiger Leistungsbeginn, Widerrufsfunktion bei späterem Onlinevertrag, Datenschutz-/Löschprozesse, PayPal-Gewerbenutzung, Rechnungen, GPSR, Lebensmittelkontakt, Textilkennzeichnung, VerpackG/LUCID, Kammer-/Gewerberecht, Haftpflicht, Nutzungsrechte und BFSG-Prüfung.
- Kein Online-Bestell-/Zahlungs-/Vertragsabschluss implementiert. PayPal ist rechtlich beschriebene externe Zahlungsoption, keine neue Integration. Download/Mailkontakt wird nicht als gesetzliche elektronische Widerrufsfunktion ausgegeben.

### Datenschutzbezogene technische Anpassungen
- Explizite PostHog-/Session-Recording-Einbindung und `emergent-main.js` aus `frontend/public/index.html` entfernt. Keine neuen Analyse-/Cookie-Dienste hinzugefügt. Keine pauschale Behauptung völliger Infrastruktur-Cookie-Freiheit.
- Obligatorische Einwilligungscheckbox im Anfrageformular entfernt; stattdessen vor Absenden transparenter Datenschutzhinweis mit Link in neuem Tab, Verantwortlichem und Rechtsgrundlage für vorvertragliche Bearbeitung. Ausdrücklicher Hinweis: keine Bestellung, Vertrag erst mit Auftragsbestätigung.
- Backend benötigt keine Einwilligung mehr. Kompatibilitätsfeld `consent` optional und ausgeschlossen von neuer Speicherung; `privacy_notice_version='2026-10-02'` wird festgehalten. Historische Datensätze unverändert. Kein automatischer E-Mail-Versand hinzugefügt.

### Wichtige juristische Grenzen/noch offene Angaben
- Geschäftliche Telefonnummer noch nicht geliefert; gesetzliche Fernabsatzinformationen/Muster daher noch nicht vollständig. Vor verbindlichen Verbraucheraufträgen ergänzen.
- Nichtteilnahme an Verbraucherschlichtung und unmittelbare Rücksendekosten beim Kunden sind gewählte Entwurfsannahmen, vom Betreiber zu bestätigen.
- Keine persönliche Steuernummer veröffentlicht; vorhandene USt-ID/W-ID trotz Kleinunternehmerstatus ggf. nachtragen.
- Öffentliches Hosting-DPA nennt Emergent Labs Inc., 2380 Via Espada, Pleasanton, CA 94566, USA; mögliche Verarbeitungsorte USA/EU/Indien, SCC als vorgesehenes Transferinstrument. Keine nicht geprüfte EU-only-Zusage, kein unbelegter Nachweis konkreter Kontoeinstellungen oder tatsächlicher Log-Aufbewahrungsfristen.
- Konkreter E-Mail-Anbieter und Löschkonzept noch offen. Anwendung löscht Anfragen nicht automatisch. Checkliste weist auf manuelle organisatorische Umsetzung und fehlende automatische Betreiberbenachrichtigung hin.
- AGB-Veröffentlichung allein bezieht sie nicht wirksam ein. Texte vor verbindlicher Kundenerklärung bereitstellen und passende Widerrufsbelehrung mit Telefonnummer auf dauerhaftem Datenträger übermitteln.
- §356a BGB seit 19.06.2026: Pflicht bei Vertragsschluss über Onlineoberfläche prüfen. Derzeit echtes unverbindliches Anfrageformular; bei späterer Bestellung/Annahme-/Zahlungsänderung neu bewerten. Kein vorgetäuschter Widerrufsbutton ohne Eingangsbestätigung.
- Offizielle Quellen aus §5 DDG, §§312g/356/356a BGB, Artikel246a EGBGB und Anlage1 recherchiert. Aktuelle amtliche §356-Struktur verwendet (Dienstleistungserlöschen inzwischen Absatz5). EU-OS-Plattform seit20.07.2025 eingestellt: kein veralteter Pflichtlink eingebaut.
- Neue harmonisierte Gewährleistungsmitteilung nach EU2025/1960 / aktuellem Artikel246a EGBGB in Betreiber-Checkliste für konkrete Angebote/Vertragsschluss berücksichtigt; keine unbelegte Behauptung, ein AGB-Satz erfülle alle Kennzeichnungspflichten.

### Verifiziert
- 15/15 Backendtests: ohne Consent erfolgreich, alte true/false/fehlende Consentwerte akzeptiert und nicht gespeichert, Pflichtfelder weiter validiert, Mongo-Persistenz, Idempotenz, keine öffentliche Anfrageliste.
- Frontend: vier direkte Routen inklusive Reload/Titel, Footer/Tabs/TOC/Mail/Zurück, Downloads/Volltext/Widerrufsformular, Druckansicht, 390-/360-Pixel-Layout ohne Overflow, Browserformular ohne Checkbox und Datenschutzlink, Hero weiterhin ohne Pinning.
- Explizite Telemetrie-Snippets in Source/Build fehlen; in getesteten Abläufen keine Anfragen an PostHog/ap.emergent.sh/emergent-main.js beobachtet.
- Testdaten bereinigt; Bericht `/app/test_reports/iteration_8.json`; Build `/app/test_reports/legal-build.log` erfolgreich.
- Keine technischen Fehler im geprüften Umfang. Rechtsprüfung wurde NICHT durch Funktionstests ersetzt.

## Kategorie-Referenzen und Slideshow — 2026-10-02
Originalauftrag: „Kannst du die Bilder noch in die entsprechenden Kategorien einordnen? Also wenn jemand auf 'ne bestimmte Kategorie klickt, dass der dort dann, wenn sich dieser, äh, Popup-Dialog oder was das ist, öffnet, beziehungsweise die Detailseite zu dem entsprechenden, zu Kategorie, dass der da so 'ne Slideshow hat. Dass der dann da so 'ne Slideshow hat, wo dann noch andere, ja, Referenzen sichtbar werden“.

### Nutzerentscheidungen
- Das transparente Praxisschild besteht ausdrücklich aus Glas und gehört zu Glasgravuren, NICHT Kunststoff/Acryl.
- Bei der Slideshow wurden beide Optionen ausgewählt: „Zusätzlich automatisch, mit einer Pause-Taste; Nur durch Klicken oder Wischen“. Umgesetzt als kombinierte Automatik plus jederzeitige manuelle Bedienung; manuelle Bedienung stoppt die Automatik bis zum erneuten Einschalten.

### Bilderzuordnung
- `IMG_6072.webp` → Metall: zylindrisches Bauteil mit QR-Code und Seriennummer, `/images/references/metall-bauteil.webp`.
- `IMG_6071.webp` → Metall: Hundemarke „Luna“, `/images/references/metall-hundemarke.webp`.
- `IMG_6070.webp` → Glas: Zahnarzt-Praxisschild „Dr. Klein“, `/images/references/glas-praxisschild.webp`.
- `IMG_6069.webp` → Glas: Familienporträt in Kristallglas, `/images/references/glas-familienportrait.webp`.
- Gelieferte Originale unverändert unter `/app/assets/originals/` gespeichert. Web-Versionen 1600 × 1070, ca. 109–259 KB; zusätzliche kleine Vorschaubilder lokal unter `/images/references/`.
- Glas: 3 Motive (bisheriges Whiskyglas + Praxisschild + Familienporträt).
- Metall: 3 Motive (bisheriges Schild + Bauteil + Hundemarke).
- Holz: 2 Motive (bisheriges Lebensbaum-Brett + bereits gelieferter „Make it Real“-Holzblock).
- Kunststoff, Schiefer, Textil: je 1 vorhandenes Motiv; keine erfundenen oder duplizierten Füllbilder.

### Umsetzung
- Bestehende Kategorie-Popups auf Slideshow umgestellt; Zugang sowohl über Leistungskacheln als auch Beispielübersicht.
- Bilder bleiben vollständig sichtbar (`object-fit: contain`), mit stabiler 3:2-Bühne, individuellen Beschreibungen, Motivzählung und Vorschaubildern. Startseitenkacheln und Hero unverändert.
- Bewährte vorhandene Shadcn-/Embla-Carousel-Komponente für Touch-/Drag-Gesten und umlaufendes Blättern genutzt; keine neue externe Integration oder Bibliothek.
- Automatischer Wechsel alle 5 Sekunden; Play/Pause, Zurück/Weiter, direkte Thumbnail-Auswahl und Tastatur (Links/Rechts, Pos1/Ende).
- Manuelles Blättern, Ziehen/Wischen und Tastaturfokus im Carousel stoppen die Automatik; Play erlaubt explizites Fortsetzen. Maus-Hover pausiert vorübergehend. Ein-Bild-Kategorien zeigen keine sinnlosen Navigations-/Autoplay-Steuerungen.
- Reduzierte Bewegung startet ohne Autoplay. Explizites Einschalten erlaubt Bildwechsel ohne erzwungene Tween-Animation.
- Bei Schließen, Kategorie-Wechsel oder Anfrageübergang werden Timer/Listener entfernt. Neuer Kategorieaufruf beginnt beim ersten Motiv.
- Sichtbarkeitswechsel, Fenster-Fokusverlust und Pagehide pausieren die Automatik sofort. Rückkehr startet ein frisches Intervall; zusätzliche synchrone Prüfung im Timer verhindert Weiterlaufen im Hintergrund.
- Bildladefehler: lesbare Fehlermeldung und erneutes Laden statt leerer/kaputter Bildfläche.
- Bestehende Anfrage übernimmt weiterhin die ausgewählte Materialkategorie; keine Backend-, Zahlungs-, Rechts- oder Hero-Änderungen.

### Dateien
- Zentrale Referenzzuordnung: `frontend/src/data/serviceReferences.js`.
- Anzeige: `components/site/ReferenceSlideshow.jsx`, `ReferenceImage.jsx`; Einbindung in `ContentDialog.jsx`.
- Interaktion/Timer: `hooks/useReferenceSlideshow.js`; Gestaltung: `styles/reference-slideshow.css`.
- Bestehender Carousel-Wrapper ergänzt um fehlendes Entfernen des `reInit`-Listeners beim Unmount.

### Prüfung
- Hauptagent: tatsächlicher automatischer Bildwechsel, Pause über mehr als 5 Sekunden, Praxisschild- und Metallmotive, korrekte Anfragevorauswahl im externen Browser erfolgreich.
- Testing-Agent `/app/test_reports/iteration_9.json`: korrekte Zuordnung/Anzahl, Pfeile, Thumbnails, Tastatur, Fokus/Escape, Wiederöffnen, Einzelbildansicht, reduzierte Bewegung, Fehler/Retry und Anfrageübergang bestanden; 390 × 844, 320 × 568 und 768 × 1024 ohne horizontales Overflow.
- Drag-Geste in mobiler Emulation geprüft; der Testbrowser bot keine echte Touch-API. Keine Behauptung eines Tests auf einem physischen Smartphone.
- Ein Tabwechsel-Test war wegen unklarer Headless-Sichtbarkeit nicht eindeutig. Daraufhin zusätzlich synchrone Timer-Abschaltung bei `blur`/`pagehide`, Aktivitätsgeneration und direkte `document.hidden`/`document.hasFocus()`-Prüfung implementiert.
- Gezielter Browser-Nachtest über kontrollierte Visibility-/Focus-Ereignisse: Hintergrundpause, Wiederaufnahme, zusätzliche Blur-Pause und erneute Focus-Wiederaufnahme jeweils nach 5,5 Sekunden erfolgreich. Ergänzungsbericht `/app/test_reports/reference-slideshow-fix-verification.json` beschreibt die Testgrenzen ausdrücklich.
- Produktionsbuild erfolgreich: `/app/test_reports/reference-slideshow-build.log`.

## Gestaltungsstudio mit KI und Test-Warenkorb — 2026-10-04
Originalauftrag: „Ich benötige für meine Seite eine Art Tool zum personalisieren ähnlich wie auf dem Mockup, wo rein basierend auf den produktrohlingen mittels ki eine Vorschau generiert werden kann um ein personalisiertes Produkt fertigen zu lassen.“

### Explizite Entscheidungen
- Vorerst Musterrohlinge Holzscheibe, Schneidebrett, Glasschild, Metallanhänger; echte ungravierte Produktfotos und Namen folgen vom Nutzer.
- Foto/Logo-Upload, Text/Namen/Datum, Schriftstil und begrenzte Größen-/Positionseinstellungen; Herstellbarkeit und geringe KI-Kosten wichtig.
- Anbieterwahl delegiert; Gemini Nano Banana über das freigegebene Plattform-KI-Guthaben gewählt.
- Bestätigter Ablauf: feste Vorlagen, kostenlose direkte Vorschau, KI nur auf ausdrücklichen Klick, Wiederverwendung und Generierungslimits.
- Abschluss ausdrücklich TESTBESTELLUNGEN mit klaren Musterprodukten/Beispielpreisen und OHNE echte Zahlungen. Keine Änderung zu Live-Zahlungen ohne neue ausdrückliche Beauftragung.

### Implementierte erste Ausbaustufe
- `/gestalten`: Produktwahl links, kostenlose Live-Canvas-Vorschau mittig, vorgegebene Gestaltung rechts, mobil untereinander.
- Vier neutrale Musterfotos generiert; Mustermaße, Gravurflächen und Preise ausdrücklich nicht für tatsächliche Fertigung freigegeben. Bilder unter `frontend/public/images/studio`, identische serverseitige Vorlagen unter `backend/studio/assets`.
- Vorlagen „Nur Text“, „Foto & Text“, „Logo & Text“; Foto nur für Holzrohlinge, Logo/Text auch für Glas/Metall.
- Drei lokal gehostete Nimbus-Schriften, begrenzte Textlängen/Größen, vorgegebene Position oben/Mitte/unten, Bildfokus/Zoom. Canvas und Pillow verwenden dieselben Fonts und Flächenregeln. Server validiert und beschneidet Darstellungen auf die freigegebene Musterfläche.
- ACHTUNG: Flächen stehen aktuell fest in `backend/studio/catalog.py`; noch KEIN Betreibereditor für Rohlinge und noch KEIN freies Drag-and-Drop einzelner Elemente.
- Foto-/Logo-Upload mit Rechtebestätigung, JPG/PNG/WebP, max. 8 MB und 20 Megapixel; EXIF entfernen, ungültige/zu große Bilder ablehnen. SVG nicht zulässig.
- ECHTER Emergent Object Storage für Uploads, gespeicherte Renderings und KI-Ergebnisse; MongoDB speichert nur Metadaten/Referenzen. Private Dateiabrufe ausschließlich nach Gastbesitzprüfung, keine Tokens in Bild-URLs.
- Anonymer JWT-Gastzugang ohne Login-UI: Access 15 Minuten, Refresh 7 Tage mit Rotation, serverseitigem Secret und Mongo-Gültigkeit; lokale Browserpersistenz für Zugang und letzten Entwurf. Keine Admin-/Passwortkonten erstellt.
- Bilder/Drafts/Warenkorb/Bestellungen sind dem Gast zugeordnet. Gastablauf löscht die Bilder nicht automatisch; entsprechend transparenter Datenschutzentwurf, Löschkonzept weiterhin erforderlich.
- Speichern erzeugt serverseitige exakte Direktvorschau und unveränderliche Gestaltungsparameter. SHA256-Fingerprint pro Gast dedupliziert identische normalisierte Designs einschließlich Bildinhalt; keine KI-Aufrufe beim Bearbeiten/Speichern/Warenkorb.
- ECHTE optionale Gemini-Bildgenerierung: `gemini-3.1-flash-image-preview` über `emergentintegrations`, Referenzen Rohling + deterministischer Entwurf. Expliziter Bestätigungsdialog über Datenweitergabe, serverseitig `confirmed=true` erforderlich. KI-Ausgabe ist unverbindliche Anschauung, niemals Produktionsdatei oder Fertigungsfreigabe.
- Jobs werden asynchron bearbeitet und abgefragt; Fehler lassen den exakten Entwurf bestehen. Fertige identische Vorschauen werden ohne neuen Provider-Aufruf wiederverwendet; geänderte Entwürfe markieren die alte Ansicht als veraltet.
- Quoten in `.env`: 2 KI-Aufrufe/Gast/Tag, 4 je serverseitiger Peer-Netzwerkgruppe/Tag, global 8/Tag, 30 Sekunden Abstand. Globale/Netz-/Gastzähler atomar, Cache-Hits verbrauchen nichts, maximal zwei Versuche für fehlgeschlagenen identischen Entwurf, nach Erfolg keine erneute Generierung desselben Fingerprints. Hinter Shared-Ingress kann das konservative Peer-Limit mehrere Besucher gruppieren; keine Behauptung einer verifizierten Endnutzer-IP.
- `/warenkorb`: eigene Entwürfe, private Vorschaubilder, Stückzahl/Entfernen/Wiederöffnen, ausschließlich serverseitige Beispielpreise.
- `/testabschluss`: Beispieldaten-Button, Testbestätigung, null Euro zahlbar, keine Zahlungsdaten/Abwicklung, keine automatische Bestell-E-Mail.
- `/testbestellung/:id`: gespeicherter TEST-Beleg mit unveränderlichem Entwurfssnapshot, Download und Rückkehr. Idempotenz per request_id, keine Fertigung ausgelöst.
- Eigene API-Module unter `backend/studio/`; response_models für Mongo-basierte Draft-/Cart-/Order-Antworten, `_id` ausgeschlossen. Keine Änderung geschützter Backend-/Frontend-URL-/Mongo-Werte.
- Hauptnavigation „Selbst gestalten“ auf Desktop/Mobil. Vorhandene Seite, Slideshow, nicht gepinnter Scroll-Hero und rechtliche Seiten bleiben bestehen.
- Datenschutzentwurf ergänzt um Gastzugang/Local Storage, Uploads/Objektspeicher, ausdrücklich angeforderte Gemini-Verarbeitung, Testbestellungen und tatsächlich fehlende automatische Datenlöschung. Rechtsstand/Notice-Version 2026-10-04.

### Dateien / Integration / Betrieb
- Verifizierte Playbooks für Gemini-Bildbearbeitung, Emergent Object Storage und JWT-Gastzugang vor Implementierung eingeholt. Keine zusätzlichen Nutzer-Accounts oder Zahlungsintegration.
- `studioApi.js` verwaltet Gastzugang/Refresh und autorisierte API-/Blob-Abrufe; Auth-Testhinweise unter `/app/auth_testing.md`, Credential-Hinweise in `/app/memory/test_credentials.md`.
- `studio-base.css` enthält Basisdarstellung, `studio.css` responsive Regeln. Konfigurator-Datenmodelle/Constraints in `catalog.py`, `models.py`, `rendering.py`; nächste Ausbaustufe muss diese serverseitigen Grenzen ausdrücklich erweitern, nicht nur das UI.
- Modell/Storage-Proxy/JWT-Secret/Quoten nur in Backend-Umgebung. In Produktion muss deren Vorhandensein separat sichergestellt werden; in dieser Arbeit kein Deployment angefordert oder durchgeführt.

### Verifiziert
- Testing-Agent `/app/test_reports/iteration_10.json`: 26/26 Backendtests plus Desktop-/Tablet-/Mobilabläufe, Gastisolation, Uploadvalidierung/EXIF, echtes Object Storage, Draft-Deduplizierung, Cart/Testcheckout und Idempotenz.
- Genau EINE echte KI-Generierung im Test ausgeführt und erfolgreich beendet; Ergebnis privat abrufbar. Zweiter Abruf desselben Entwurfs bestätigt Cache-Hit ohne Quotenverbrauch. Echte Verbrauchszähler wurden nicht zurückgesetzt.
- Initialer Gesamtbuild erfolgreich (`/app/test_reports/studio-build.log`); keine blockierenden Testfehler. Optional bemängelter Proxy-Fallback entfernt, jetzt strikte Umgebungsvariable.
- Nachtest nach Persistenzverbesserung: gespeicherter Entwurf bleibt nach Reload inklusive serverseitigem Speicherstatus erhalten; 1920×800-Layout intakt, kein horizontaler Overflow, keine KI-Anfrage ausgelöst.
- Keine weitere KI-Generierung für reine UI-Nachtests beauftragen, sofern vorhandenes Ergebnis wiederverwendbar ist.

## Neuester Nutzerwunsch: mehr Gestaltungsfreiheit bei festen Fertigungsgrenzen — 2026-10-04
Nutzer fragt, wo später die Gravurfläche eingestellt wird, wie Text auf Mobil/Desktop frei verschoben werden kann und ob ein schrittweiser Chat mit Beispielen, Schrift-/Bildstilen und Hintergrundentfernung (ähnlich dem erwähnten XTool-Workflow) sinnvoll wäre, ohne hohe KI-Kosten.

### Gegebene Empfehlung, NOCH NICHT implementiert
- Betreiberverwaltung für echte Rohlinge, Maße, freigegebene Rechteck-/Kreis-/Konturflächen und gesperrte Bereiche; diese technischen Grenzen sollen nicht von Kunden veränderbar sein.
- Kunden können Text und Bild innerhalb dieser Grenzen per Maus/Finger verschieben, skalieren und ausrichten; Einrasten/Hilfslinien, Mindestschriftgrößen, Undo/Reset und Auflösungswarnungen; ohne Bildgenerierung bei normalen Änderungen.
- Geführter Gestaltungsassistent im Chat-Stil mit tatsächlichen Auswahlchips und visuellen Beispielen, nicht als vorgetäuschter LLM-Chat. Standardfragen benötigen keine Sprachmodell-Aufrufe.
- Optionaler Freitext-KI-Chat erst bei ausdrücklicher Wahl: übersetzt Wünsche in begrenzte, validierte Editoraktionen, darf keine Produkt-/Fertigungsgrenzen aufheben.
- Hintergrundentfernung/Bildaufbereitung ausdrücklich auf Klick und wiederverwendbar. Technik/Lizenz/Ressourcen/Datenschutz dafür noch zu klären, keine bereits vorhandene Funktion behaupten.
- KI-Produktansicht bleibt separat und kostenbegrenzt; Fertigungsgrundlage bleibt exakter Entwurf plus Originalmotiv. Herstellbarkeit muss weiterhin materialspezifisch geprüft werden.
- Vor Implementierung Umfang/Assistentenvariante bestätigen. Auth-/Betreiberverwaltung vor neuem Auth-Code erneut mit passendem Integrations-Playbook klären; kein ungeschützter Adminbereich.

### Priorisierter weiterer Backlog
- P0: Reale Rohlingmaße/Gravurflächen/Materialregeln und Fotos vom Nutzer; keine Freigabe der Muster zur Fertigung behaupten.
- P1: Nach Bestätigung Betreiber-Flächeneditor und begrenzter Drag-/Resize-Editor für Endkunden.
- P1: Geführter Gestaltungsassistent mit Beispielauswahl; optionale zusätzliche Text-KI nur nach Entscheidung.
- P2: Gesonderte Hintergrundentfernung und druck-/laserfähiger Export nach festgelegten Maschinenanforderungen.
- Testmodus mit null Euro Zahlbetrag bleibt erhalten; echte Zahlungen sind kein automatischer nächster Schritt.

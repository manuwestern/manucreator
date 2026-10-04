# ManuCreator — One-Page-Webseite

## Aktueller Stand — 2026-10-04 (maßgeblich; ältere Studio-Pläne unten sind Historie)
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

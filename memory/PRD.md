# ManuCreator — One-Page-Webseite

## Originale Aufgabenstellung
„Kannst du basierend auf diesem Mockup eine schöne One-Page-Webseite machen mit schönen dezenten Animationen. Die weiteren Bilder, die du auf dem Bild siehst, die werde ich dir noch mitgeben. Und im Hero soll so ein Effekt sein, dazu gebe ich dir aber auch noch mal drei, vier separate Bilder, ähm, wo wenn man so scrollt, sich so ein bisschen so dieser Parallax-Effekt beziehungsweise so perspektivischer Effekt reinkommt.“

Der Nutzer stellte ein vollständiges ManuCreator-Mockup bereit und bat: „Start the task now“.

## Explizite Entscheidungen des Nutzers
- „Starte mit passenden vorläufigen Bildern; die Originale liefere ich später“
- „Ein Kontaktformular, das Anfragen auf der Webseite speichert“
- Deutschsprachige One-Page nahe der bereitgestellten visuellen Vorlage. Keine zusätzliche Rückfrage erforderlich.
- Aktuell: geliefertes Video als Hero-Hintergrund nutzen; Scrollen abwärts steuert die Bilder vorwärts, aufwärts rückwärts. Kein zeitgesteuertes Autoplay.
- Nach Fehlermeldung des Nutzers wird derselbe Effekt mit echten extrahierten Video-Einzelbildern statt browserabhängigem Video-Seeking dargestellt. Bewegungsreduktion bleibt standardmäßig respektiert, kann ausdrücklich im Hero übersteuert werden.

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
- Kein Login, Adminbereich, Dateiupload oder E-Mail-Versand angefragt oder implementiert. Anfragen werden tatsächlich gespeichert, keine gemockte API.
- Keine öffentliche Liste oder Abrufmöglichkeit für personenbezogene Anfragedaten.
- Pydantic validiert UUID, Name, E-Mail, Material, Stückzahl, Nachricht, Einwilligung und Honeypot. Einmalige Request-ID verhindert doppelte Speicherung bei Retry.
- Einwilligungszeitpunkt entspricht `created_at`, gespeichert als UTC-ISO-Zeitstempel; Status initial `new`.
- Statische Bilder unter `frontend/public/images/`, Materialdaten zentral unter `src/data/services.js`.
- Vom Nutzer bereitgestellte Vorlage ist Designgrundlage, deshalb kein eigener Design-Agent benötigt. Palette Anthrazit, gebrochenes Weiß, warmer heller CTA-Akzent; lokal gehostete variable Schrift Manrope.
- Stockbilder waren nicht passend zur Materialdarstellung. Vorläufige Produktmotive wurden generiert. Original-Logo aus der vom Nutzer bereitgestellten Mockup-Bilddatei extrahiert.
- Kontakt-, Material-, Beispiel-, Über-mich- und Rechtstext-Ansichten als zugängliche Dialoge, keine unnötigen Unterseiten.

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
- Vollständigen Namen/Firmenbezeichnung, Anschrift und Kontaktdaten für Impressum erhalten; Datenschutz anhand tatsächlicher Betreiber-/Hostingangaben vervollständigen.
### P1 — Vom Nutzer angekündigt
- Noch ausstehende Originalbilder für Holzgravuren und Kunststoffgravuren einbauen, sobald hochgeladen. Glas, Metall, Schiefer, Textildruck und Kontaktmotiv sind bereits ersetzt.
- Ursprünglich angekündigte separate Hero-Ebenen sind durch den später gewünschten, gelieferten Scroll-Video-Hero ersetzt; keine weiteren Hero-Bilder für den aktuellen Effekt erforderlich.
### P2 — Optionale sichtbare Erweiterungen
- Wunschtext-Gravurvorschau auf einem ausgewählten Material.
- Optional später eine geschützte Anfrageverwaltung, nur nach ausdrücklicher Beauftragung; vor Auth-Code zwingend Integrations-Playbook einholen.
- Optionale echte Referenzgalerie mit gelieferten Projektbildern.

## Nächste Aufgaben
1. Weitere Originalbilder für Holz/Kunststoff vom Nutzer entgegennehmen.
2. Rechtliche Anbieterangaben ergänzen.
3. Optional interaktive Gravurvorschau anbieten.

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

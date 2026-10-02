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
- Kein Login, Adminbereich, Dateiupload oder E-Mail-Versand angefragt oder implementiert. Anfragen werden tatsächlich gespeichert, keine gemockte API.
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
- Wunschtext-Gravurvorschau auf einem ausgewählten Material.
- Optional später eine geschützte Anfrageverwaltung, nur nach ausdrücklicher Beauftragung; vor Auth-Code zwingend Integrations-Playbook einholen.
- Optionale echte Referenzgalerie mit gelieferten Projektbildern.

## Nächste Aufgaben
1. Weitere Originalbilder für Holz/Kunststoff vom Nutzer entgegennehmen.
2. Fehlende Telefonnummer und Betriebsdetails ergänzen; Rechtstext-Entwürfe nach fachlicher Prüfung freigeben.
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

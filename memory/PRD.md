# ManuCreator — One-Page-Webseite

## Originale Aufgabenstellung
„Kannst du basierend auf diesem Mockup eine schöne One-Page-Webseite machen mit schönen dezenten Animationen. Die weiteren Bilder, die du auf dem Bild siehst, die werde ich dir noch mitgeben. Und im Hero soll so ein Effekt sein, dazu gebe ich dir aber auch noch mal drei, vier separate Bilder, ähm, wo wenn man so scrollt, sich so ein bisschen so dieser Parallax-Effekt beziehungsweise so perspektivischer Effekt reinkommt.“

Der Nutzer stellte ein vollständiges ManuCreator-Mockup bereit und bat: „Start the task now“.

## Explizite Entscheidungen des Nutzers
- „Starte mit passenden vorläufigen Bildern; die Originale liefere ich später“
- „Ein Kontaktformular, das Anfragen auf der Webseite speichert“
- Deutschsprachige One-Page nahe der bereitgestellten visuellen Vorlage. Keine zusätzliche Rückfrage erforderlich.

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
- Drei/vier separate Hero-Bilder als unabhängige Tiefenebenen integrieren und Scroll-Perspektive gezielt pro Ebene abstimmen.
### P2 — Optionale sichtbare Erweiterungen
- Wunschtext-Gravurvorschau auf einem ausgewählten Material.
- Optional später eine geschützte Anfrageverwaltung, nur nach ausdrücklicher Beauftragung; vor Auth-Code zwingend Integrations-Playbook einholen.
- Optionale echte Referenzgalerie mit gelieferten Projektbildern.

## Nächste Aufgaben
1. Weitere Originalbilder für Holz/Kunststoff und separate Hero-Ebenen vom Nutzer entgegennehmen.
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

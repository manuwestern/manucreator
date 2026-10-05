# Aktueller Auth-Fehler — Domainfreigabe / Produktionsprüfung 2026-10-05
- Gemeldete Seite: https://manucreator.de/verwaltung, Fehler „Nicht erlaubter Ursprung der Anfrage.“ Produktionsdiagnose bestätigt: CORS_ORIGINS war `*`, aber die Admin-CSRF-Prüfung verlangt explizite Ursprünge. Frontend-Zieladresse, Erreichbarkeit und Cookie-Eigenschaften waren nicht die Ursache.
- Korrektur in Quellkonfiguration: bestehende Vorschauursprünge erhalten, konkrete Live-Ursprünge ergänzt. Gemeinsamer Parser `studio/origins.py` für CORS und Adminprüfung: trimmen/kanonisieren, doppelte Einträge entfernen, Wildcard/null/ungültige URLs nicht freigeben. Niemals beliebigen Origin oder Forwarded-Host vertrauen.
- Der bestehende Produktions-Secretwert wird durch eine erneute Veröffentlichung **nicht** automatisch aus backend/.env überschrieben. Der Betreiber muss CORS_ORIGINS im Veröffentlichungspanel/Secrets auf `https://manucreator.de,https://www.manucreator.de,https://subtle-motion-8.emergent.host` setzen, speichern und erneut veröffentlichen. Bis zur Umsetzung/Live-Prüfung den Produktionsfehler nicht als behoben bezeichnen.
- Vor Abschluss zwingend Testing-Agent: Parser und Origin-Prüfung für Apex/www/native/Vorschau, Leerzeichen/abschließender Slash/Port443, Wildcard-only fail-closed, falsche Domain/Subdomain-Suffix/Port/Schema, fehlender Origin und `null`; auch gefälschte Host-/Forwarded-Header dürfen keine neue Freigabe erzeugen.
- API: zulässige Ursprünge → Login mit vorhandenem Admin, Secure/HttpOnly/SameSite=None/Path=/api/admin, /me, Refresh-Rotation, Logout. Echte fremde/fehlende Origins bleiben403; kein wildcard ACAO mit Credentials. Ungültige Passwörter/Role/Tokens bleiben abgewiesen. Nicht den echten Admin durch absichtlich falsche Passwörter sperren.
- Browser: normale Vorschau-Anmeldung und Adminnavigation ohne Regression. Produktionslogin erst nach Bestätigung der Secretänderung und Veröffentlichung prüfen, nur einmal mit vorhandenen Zugangsdaten; keine Änderungen an Produktivartikeln/-inhalten. Keine Secrets in Berichten ausgeben.
- Nach Iteration21 durch Troubleshooting eingegrenzt: Vorschau-Gateway normalisiert ausschließlich seine eigene `preview.emergentagent.com`-Origin zur konfigurierten Cluster-Vorschau-Origin. Direkte ASGI-Tests müssen für **alle** expliziten Origins exaktes Echo erzwingen. Externe Tests dürfen nur für die eigene Vorschau-Alias-Origin den ebenfalls explizit konfigurierten, gleichnamigen Cluster-Ursprung akzeptieren; Produktions-/Fremd-Ursprünge bleiben exakt geprüft. Keine Anpassung oder Lockerung am Anwendungscode für diese Infrastruktur-Eigenheit.

# Admin-Tests — Erweiterung 2026-10-04
Richtige Zugangsdaten: /app/memory/test_credentials.md. Externe Preview aus frontend/.env benutzen.
1. Mongo: studio_admins.email eindeutiger Index, password_hash beginnt mit $2b$, keine Klartextpasswörter. studio_admin_sessions und studio_login_attempts TTL auf expires_at.
2. POST /api/admin/auth/login mit E-Mail/Passwort und Origin der Vorschau; Cookiejar speichern. Secure/HttpOnly admin_access + admin_refresh, Path /api/admin prüfen.
3. GET /api/admin/auth/me mit Cookies erfolgreich; ohne Cookies, mit Gasttoken und abgelaufenen/manipulierten Cookies 401.
4. POST refresh rotiert Nonce; derselbe Refresh-Token darf nicht erneut funktionieren. Logout widerruft Session inklusive kopierter Access-Cookies.
5. Fünf falsche Passwörter sperren den Netzwerk/E-Mail-Schlüssel für 15min. Tests dafür separate E-Mail verwenden, echten Admin nicht sperren.
6. Admin-Mutationsrequests ohne bzw. mit fremdem Origin ablehnen (403). Gast-Dateien bleiben privat. Produktbilder werden ausschließlich für kind=product_blank öffentlich bedient.

# Gastzugang des Gestaltungsstudios
Kein Login, keine Passwörter, keine Admin-Konten. Relevante Teile des JWT-Playbooks umgesetzt: HS256 mit serverseitigem geheimem JWT_SECRET, Access-Tokens 15 Minuten, Refresh 7 Tage, Typ-/Signatur-/Ablaufprüfung sowie Existenzprüfung in Mongo.

## Prüfen
1. POST /api/studio/session mit {} erstellt Gast und liefert Access-/Refresh-Token. Refresh nur mit refresh_token im Body, korrektem Typ, gültiger Signatur und passendem gespeicherten nonce. Alte Refresh-Nonce nach Rotation ungültig.
2. Authorization: Bearer für Upload, Dateiabruf, Entwurf, KI, Warenkorb und Testbestellung erforderlich. Kein Token in URLs; Bilder per Blob abrufen.
3. Zweiter Gast darf keine Dateien/Entwürfe/Bestellungen des ersten lesen, verändern oder für KI/Warenkorb verwenden. Ungültige/abgelaufene Tokens und falscher Tokentyp führen zu 401.
4. Bestätigte Upload-Rechte, Dateiformat/-größe, exakte Vorlage/Textgrenzen und alle Produktparameter serverseitig validieren.
5. KI-Quoten atomar prüfen, parallele Requests dürfen nur einen Job je Entwurf erzeugen. Fertige Vorschauen werden unverändert wiederverwendet, ohne Zählererhöhung. Globale Tagesgrenze bindend, Peer-IP nur sekundäres Gruppierungslimit (keine Behauptung echter Nutzer-IP hinter Shared-Ingress).
6. Testcheckout niemals Zahlung oder Fertigung; Preise ausschließlich serverseitig, Snapshots unveränderlich, Idempotenz pro request_id. Alte Homepage-Anfragen unverändert.
7. Alle privaten Mongo-Antworten projizieren _id heraus; keine Passwörter oder Speicher-/Provider-Schlüssel im Frontend.
# RCA — ManuCreator production admin login: "Nicht erlaubter Ursprung der Anfrage" (403)

## Deployment
- Deployment: `subtle-motion-8` (active, monthly plan)
- Platform URL: `https://subtle-motion-8.emergent.host`
- Verified custom domains: `manucreator.de`, `www.manucreator.de` (frontend served via Cloudflare)
- Active run: `c9ec455d-e9ee-401e-a1f5-caa30af83000` (redeploy, success)
- Template: fastapi_react_mongo_shadcn (FastAPI + React + Mongo)

## Symptom
Admin login at `/verwaltung` fails ONLY in production with HTTP 403 and message
`Nicht erlaubter Ursprung der Anfrage.` Preview worked.

## Production evidence (not assumed)
Runtime logs (active run, last 24h) — repeated and unambiguous:
```
Admin origin rejected: received='https://manucreator.de' configured='*'
POST /api/admin/auth/login  HTTP/1.1  403 Forbidden
POST /api/admin/auth/refresh HTTP/1.1 403 Forbidden
GET  /api/admin/auth/me     HTTP/1.1 401 Unauthorized   (cascade — no valid cookie ever set)
```
- `POST /api/studio/text-preview` → 200, so the backend is reachable and healthy; this is an app-level authorization rejection, not a network/proxy failure.
- Observed request Origin: `https://manucreator.de`. API target is same-origin (see below).

## Source line causing the rejection
`backend/studio/admin_auth.py` (lines 39–43):
```python
async def same_origin(request: Request):
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        if request.headers.get('origin') not in os.environ['CORS_ORIGINS'].split(','):
            logging.getLogger(__name__).warning('Admin origin rejected: received=%r configured=%r', ...)
            raise HTTPException(403, 'Nicht erlaubter Ursprung der Anfrage.')
```
`same_origin` is a dependency on `/api/admin/auth/login`, `/refresh`, and (via `current_admin`) `/me`.
It performs an **exact string membership test** against `CORS_ORIGINS.split(',')`. It does **NOT** interpret `*` as a wildcard.

## Root cause
The **production `CORS_ORIGINS` secret is literally `*`** (confirmed by the log `configured='*'`).
`'https://manucreator.de' not in ['*']` → `True` → 403 on every state‑changing admin request.

- Verified via `list_secrets` equals-check: production `CORS_ORIGINS` does **NOT** equal
  `https://manucreator.de,https://www.manucreator.de` (`matches_expected=false`), consistent with the logged value `*`.
- Preview succeeded because preview `backend/.env` has the exact preview origins:
  `CORS_ORIGINS="https://subtle-motion-8.preview.emergentagent.com,https://subtle-motion-8.cluster-12.preview.emergentcf.cloud"` — which matched the preview page origin. The production custom-domain origins were never placed in that list; the deployed secret ended up as the non‑functional wildcard `*`.

## Ruled out (verified, NOT the cause)
- **REACT_APP_BACKEND_URL**: production value equals `https://manucreator.de` (`matches_expected=true`). The admin API call is therefore **same-origin** with the page — correct. Not the problem.
- **Cookies**: `set_cookie(httponly=True, secure=True, samesite='none', path='/api/admin')` — valid for the same-origin HTTPS setup; irrelevant because the 403 happens before any cookie is issued.
- **Reachability / proxy**: backend reachable, other POSTs return 200. Cloudflare `/api/*` routing works.

## Remediation — two parties

### 1) PRIMARY — Production config action (User, no code strictly required)
`CORS_ORIGINS` is an existing deployment secret. Pre-existing secret values are NOT overwritten on redeploy, so it must be changed in the UI: **Deployment Panel → Secrets**. Set it to the exact live origins (comma-separated, no spaces, scheme included, no trailing slash):
```
https://manucreator.de,https://www.manucreator.de,https://subtle-motion-8.emergent.host
```
Save, then redeploy. Because the check is exact-match, these literal origins make `same_origin` pass and admin login succeeds. This alone fixes the live failure.

### 2) SECONDARY — Code hardening (Code, applied by main agent; durable + defensive)
- Update `backend/.env` `CORS_ORIGINS` to include the production origins above, so source config is correct for future deploys. (Note: this does NOT retroactively change the live secret — step 1 is still required to fix the current run.)
- In `backend/studio/admin_auth.py` make `same_origin` robust:
  - strip whitespace per entry: `allowed = [o.strip() for o in os.environ['CORS_ORIGINS'].split(',') if o.strip()]`
  - decide `*` semantics explicitly. For credentialed admin cookies, prefer an explicit allow-list (do NOT rely on `*`). If a wildcard must be supported, handle it: `if '*' not in allowed and origin not in allowed: reject`.
- Note: `backend/server.py` line 34 sets the CORS middleware `allow_origins=os.environ['CORS_ORIGINS'].split(',')`; wildcard `*` combined with credentialed cookies is spec-invalid in browsers. Using explicit origins also resolves this.

## Verification note
Source logic reproduced and read in an ephemeral sandbox from this run's pulled source (exact-match test, no `*` handling confirmed). The production secret value `*` is confirmed from runtime logs plus the `matches_expected=false` check — the full 403 could not be re-executed in-pod because it depends on the production secret (not injected into the sandbox), but source + logs make the chain unambiguous.

## Post-fix verification (per user instruction)
After updating the secret and (if code changed) redeploying, main agent MUST use testing_agent to verify `/api/admin/auth/login` → 200 and cookie issuance from origin `https://manucreator.de` (and `https://www.manucreator.de`).

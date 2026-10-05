"""Iteration 21: explicit origin parser and admin auth CORS/CSRF regression tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests

sys.path.append("/app/backend")
from studio.origins import explicit_origins


def _load_env_value(env_path: Path, key: str) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    raise RuntimeError(f"Missing {key} in {env_path}")


BASE_URL = _load_env_value(Path("/app/frontend/.env"), "REACT_APP_BACKEND_URL").rstrip("/")
ADMIN_EMAIL = _load_env_value(Path("/app/backend/.env"), "ADMIN_EMAIL")
ADMIN_PASSWORD = _load_env_value(Path("/app/backend/.env"), "ADMIN_PASSWORD")
CORS_ORIGINS_VALUE = _load_env_value(Path("/app/backend/.env"), "CORS_ORIGINS")
os.environ["CORS_ORIGINS"] = CORS_ORIGINS_VALUE
CONFIGURED_EXPLICIT_ORIGINS = explicit_origins()


def _extract_cookie_by_name(response: requests.Response, cookie_name: str) -> str | None:
    for cookie in response.cookies:
        if cookie.name == cookie_name:
            return cookie.value
    return None


def _assert_cookie_security_headers(set_cookie_header: str):
    assert "HttpOnly" in set_cookie_header
    assert "Secure" in set_cookie_header
    assert "Path=/api/admin" in set_cookie_header
    assert "SameSite=None" in set_cookie_header or "SameSite=none" in set_cookie_header


def _assert_external_origin(response, origin):
    """The preview gateway rewrites ONLY its own alias to the configured cluster origin.

    Exact application behavior is independently required by the direct ASGI test.
    Live/custom/unrelated origins must still echo EXACTLY, never a wildcard.
    """
    acceptable={origin}
    host=urlsplit(origin).hostname or ''
    if origin==BASE_URL and host.endswith('.preview.emergentagent.com'):
        job=host.removesuffix('.preview.emergentagent.com')
        acceptable.update(candidate for candidate in CONFIGURED_EXPLICIT_ORIGINS
                          if (urlsplit(candidate).hostname or '').startswith(job+'.cluster-')
                          and (urlsplit(candidate).hostname or '').endswith('.preview.emergentcf.cloud'))
    assert response.headers.get('access-control-allow-origin') in acceptable
    assert response.headers.get('access-control-allow-origin')!='*'


def test_direct_application_cors_echoes_every_origin_exactly():
    from starlette.testclient import TestClient
    from server import app

    client=TestClient(app)
    for origin in CONFIGURED_EXPLICIT_ORIGINS:
        response=client.options('/api/admin/auth/login',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
        assert response.status_code==200
        assert response.headers.get('access-control-allow-origin')==origin
        assert response.headers.get('access-control-allow-credentials')=='true'
    foreign=client.options('/api/admin/auth/login',headers={'Origin':'https://foreign.example','Access-Control-Request-Method':'POST'})
    assert foreign.status_code==400
    assert 'access-control-allow-origin' not in foreign.headers


# Module coverage: parser canonicalization and invalid-entry rejection rules
def test_explicit_origins_canonicalization_and_rejection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        " ,https://MANUCREATOR.DE/ ,https://manucreator.de:443,https://www.manucreator.de:443/,http://example.com:80/,"
        "https://[2001:db8::1]:443,https://user:pass@evil.com,https://manucreator.de/path,https://manucreator.de?x=1,"
        "https://manucreator.de#frag,https://manucreator.de:abc,null,//manucreator.de,*.manucreator.de,https://*.manucreator.de,* ",
    )

    assert explicit_origins() == [
        "https://manucreator.de",
        "https://www.manucreator.de",
        "http://example.com",
        "https://[2001:db8::1]",
    ]


# Module coverage: fail-fast behavior when CORS_ORIGINS is missing
def test_explicit_origins_missing_env_fails_fast(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    with pytest.raises(KeyError):
        explicit_origins()


# Module coverage: wildcard-only fail-closed and wildcard+explicit allow explicit only
def test_explicit_origins_wildcard_handling(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")
    assert explicit_origins() == []

    monkeypatch.setenv("CORS_ORIGINS", "*, https://manucreator.de/, https://www.manucreator.de")
    assert explicit_origins() == ["https://manucreator.de", "https://www.manucreator.de"]


# Module coverage: server CORS middleware and admin CSRF share same explicit-origin parser output
def test_server_cors_uses_same_explicit_origin_policy():
    from server import app

    cors = next(m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware")
    assert cors.kwargs["allow_origins"] == CONFIGURED_EXPLICIT_ORIGINS
    assert "*" not in cors.kwargs["allow_origins"]


# Module coverage: configured origins pass login/me/refresh/logout and enforce cookie+CORS headers
def test_admin_auth_succeeds_for_each_configured_origin():
    assert CONFIGURED_EXPLICIT_ORIGINS, "CORS_ORIGINS resolved empty; admin credentialed CORS would be blocked"

    for origin in CONFIGURED_EXPLICIT_ORIGINS:
        session = requests.Session()
        login = session.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers={"Origin": origin},
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=25,
        )
        assert login.status_code == 200, f"{origin}: {login.status_code} {login.text}"
        _assert_external_origin(login,origin)
        assert login.headers.get("access-control-allow-credentials") == "true"
        _assert_cookie_security_headers(login.headers.get("set-cookie", ""))

        me = session.get(f"{BASE_URL}/api/admin/auth/me", headers={"Origin": origin}, timeout=20)
        assert me.status_code == 200
        assert me.json()["email"] == ADMIN_EMAIL.lower()

        old_refresh = _extract_cookie_by_name(login, "admin_refresh")
        refreshed = session.post(f"{BASE_URL}/api/admin/auth/refresh", headers={"Origin": origin}, timeout=20)
        assert refreshed.status_code == 200
        _assert_external_origin(refreshed,origin)
        assert refreshed.headers.get("access-control-allow-credentials") == "true"
        _assert_cookie_security_headers(refreshed.headers.get("set-cookie", ""))

        new_refresh = _extract_cookie_by_name(refreshed, "admin_refresh")
        assert old_refresh is not None and new_refresh is not None and old_refresh != new_refresh

        logout = session.post(f"{BASE_URL}/api/admin/auth/logout", headers={"Origin": origin}, timeout=20)
        assert logout.status_code == 200


# Module coverage: missing/null/malicious/wrong-scheme-or-port origins must be blocked on writes
def test_admin_login_rejects_unconfigured_origins():
    rejected = [
        {},
        {"Origin": "null"},
        {"Origin": "https://manucreator.de.evil.example"},
        {"Origin": "https://evil.manucreator.de"},
        {"Origin": "http://manucreator.de"},
        {"Origin": "https://manucreator.de:444"},
    ]
    for headers in rejected:
        response = requests.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers=headers,
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=20,
        )
        assert response.status_code == 403, f"expected 403 for headers={headers}, got {response.status_code}"


# Module coverage: host/x-forwarded spoofing cannot authorize foreign origins
def test_admin_login_rejects_spoofed_forwarded_headers_with_foreign_origin():
    allowed_host = CONFIGURED_EXPLICIT_ORIGINS[0].replace("https://", "").replace("http://", "")
    response = requests.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={
            "Origin": "https://foreign.example",
            "Host": allowed_host,
            "X-Forwarded-Host": allowed_host,
            "X-Forwarded-Proto": "https",
        },
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert response.status_code == 403


# Module coverage: preflight CORS allows explicit origins only; foreign preflight blocked
def test_admin_login_preflight_explicit_only():
    for origin in CONFIGURED_EXPLICIT_ORIGINS:
        ok = requests.options(
            f"{BASE_URL}/api/admin/auth/login",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=20,
        )
        assert ok.status_code in (200, 204)
        _assert_external_origin(ok,origin)
        assert ok.headers.get("access-control-allow-credentials") == "true"

    foreign = requests.options(
        f"{BASE_URL}/api/admin/auth/login",
        headers={
            "Origin": "https://foreign.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
        timeout=20,
    )
    assert foreign.status_code in (400, 403)
    assert foreign.headers.get("access-control-allow-origin") != "https://foreign.example"
    assert foreign.headers.get("access-control-allow-origin") != "*"


# Module coverage: brute-force lockout threshold still enforced after five failed attempts
def test_admin_login_lockout_after_five_failures_for_isolated_email():
    test_email = f"origin-lockout-{os.urandom(4).hex()}@example.com"
    statuses = []
    for _ in range(6):
        attempt = requests.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers={"Origin": CONFIGURED_EXPLICIT_ORIGINS[0]},
            json={"email": test_email, "password": "wrong-password"},
            timeout=20,
        )
        statuses.append(attempt.status_code)
    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429

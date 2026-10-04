"""Studio admin auth/product management tests and retired assistant endpoint checks."""

import io
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import jwt
import pytest
import requests
from PIL import Image
from pymongo import MongoClient


def _load_env_value(env_path: Path, key: str) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    raise RuntimeError(f"Missing {key} in {env_path}")


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _load_env_value(Path("/app/frontend/.env"), "REACT_APP_BACKEND_URL")).rstrip("/")
MONGO_URL = _load_env_value(Path("/app/backend/.env"), "MONGO_URL")
DB_NAME = _load_env_value(Path("/app/backend/.env"), "DB_NAME")
ALLOWED_ORIGINS = [value.strip() for value in _load_env_value(Path("/app/backend/.env"), "CORS_ORIGINS").split(",") if value.strip()]
ORIGIN = next((value for value in ALLOWED_ORIGINS if "emergentcf.cloud" in value), ALLOWED_ORIGINS[0])
COOKIE_DOMAIN = urlparse(BASE_URL).hostname
COOKIE_PATH = "/api/admin"
GUEST_CACHE = {"refresh_token": None}
JWT_SECRET = _load_env_value(Path("/app/backend/.env"), "JWT_SECRET")


def _markdown_value(path: Path, marker: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if marker in line:
            return line.split(marker, 1)[1].split("`", 1)[0]
    raise RuntimeError(f"Missing marker {marker} in {path}")


# override parsed credentials with markdown parser (test_credentials.md format)
ADMIN_EMAIL = _markdown_value(Path("/app/memory/test_credentials.md"), "E-Mail: `")
ADMIN_PASSWORD = _markdown_value(Path("/app/memory/test_credentials.md"), "Passwort: `")


@pytest.fixture(scope="session")
def api_client():
    return requests.Session()


@pytest.fixture(scope="session")
def mongo_db():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=7000)
    database = client[DB_NAME]
    try:
        yield database
    finally:
        client.close()


@pytest.fixture(autouse=True)
def cleanup_test_products(mongo_db):
    yield
    mongo_db["studio_products"].delete_many({"name": {"$regex": "^TEST "}})


def _png_bytes(width=1100, height=700, color=(180, 210, 140, 255)):
    image = Image.new("RGBA", (width, height), color)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _create_guest(api_client, force_new=False):
    payload = {} if force_new else ({"refresh_token": GUEST_CACHE["refresh_token"]} if GUEST_CACHE.get("refresh_token") else {})
    response = api_client.post(f"{BASE_URL}/api/studio/session", json=payload, timeout=25)
    if response.status_code == 429 and GUEST_CACHE.get("refresh_token") and not force_new:
        response = api_client.post(
            f"{BASE_URL}/api/studio/session",
            json={"refresh_token": GUEST_CACHE["refresh_token"]},
            timeout=25,
        )
    assert response.status_code == 200
    token = response.json()["token"]
    GUEST_CACHE["refresh_token"] = response.json().get("refresh_token")
    return {"Authorization": f"Bearer {token}"}


def _save_text_draft(api_client, headers, product_id="holzscheibe", text="Mia", subtitle="Test"):
    payload = {
        "product_id": product_id,
        "template": "text",
        "text": text,
        "subtitle": subtitle,
        "font": "classic",
        "size": "medium",
        "position": "center",
        "asset_id": None,
        "zoom": 1,
        "focal_x": 0,
        "focal_y": 0,
    }
    saved = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=payload, timeout=30)
    assert saved.status_code == 200
    return saved.json()


def _admin_login(api_client):
    response = api_client.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=25,
    )
    assert response.status_code == 200
    return response


def _cookie_value(cookiejar, name: str) -> str | None:
    for cookie in cookiejar:
        if cookie.name != name:
            continue
        if cookie.path != COOKIE_PATH:
            continue
        if COOKIE_DOMAIN and cookie.domain and COOKIE_DOMAIN not in cookie.domain:
            continue
        return cookie.value
    return None


def _set_admin_cookie(cookiejar, name: str, value: str | None):
    if not value:
        return
    for cookie in list(cookiejar):
        if cookie.name == name:
            cookiejar.clear(domain=cookie.domain, path=cookie.path, name=cookie.name)
    cookiejar.set(name, value, domain=COOKIE_DOMAIN, path=COOKIE_PATH)


def _seed_peer_guest(mongo_db):
    identity = f"TEST_guest_{uuid4().hex}"
    nonce = uuid4().hex
    issued = datetime.now(timezone.utc)
    expires = issued + timedelta(days=7)
    mongo_db["studio_guests"].update_one(
        {"id": identity},
        {
            "$set": {
                "id": identity,
                "network": "seeded-test-network",
                "nonce": nonce,
                "expires_at": expires,
                "created_at": issued,
            }
        },
        upsert=True,
    )
    access = jwt.encode(
        {"sub": identity, "type": "access", "jti": nonce, "exp": issued + timedelta(minutes=15), "iat": issued},
        JWT_SECRET,
        algorithm="HS256",
    )
    refresh = jwt.encode(
        {"sub": identity, "type": "refresh", "jti": nonce, "exp": issued + timedelta(days=7), "iat": issued},
        JWT_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {access}"}, refresh


@pytest.fixture(scope="session", autouse=True)
def prime_guest_cache(mongo_db):
    if not GUEST_CACHE.get("refresh_token"):
        _, refresh = _seed_peer_guest(mongo_db)
        GUEST_CACHE["refresh_token"] = refresh


# Module coverage: admin auth CORS/cookies/rotation/logout and brute-force protection
def test_admin_auth_flow_and_cookie_rotation(api_client, mongo_db):
    admin_record = mongo_db["studio_admins"].find_one({"email": ADMIN_EMAIL.lower()}, {"_id": 0, "password_hash": 1})
    assert admin_record and admin_record["password_hash"].startswith("$2b$")

    no_origin = api_client.post(
        f"{BASE_URL}/api/admin/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert no_origin.status_code == 403

    bad_origin = api_client.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": "https://invalid-origin.example"},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert bad_origin.status_code == 403

    login = _admin_login(api_client)
    assert login.headers.get("access-control-allow-origin") in ALLOWED_ORIGINS
    assert login.headers.get("access-control-allow-credentials") == "true"
    assert "HttpOnly" in "; ".join(login.headers.get("set-cookie", "").split(","))

    me = api_client.get(f"{BASE_URL}/api/admin/auth/me", timeout=20)
    assert me.status_code == 200
    assert me.json()["email"] == ADMIN_EMAIL.lower()

    old_refresh = _cookie_value(api_client.cookies, "admin_refresh")
    refresh = api_client.post(f"{BASE_URL}/api/admin/auth/refresh", headers={"Origin": ORIGIN}, timeout=20)
    assert refresh.status_code == 200
    new_refresh = _cookie_value(api_client.cookies, "admin_refresh")
    assert new_refresh and new_refresh != old_refresh

    _set_admin_cookie(api_client.cookies, "admin_refresh", old_refresh)
    old_refresh_reuse = api_client.post(f"{BASE_URL}/api/admin/auth/refresh", headers={"Origin": ORIGIN}, timeout=20)
    assert old_refresh_reuse.status_code == 401

    _set_admin_cookie(api_client.cookies, "admin_refresh", new_refresh)
    copied_access = _cookie_value(api_client.cookies, "admin_access")
    copied_refresh = _cookie_value(api_client.cookies, "admin_refresh")
    logout = api_client.post(f"{BASE_URL}/api/admin/auth/logout", headers={"Origin": ORIGIN}, timeout=20)
    assert logout.status_code == 200

    _set_admin_cookie(api_client.cookies, "admin_access", copied_access)
    _set_admin_cookie(api_client.cookies, "admin_refresh", copied_refresh)
    after_logout = api_client.get(f"{BASE_URL}/api/admin/auth/me", timeout=20)
    assert after_logout.status_code == 401


# Module coverage: brute force lockout on non-owner account after five failures
def test_admin_bruteforce_lockout_non_owner_email(api_client):
    test_email = f"lockout-{uuid4().hex[:8]}@example.com"
    for _ in range(5):
        fail = api_client.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers={"Origin": ORIGIN},
            json={"email": test_email, "password": "wrong-pass"},
            timeout=20,
        )
        assert fail.status_code == 401

    blocked = api_client.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": test_email, "password": "wrong-pass"},
        timeout=20,
    )
    assert blocked.status_code == 429


# Module coverage: admin CRUD/product-photo pipeline/version conflicts/archive/reactivate/public privacy
def test_admin_product_crud_and_public_product_image_guard(api_client, mongo_db):
    _admin_login(api_client)
    product_id = None
    file_id = None
    guest_file_id = None

    uploaded = api_client.post(
        f"{BASE_URL}/api/admin/products/photo",
        headers={"Origin": ORIGIN},
        files={"file": ("product.png", _png_bytes(), "image/png")},
        timeout=35,
    )
    assert uploaded.status_code == 201
    file_id = uploaded.json()["id"]

    photo = api_client.get(f"{BASE_URL}{uploaded.json()['image']}", timeout=35)
    assert photo.status_code == 200
    normalized = Image.open(io.BytesIO(photo.content))
    assert normalized.size == (800, 800)

    guest_headers = _create_guest(api_client)
    guest_upload = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest_headers,
        files={"file": ("private.png", _png_bytes(640, 640), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    assert guest_upload.status_code == 201
    guest_file_id = guest_upload.json()["id"]
    leaked = api_client.get(f"{BASE_URL}/api/studio/product-images/{guest_file_id}", timeout=20)
    assert leaked.status_code == 404

    payload = {
        "name": f"TEST Blank {uuid4().hex[:6]}",
        "subtitle": "Test Rohling",
        "material": "Testmaterial",
        "category": "holz",
        "price_cents": 2990,
        "dimensions": "90x90x10",
        "area_mm": "50x50",
        "max_text": 24,
        "area": {"x": 220, "y": 220, "w": 300, "h": 300, "shape": "circle"},
        "ink": "#334455",
        "templates": ["text", "photo"],
        "image_file_id": file_id,
        "active": True,
        "is_sample": False,
        "version": 1,
    }
    created = api_client.post(
        f"{BASE_URL}/api/admin/products",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        json=payload,
        timeout=35,
    )
    assert created.status_code == 201
    product = created.json()
    product_id = product["id"]
    assert product["area"]["shape"] == "circle"

    edit_payload = {**payload, "version": product["version"], "area": {"x": 180, "y": 210, "w": 360, "h": 220, "shape": "rect"}}
    edited = api_client.put(
        f"{BASE_URL}/api/admin/products/{product_id}",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        json=edit_payload,
        timeout=35,
    )
    assert edited.status_code == 200
    assert edited.json()["version"] == 2
    assert edited.json()["area"]["shape"] == "rect"

    stale = api_client.put(
        f"{BASE_URL}/api/admin/products/{product_id}",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        json={**edit_payload, "version": 1},
        timeout=30,
    )
    assert stale.status_code == 409

    archived = api_client.delete(
        f"{BASE_URL}/api/admin/products/{product_id}",
        headers={"Origin": ORIGIN},
        timeout=30,
    )
    assert archived.status_code == 200
    assert archived.json()["active"] is False

    public_catalog = api_client.get(f"{BASE_URL}/api/studio/products", timeout=25)
    assert public_catalog.status_code == 200
    assert all(item["id"] != product_id for item in public_catalog.json()["products"])

    archived_list = api_client.get(f"{BASE_URL}/api/admin/products", timeout=25)
    assert archived_list.status_code == 200
    archived_item = next(item for item in archived_list.json() if item["id"] == product_id)
    reactivate_payload = {
        key: value
        for key, value in archived_item.items()
        if key not in {"id", "image", "production_approved", "updated_at"}
    }
    reactivate_payload["active"] = True
    restored = api_client.put(
        f"{BASE_URL}/api/admin/products/{product_id}",
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
        json=reactivate_payload,
        timeout=35,
    )
    assert restored.status_code == 200
    assert restored.json()["active"] is True

    # Cleanup TEST artifacts
    if product_id:
        mongo_db["studio_products"].delete_one({"id": product_id})
    if file_id:
        mongo_db["studio_files"].delete_one({"id": file_id})
    if guest_file_id:
        mongo_db["studio_files"].delete_one({"id": guest_file_id})


# Module coverage: assistant endpoints must stay retired in new non-AI studio scope
def test_assistant_endpoints_are_removed(api_client):
    guest = _create_guest(api_client)
    draft = _save_text_draft(api_client, guest, text="Lina", subtitle="Sommer 2026")

    create_session = api_client.post(
        f"{BASE_URL}/api/studio/assistant/sessions",
        headers=guest,
        json={"product_id": draft["design"]["product_id"]},
        timeout=20,
    )
    assert create_session.status_code == 404

    send_message = api_client.post(
        f"{BASE_URL}/api/studio/assistant/message",
        headers={**guest, "Accept": "text/event-stream"},
        json={
            "session_id": str(uuid4()),
            "message": "TEST",
            "design": draft["design"],
            "confirmed": True,
        },
        timeout=25,
    )
    assert send_message.status_code == 404

    read_history = api_client.get(
        f"{BASE_URL}/api/studio/assistant/sessions/{uuid4()}",
        headers=guest,
        timeout=20,
    )
    assert read_history.status_code == 404

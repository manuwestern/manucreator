"""Studio API integration tests for guest sessions, uploads, drafts, retired AI endpoints, cart, and test checkout."""

import io
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
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
GUEST_LIMIT = int(_load_env_value(Path("/app/backend/.env"), "STUDIO_AI_GUEST_DAILY_LIMIT"))
JWT_SECRET = _load_env_value(Path("/app/backend/.env"), "JWT_SECRET")
SESSION_CACHE = {"refresh_token": None}


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


def create_guest(api_client, refresh_token=None, force_new=False):
    token = refresh_token if refresh_token is not None else (None if force_new else SESSION_CACHE.get("refresh_token"))
    payload = {"refresh_token": token} if token else {}
    response = api_client.post(f"{BASE_URL}/api/studio/session", json=payload, timeout=25)
    if response.status_code == 429 and SESSION_CACHE.get("refresh_token") and not refresh_token and not force_new:
        response = api_client.post(
            f"{BASE_URL}/api/studio/session",
            json={"refresh_token": SESSION_CACHE["refresh_token"]},
            timeout=25,
        )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("token"), str) and data["token"]
    assert isinstance(data.get("refresh_token"), str) and data["refresh_token"]
    SESSION_CACHE["refresh_token"] = data["refresh_token"]
    claims = jwt.decode(data["token"], options={"verify_signature": False})
    return {
        "token": data["token"],
        "refresh_token": data["refresh_token"],
        "guest": claims["sub"],
        "headers": {"Authorization": f"Bearer {data['token']}"},
    }


def create_png_bytes(width=640, height=640, color=(20, 140, 80, 255)):
    image = Image.new("RGBA", (width, height), color)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def load_real_photo_bytes():
    return Path("/app/frontend/public/images/studio/holzscheibe.webp").read_bytes()


def seed_peer_guest(mongo_db):
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
    return {
        "token": access,
        "refresh_token": refresh,
        "guest": identity,
        "headers": {"Authorization": f"Bearer {access}"},
    }


@pytest.fixture(scope="session", autouse=True)
def prime_session_cache(mongo_db):
    if not SESSION_CACHE.get("refresh_token"):
        SESSION_CACHE["refresh_token"] = seed_peer_guest(mongo_db)["refresh_token"]


def save_text_draft(api_client, headers, product_id="holzscheibe", text="TEST Unikat", subtitle="TEST 2026"):
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
    response = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=payload, timeout=30)
    assert response.status_code == 200
    draft = response.json()
    assert draft["design"]["product_id"] == product_id
    assert draft["design"]["template"] == "text"
    return draft


def _base_layer_payload(product_id="holzscheibe"):
    return {
        "product_id": product_id,
        "template": "text",
        "text": "",
        "subtitle": "",
        "font": "classic",
        "size": "medium",
        "position": "center",
        "asset_id": None,
        "zoom": 1,
        "focal_x": 0,
        "focal_y": 0,
    }


# Module coverage: catalog/sample data and product constraints
def test_products_catalog_has_sample_flags_and_expected_templates(api_client):
    response = api_client.get(f"{BASE_URL}/api/studio/products", timeout=20)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "test"
    assert data["production_approved"] is False
    products = {item["id"]: item for item in data["products"]}
    required = {"holzscheibe", "schneidebrett", "glasschild", "metallanhaenger"}
    assert required.issubset(set(products.keys()))
    assert products["glasschild"]["templates"] == ["text", "logo"]
    assert products["metallanhaenger"]["templates"] == ["text", "logo"]
    assert products["holzscheibe"]["templates"] == ["text", "photo", "logo"]
    assert all(product["is_sample"] is True for product in products.values())


# Module coverage: strict Design.elements schema/rules (count, unique ids, hidden-only invalid, font allowlist)
def test_design_elements_strict_validation_rules(api_client):
    guest = create_guest(api_client)

    too_many = _base_layer_payload()
    too_many["elements"] = [
        {
            "id": f"t{i}",
            "kind": "text",
            "text": "A",
            "font": "sans",
            "x": 260,
            "y": 260,
            "w": 80,
            "h": 30,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        }
        for i in range(13)
    ]
    too_many_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=too_many, timeout=30
    )
    assert too_many_resp.status_code == 422

    duplicate_ids = _base_layer_payload()
    duplicate_ids["elements"] = [
        {
            "id": "dup",
            "kind": "text",
            "text": "A",
            "font": "sans",
            "x": 260,
            "y": 260,
            "w": 120,
            "h": 35,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        },
        {
            "id": "dup",
            "kind": "text",
            "text": "B",
            "font": "sans",
            "x": 280,
            "y": 300,
            "w": 120,
            "h": 35,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        },
    ]
    duplicate_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=duplicate_ids, timeout=30
    )
    assert duplicate_resp.status_code == 422

    hidden_only = _base_layer_payload()
    hidden_only["elements"] = [
        {
            "id": "hidden-text",
            "kind": "text",
            "text": "Invisible",
            "font": "sans",
            "x": 260,
            "y": 260,
            "w": 140,
            "h": 36,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": True,
        }
    ]
    hidden_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=hidden_only, timeout=30
    )
    assert hidden_resp.status_code == 422

    bad_font = _base_layer_payload()
    bad_font["elements"] = [
        {
            "id": "font-test",
            "kind": "text",
            "text": "Text",
            "font": "comic-sans",
            "x": 260,
            "y": 260,
            "w": 120,
            "h": 35,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        }
    ]
    bad_font_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=bad_font, timeout=30
    )
    assert bad_font_resp.status_code == 422


# Module coverage: JWT guest session, refresh rotation, and auth protection
def test_guest_session_refresh_rotation_and_no_auth_401(api_client):
    initial = create_guest(api_client)
    refreshed = create_guest(api_client, initial["refresh_token"])
    assert refreshed["guest"] == initial["guest"]
    assert refreshed["refresh_token"] != initial["refresh_token"]

    old_refresh = api_client.post(
        f"{BASE_URL}/api/studio/session",
        json={"refresh_token": initial["refresh_token"]},
        timeout=20,
    )
    assert old_refresh.status_code == 401

    unauthorized = api_client.get(f"{BASE_URL}/api/studio/cart", timeout=20)
    assert unauthorized.status_code == 401

    wrong_type = api_client.get(
        f"{BASE_URL}/api/studio/cart",
        headers={"Authorization": f"Bearer {initial['refresh_token']}"},
        timeout=20,
    )
    assert wrong_type.status_code == 401


# Module coverage: upload validation, rights check, and PNG/JPG/WebP guardrails
def test_upload_requires_rights_and_rejects_invalid_payloads(api_client):
    guest = create_guest(api_client)

    no_rights = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("small.png", create_png_bytes(), "image/png")},
        data={"rights_confirmed": "false"},
        timeout=30,
    )
    assert no_rights.status_code == 422

    fake = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("fake.png", b"not-an-image", "image/png")},
        data={"rights_confirmed": "true"},
        timeout=30,
    )
    assert fake.status_code == 422

    svg = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("vector.svg", b"<svg xmlns='http://www.w3.org/2000/svg'></svg>", "image/svg+xml")},
        data={"rights_confirmed": "true"},
        timeout=30,
    )
    assert svg.status_code == 422

    oversized = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("big.png", b"0" * (8 * 1024 * 1024 + 1), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=40,
    )
    assert oversized.status_code == 413

    huge = create_png_bytes(width=5000, height=5000)
    huge_pixels = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("huge.png", huge, "image/png")},
        data={"rights_confirmed": "true"},
        timeout=45,
    )
    assert huge_pixels.status_code == 422


# Module coverage: object storage file persistence and metadata-only Mongo record
def test_valid_upload_persists_blob_and_metadata_without_base64(api_client, mongo_db):
    guest = create_guest(api_client)
    uploaded = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("photo.png", create_png_bytes(900, 620), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    assert uploaded.status_code == 201
    body = uploaded.json()
    assert isinstance(body["id"], str)
    assert body["width"] == 900
    assert body["height"] == 620

    blob = api_client.get(f"{BASE_URL}/api/studio/files/{body['id']}", headers=guest["headers"], timeout=35)
    assert blob.status_code == 200
    assert blob.headers["content-type"].startswith("image/")
    loaded = Image.open(io.BytesIO(blob.content))
    assert loaded.width > 0 and loaded.height > 0
    assert "exif" not in loaded.info

    record = mongo_db["studio_files"].find_one({"id": body["id"], "guest": guest["guest"]}, {"_id": 0})
    assert record is not None
    assert record["kind"] == "upload"
    assert "storage_path" in record and isinstance(record["storage_path"], str)
    assert "data" not in record and "base64" not in record and "content" not in record


# Module coverage: GPT cutout no-key contract (capabilities, consent gate, 503 without fallback, ownership)
def test_gpt_cutout_contract_without_openai_key(api_client, mongo_db):
    guest_a = create_guest(api_client)
    guest_b = seed_peer_guest(mongo_db)

    capabilities = api_client.get(f"{BASE_URL}/api/studio/uploads/background-capabilities", timeout=20)
    assert capabilities.status_code == 200
    cap = capabilities.json()
    assert cap["configured"] is False
    assert cap["provider"] == "OpenAI"
    assert cap["requires_consent"] is True
    assert "OpenAI-API-Zugang nicht eingerichtet" in cap["reason"]

    uploaded = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest_a["headers"],
        files={"file": ("holzscheibe.webp", load_real_photo_bytes(), "image/webp")},
        data={"rights_confirmed": "true"},
        timeout=45,
    )
    assert uploaded.status_code == 201
    original_id = uploaded.json()["id"]

    request_id = str(uuid4())
    no_consent = api_client.post(
        f"{BASE_URL}/api/studio/uploads/{original_id}/remove-background",
        headers=guest_a["headers"],
        json={"request_id": request_id, "consent": False},
        timeout=30,
    )
    assert no_consent.status_code == 422

    blocked = api_client.post(
        f"{BASE_URL}/api/studio/uploads/{original_id}/remove-background",
        headers=guest_a["headers"],
        json={"request_id": request_id, "consent": True},
        timeout=30,
    )
    assert blocked.status_code == 503

    bg_request = mongo_db["studio_bg_requests"].find_one(
        {"guest": guest_a["guest"], "request_id": request_id},
        {"_id": 0},
    )
    assert bg_request is None

    foreign = api_client.post(
        f"{BASE_URL}/api/studio/uploads/{original_id}/remove-background",
        headers=guest_b["headers"],
        json={"request_id": str(uuid4()), "consent": True},
        timeout=30,
    )
    assert foreign.status_code == 404


# Module coverage: curated font manifest contract and retired install endpoint
def test_font_catalog_and_install_flow(api_client):
    catalog = api_client.get(f"{BASE_URL}/api/studio/fonts", timeout=30)
    assert catalog.status_code == 200
    body = catalog.json()
    assert body["version"] == "manucreator-curated-1"
    assert len(body["families"]) == 25
    assert sum(len(f["variants"]) for f in body["families"]) == 177

    retired = api_client.post(
        f"{BASE_URL}/api/studio/fonts/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/install",
        timeout=30,
    )
    assert retired.status_code == 404

    for family in body["families"]:
        license_response = api_client.get(f"{BASE_URL}{family['license_url']}", timeout=30)
        assert license_response.status_code == 200
        assert len(license_response.text.strip()) > 20


# Module coverage: text-preview endpoint consistency, umlauts, curvature, and no-fallback invalid font handling
def test_text_preview_endpoint_behavior(api_client):
    guest = create_guest(api_client)

    straight = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=guest["headers"],
        json={"text": "München ÄÖÜ", "font": "sans", "font_size": 36, "curvature": 0},
        timeout=45,
    )
    assert straight.status_code == 200
    straight_body = straight.json()
    assert straight_body["width"] > 0 and straight_body["height"] > 0
    assert straight_body["image"].startswith("data:image/png;base64,")

    curved_up = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=guest["headers"],
        json={"text": "München ÄÖÜ", "font": "sans", "font_size": 36, "curvature": 90},
        timeout=45,
    )
    curved_down = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=guest["headers"],
        json={"text": "München ÄÖÜ", "font": "sans", "font_size": 36, "curvature": -90},
        timeout=45,
    )
    assert curved_up.status_code == 200
    assert curved_down.status_code == 200

    invalid_font = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=guest["headers"],
        json={"text": "Test", "font": "fs:ffffffffffffffffffffffffffffffff", "font_size": 30, "curvature": 0},
        timeout=30,
    )
    assert invalid_font.status_code == 422
    assert "keine Ersatzschrift" in invalid_font.text

    invalid_glyph = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=guest["headers"],
        json={"text": "A\u0001", "font": "sans", "font_size": 30, "curvature": 0},
        timeout=30,
    )
    assert invalid_glyph.status_code == 422


# Module coverage: image proportion persistence (portrait/landscape) and explicit stretch rejection
def test_image_ratio_validation_with_landscape_and_portrait(api_client):
    guest = create_guest(api_client)

    landscape = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("landscape.png", create_png_bytes(1200, 800), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    portrait = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("portrait.png", create_png_bytes(800, 1200), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    assert landscape.status_code == 201
    assert portrait.status_code == 201

    landscape_id = landscape.json()["id"]
    portrait_id = portrait.json()["id"]

    payload = _base_layer_payload("holzscheibe")
    payload["elements"] = [
        {
            "id": "img-landscape",
            "kind": "image",
            "text": "",
            "font": "sans",
            "x": 280,
            "y": 285,
            "w": 180,
            "h": 120,
            "rotation": 0,
            "asset_id": landscape_id,
            "original_asset_id": None,
            "image_type": "photo",
            "image_ratio": 1.5,
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        },
        {
            "id": "img-portrait",
            "kind": "image",
            "text": "",
            "font": "sans",
            "x": 410,
            "y": 300,
            "w": 120,
            "h": 180,
            "rotation": 0,
            "asset_id": portrait_id,
            "original_asset_id": None,
            "image_type": "photo",
            "image_ratio": 2 / 3,
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": False,
        },
    ]

    valid = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=payload, timeout=45)
    assert valid.status_code == 200
    saved = valid.json()["design"]["elements"]
    assert saved[0]["image_ratio"] == pytest.approx(1.5, rel=1e-3)
    assert saved[1]["image_ratio"] == pytest.approx(2 / 3, rel=1e-3)

    stretched = _base_layer_payload("holzscheibe")
    stretched["elements"] = [{**payload["elements"][0], "h": 180, "rotation": 0}]
    stretched_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts",
        headers=guest["headers"],
        json=stretched,
        timeout=45,
    )
    assert stretched_resp.status_code == 422
    assert "proportional" in stretched_resp.text

    legacy_ratio_zero = _base_layer_payload("holzscheibe")
    legacy_ratio_zero["elements"] = [{**payload["elements"][0], "h": 180, "image_ratio": 0, "rotation": 0}]
    legacy_resp = api_client.post(
        f"{BASE_URL}/api/studio/drafts",
        headers=guest["headers"],
        json=legacy_ratio_zero,
        timeout=45,
    )
    assert legacy_resp.status_code == 200


# Module coverage: cross-guest resource authorization and isolation boundaries
def test_guest_isolation_blocks_other_guests_draft_file_and_order_access(api_client, mongo_db):
    guest_a = seed_peer_guest(mongo_db)
    guest_b = seed_peer_guest(mongo_db)

    upload = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest_a["headers"],
        files={"file": ("a.png", create_png_bytes(700, 700), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    assert upload.status_code == 201
    file_id = upload.json()["id"]

    draft = save_text_draft(api_client, guest_a["headers"], text="TEST A", subtitle="A")
    draft_id = draft["id"]

    add_cart = api_client.post(
        f"{BASE_URL}/api/studio/cart",
        headers=guest_a["headers"],
        json={"draft_id": draft_id, "quantity": 1},
        timeout=30,
    )
    assert add_cart.status_code == 200

    order = api_client.post(
        f"{BASE_URL}/api/studio/orders",
        headers=guest_a["headers"],
        json={
            "request_id": str(uuid4()),
            "name": "TEST Guest A",
            "email": "guest.a@example.com",
            "note": "TEST",
            "acknowledge_test": True,
        },
        timeout=35,
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    other_draft = api_client.get(f"{BASE_URL}/api/studio/drafts/{draft_id}", headers=guest_b["headers"], timeout=25)
    assert other_draft.status_code == 404
    other_file = api_client.get(f"{BASE_URL}/api/studio/files/{file_id}", headers=guest_b["headers"], timeout=25)
    assert other_file.status_code == 404
    other_order = api_client.get(f"{BASE_URL}/api/studio/orders/{order_id}", headers=guest_b["headers"], timeout=25)
    assert other_order.status_code == 404


# Module coverage: draft fingerprint caching and no implicit AI invocation
def test_same_design_reuses_draft_id_and_changed_design_creates_new_without_ai(api_client):
    guest = create_guest(api_client)
    payload = {
        "product_id": "holzscheibe",
        "template": "text",
        "text": "TEST Cache",
        "subtitle": "Same",
        "font": "classic",
        "size": "medium",
        "position": "center",
        "asset_id": None,
        "zoom": 1,
        "focal_x": 0,
        "focal_y": 0,
    }
    first = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=payload, timeout=30)
    second = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=payload, timeout=30)
    assert first.status_code == 200 and second.status_code == 200
    one = first.json()
    two = second.json()
    assert one["id"] == two["id"]
    assert one["fingerprint"] == two["fingerprint"]

    changed = {**payload, "text": "TEST Cache Updated"}
    third = api_client.post(f"{BASE_URL}/api/studio/drafts", headers=guest["headers"], json=changed, timeout=30)
    assert third.status_code == 200
    new_draft = third.json()
    assert new_draft["id"] != one["id"]
    assert new_draft["ai_status"] == "none"


# Module coverage: save/reload must preserve layer geometry/crop/hidden/locked/order/font
def test_layered_design_save_and_reload_preserves_state(api_client):
    guest = create_guest(api_client)
    upload = api_client.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=guest["headers"],
        files={"file": ("photo.png", create_png_bytes(900, 620), "image/png")},
        data={"rights_confirmed": "true"},
        timeout=35,
    )
    assert upload.status_code == 201
    asset_id = upload.json()["id"]

    payload = _base_layer_payload("schneidebrett")
    payload["elements"] = [
        {
            "id": "img-1",
            "kind": "image",
            "text": "",
            "font": "sans",
            "x": 290,
            "y": 280,
            "w": 180,
            "h": 130,
            "asset_id": asset_id,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0.12, "y": 0.08, "w": 0.75, "h": 0.7},
            "locked": True,
            "hidden": False,
        },
        {
            "id": "txt-2",
            "kind": "text",
            "text": "TEST Layer State",
            "font": "serif-italic",
            "x": 300,
            "y": 430,
            "w": 200,
            "h": 45,
            "asset_id": None,
            "original_asset_id": None,
            "image_type": "photo",
            "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
            "locked": False,
            "hidden": True,
        },
    ]

    created = api_client.post(
        f"{BASE_URL}/api/studio/drafts",
        headers=guest["headers"],
        json=payload,
        timeout=40,
    )
    assert created.status_code == 200
    draft = created.json()
    assert len(draft["design"]["elements"]) == 2

    loaded = api_client.get(f"{BASE_URL}/api/studio/drafts/{draft['id']}", headers=guest["headers"], timeout=25)
    assert loaded.status_code == 200
    loaded_design = loaded.json()["design"]
    assert loaded_design["elements"] == draft["design"]["elements"]
    assert loaded_design["elements"][0]["locked"] is True
    assert loaded_design["elements"][1]["hidden"] is True
    assert loaded_design["elements"][1]["font"] == "serif-italic"


# Module coverage: retired AI endpoints must stay unavailable after scope change
def test_removed_quota_and_preview_endpoints_return_404(api_client):
    guest = create_guest(api_client)
    draft = save_text_draft(api_client, guest["headers"], text="TEST Confirm", subtitle="Validation")

    quota = api_client.get(f"{BASE_URL}/api/studio/quota", headers=guest["headers"], timeout=20)
    assert quota.status_code == 404

    invalid = api_client.post(
        f"{BASE_URL}/api/studio/drafts/{draft['id']}/preview",
        headers=guest["headers"],
        json={},
        timeout=25,
    )
    assert invalid.status_code == 404

    confirmed = api_client.post(
        f"{BASE_URL}/api/studio/drafts/{draft['id']}/preview",
        headers=guest["headers"],
        json={"confirmed": True},
        timeout=25,
    )
    assert confirmed.status_code == 404

    status = api_client.get(f"{BASE_URL}/api/studio/drafts/{draft['id']}", headers=guest["headers"], timeout=20)
    assert status.status_code == 200
    item = status.json()
    assert item["ai_status"] == "none"


# Module coverage: REAL Gemini generation once + polling + cache reuse no extra quota
@pytest.mark.skip(reason="Skipped per current regression scope: no real image generation run.")
def test_real_ai_generation_once_and_reuse_cached_preview(api_client):
    guest = create_guest(api_client)
    draft = save_text_draft(api_client, guest["headers"], text="TEST AI einmal", subtitle="Nur ein Aufruf")

    before = api_client.get(f"{BASE_URL}/api/studio/quota", headers=guest["headers"], timeout=20)
    assert before.status_code == 200
    before_quota = before.json()

    trigger = api_client.post(
        f"{BASE_URL}/api/studio/drafts/{draft['id']}/preview",
        headers=guest["headers"],
        json={"confirmed": True},
        timeout=35,
    )
    assert trigger.status_code == 200
    start = trigger.json()
    assert start["ai_status"] in {"generating", "ready"}

    deadline = time.time() + 240
    final = start
    while time.time() < deadline:
        poll = api_client.get(f"{BASE_URL}/api/studio/drafts/{draft['id']}", headers=guest["headers"], timeout=20)
        assert poll.status_code == 200
        final = poll.json()
        if final["ai_status"] in {"ready", "failed"}:
            break
        time.sleep(4)

    assert final["ai_status"] == "ready", f"REAL AI failed: {json.dumps(final, ensure_ascii=False)}"
    assert isinstance(final.get("ai_file_id"), str) and final["ai_file_id"]

    blob = api_client.get(f"{BASE_URL}/api/studio/files/{final['ai_file_id']}", headers=guest["headers"], timeout=40)
    assert blob.status_code == 200
    generated = Image.open(io.BytesIO(blob.content))
    assert generated.width > 0 and generated.height > 0

    mid = api_client.get(f"{BASE_URL}/api/studio/quota", headers=guest["headers"], timeout=20).json()
    assert mid["remaining"] == before_quota["remaining"] - 1

    again = api_client.post(
        f"{BASE_URL}/api/studio/drafts/{draft['id']}/preview",
        headers=guest["headers"],
        json={"confirmed": True},
        timeout=25,
    )
    assert again.status_code == 200
    reused = again.json()
    assert reused["ai_status"] == "ready"
    assert reused.get("reused") is True

    after = api_client.get(f"{BASE_URL}/api/studio/quota", headers=guest["headers"], timeout=20).json()
    assert after["remaining"] == mid["remaining"]


# Module coverage: seeded quota documents must not re-enable retired preview route
def test_seeded_quota_documents_do_not_enable_retired_preview_route(api_client, mongo_db):
    guest = create_guest(api_client)
    draft = save_text_draft(api_client, guest["headers"], text="TEST Seeded Limit", subtitle="429")

    today = datetime.now(timezone.utc).date().isoformat()
    quota_id = f"{today}:guest:{guest['guest']}"
    mongo_db["studio_quotas"].update_one(
        {"_id": quota_id},
        {
            "$set": {
                "count": GUEST_LIMIT,
                "expires_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )

    limited = api_client.post(
        f"{BASE_URL}/api/studio/drafts/{draft['id']}/preview",
        headers=guest["headers"],
        json={"confirmed": True},
        timeout=25,
    )
    assert limited.status_code == 404

    quota = api_client.get(f"{BASE_URL}/api/studio/quota", headers=guest["headers"], timeout=20)
    assert quota.status_code == 404

    status = api_client.get(f"{BASE_URL}/api/studio/drafts/{draft['id']}", headers=guest["headers"], timeout=20)
    assert status.status_code == 200
    item = status.json()
    assert item["ai_status"] == "none"

    # cleanup only seeded test quota document
    mongo_db["studio_quotas"].delete_one({"_id": quota_id})


# Module coverage: cart operations, quantity bounds, totals, and item lifecycle
def test_cart_add_edit_remove_and_quantity_constraints(api_client):
    guest = create_guest(api_client)
    draft = save_text_draft(api_client, guest["headers"], product_id="metallanhaenger", text="TEST Cart", subtitle="Flow")

    add = api_client.post(
        f"{BASE_URL}/api/studio/cart",
        headers=guest["headers"],
        json={"draft_id": draft["id"], "quantity": 1},
        timeout=25,
    )
    assert add.status_code == 200
    cart = add.json()
    assert cart["count"] == 1
    assert cart["payable_cents"] == 0
    assert cart["items"][0]["product_name"] == "Metallanhänger"
    item_id = cart["items"][0]["id"]

    patch = api_client.patch(
        f"{BASE_URL}/api/studio/cart/{item_id}",
        headers=guest["headers"],
        json={"quantity": 3},
        timeout=25,
    )
    assert patch.status_code == 200
    patched = patch.json()
    assert patched["count"] == 3
    assert patched["items"][0]["quantity"] == 3
    assert patched["items"][0]["subtotal_cents"] == patched["items"][0]["price_cents"] * 3

    too_high = api_client.patch(
        f"{BASE_URL}/api/studio/cart/{item_id}",
        headers=guest["headers"],
        json={"quantity": 21},
        timeout=25,
    )
    assert too_high.status_code == 422

    removed = api_client.delete(f"{BASE_URL}/api/studio/cart/{item_id}", headers=guest["headers"], timeout=25)
    assert removed.status_code == 200
    after_remove = removed.json()
    assert after_remove["count"] == 0
    assert after_remove["items"] == []


# Module coverage: test-only checkout idempotency, immutable snapshot, and extra field rejection
def test_test_checkout_idempotency_and_tampered_payload_rejection(api_client):
    guest = create_guest(api_client)
    draft = save_text_draft(api_client, guest["headers"], product_id="schneidebrett", text="TEST Checkout", subtitle="Snapshot")

    add = api_client.post(
        f"{BASE_URL}/api/studio/cart",
        headers=guest["headers"],
        json={"draft_id": draft["id"], "quantity": 2},
        timeout=25,
    )
    assert add.status_code == 200
    assert add.json()["count"] == 2

    request_id = str(uuid4())
    payload = {
        "request_id": request_id,
        "name": "TEST Checkout User",
        "email": "checkout.user@example.com",
        "note": "TEST order",
        "acknowledge_test": True,
    }

    first = api_client.post(f"{BASE_URL}/api/studio/orders", headers=guest["headers"], json=payload, timeout=30)
    second = api_client.post(f"{BASE_URL}/api/studio/orders", headers=guest["headers"], json=payload, timeout=30)
    assert first.status_code == 201 and second.status_code == 201
    one = first.json()
    two = second.json()
    assert one["id"] == two["id"]
    assert one["reference"].startswith("TEST-")
    assert one["is_test"] is True
    assert one["payable_cents"] == 0
    assert one["example_total_cents"] > 0
    assert one["items"][0]["quantity"] == 2

    cart_after = api_client.get(f"{BASE_URL}/api/studio/cart", headers=guest["headers"], timeout=20)
    assert cart_after.status_code == 200
    assert cart_after.json()["count"] == 0

    tampered = api_client.post(
        f"{BASE_URL}/api/studio/orders",
        headers=guest["headers"],
        json={
            "request_id": str(uuid4()),
            "name": "TEST Tamper",
            "email": "tamper@example.com",
            "note": "TEST",
            "acknowledge_test": True,
            "price_cents": 1,
        },
        timeout=25,
    )
    assert tampered.status_code == 422

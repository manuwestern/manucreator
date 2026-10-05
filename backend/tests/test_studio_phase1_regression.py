"""Phase1 regression tests: curated fonts, templates, and legacy invalid-draft checkout gating."""

import os
from pathlib import Path
from uuid import uuid4

import jwt
import pytest
import requests
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


def _create_guest(api_client):
    response = api_client.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20)
    assert response.status_code == 200
    data = response.json()
    claims = jwt.decode(data["token"], options={"verify_signature": False})
    return {
        "headers": {"Authorization": f"Bearer {data['token']}"},
        "guest": claims["sub"],
        "refresh": data["refresh_token"],
    }


# Module coverage: curated font manifest and retired install endpoint
def test_curated_fonts_manifest_and_retired_install(api_client):
    response = api_client.get(f"{BASE_URL}/api/studio/fonts", timeout=20)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "manucreator-curated-1"
    assert len(data["families"]) == 25

    variants_count = sum(len(f["variants"]) for f in data["families"])
    assert variants_count == 177

    retired = api_client.post(
        f"{BASE_URL}/api/studio/fonts/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/install",
        timeout=20,
    )
    assert retired.status_code == 404


# Module coverage: curated fonts include key German chars and family license urls are reachable
def test_curated_font_preview_german_chars_and_license_urls(api_client):
    manifest = api_client.get(f"{BASE_URL}/api/studio/fonts", timeout=20).json()
    sample = "ÄÖÜäöüß"
    guest = _create_guest(api_client)
    for family in manifest["families"]:
        license_url = family["license_url"]
        license_response = api_client.get(f"{BASE_URL}{license_url}", timeout=20)
        assert license_response.status_code == 200
        assert len(license_response.text.strip()) > 10

        default_face = family["default"]
        preview = api_client.post(
            f"{BASE_URL}/api/studio/text-preview",
            headers=guest["headers"],
            json={"text": sample, "font": default_face, "font_size": 42, "curvature": 0},
            timeout=35,
        )
        assert preview.status_code == 200
        payload = preview.json()
        assert payload["width"] > 0
        assert payload["height"] > 0
        assert payload["image"].startswith("data:image/png;base64,")


# Module coverage: templates catalog/preview and guest-protected apply
def test_templates_list_preview_and_apply_protection(api_client):
    listed = api_client.get(f"{BASE_URL}/api/studio/templates?product_id=holzscheibe", timeout=30)
    assert listed.status_code == 200
    payload = listed.json()
    items = payload["items"]
    assert payload["catalog_count"] == 40
    assert payload["collections"] == {"holz": 16, "metall": 14, "universell": 10}
    assert len(items) == 26
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))

    for item in items:
        preview = api_client.get(f"{BASE_URL}{item['preview']}", timeout=35)
        assert preview.status_code == 200
        assert preview.headers.get("content-type", "").startswith("image/png")
        assert len(preview.content) > 5000

        unauthorized = api_client.post(
            f"{BASE_URL}/api/studio/templates/{item['id']}/apply",
            json={"product_id": "holzscheibe"},
            timeout=20,
        )
        assert unauthorized.status_code == 401


# Module coverage: apply template returns simple mode with expected placeholders/text slots
def test_apply_template_returns_simple_design_shape(api_client):
    guest = _create_guest(api_client)
    listed = api_client.get(f"{BASE_URL}/api/studio/templates?product_id=holzscheibe", timeout=30)
    assert listed.status_code == 200
    ids = [item["id"] for item in listed.json()["items"]]
    for identity in ids:
        response = api_client.post(
            f"{BASE_URL}/api/studio/templates/{identity}/apply",
            headers=guest["headers"],
            json={"product_id": "holzscheibe"},
            timeout=30,
        )
        assert response.status_code == 200
        design = response.json()
        assert design["editor_mode"] == "simple"
        assert design["template_id"] == identity
        assert design["product_id"] == "holzscheibe"
        assert isinstance(design["elements"], list) and len(design["elements"]) >= 2

        if identity in {"photo", "company"}:
            placeholders = [e for e in design["elements"] if e["kind"] == "image"]
            assert placeholders
            assert any(e["placeholder"] is True for e in placeholders)


# Module coverage: legacy invalid drafts are preserved but blocked during cart/checkout revalidation
def test_legacy_invalid_draft_is_blocked_by_cart_check_available(api_client, mongo_db):
    guest = _create_guest(api_client)
    products_response = api_client.get(f"{BASE_URL}/api/studio/products", timeout=20)
    assert products_response.status_code == 200
    products_payload = products_response.json()
    current_product = next(
        (p for p in products_payload.get("products", []) if p.get("id") == "holzscheibe"),
        None,
    )
    assert current_product is not None

    draft_id = uuid4().hex
    invalid_element = {
        "id": "legacy-bad",
        "kind": "text",
        "text": "TEST",
        "font": "curated:open-sans:400:normal",
        "font_size": 40,
        "rotation": 0,
        "curvature": 0,
        "x": -120,
        "y": -120,
        "w": 260,
        "h": 100,
        "asset_id": None,
        "original_asset_id": None,
        "image_type": "photo",
        "image_ratio": 0,
        "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
        "locked": False,
        "hidden": False,
        "placeholder": False,
        "template_field": None,
        "field_label": None,
        "template_slot": None,
    }
    legacy_doc = {
        "id": draft_id,
        "guest": guest["guest"],
        "design": {
            "product_id": "holzscheibe",
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
            "elements": [invalid_element],
            "editor_mode": "free",
            "template_id": None,
            "template_version": None,
            "font_catalog_version": "manucreator-curated-1",
        },
        "product_snapshot": {
            "id": "holzscheibe",
            "name": "TEST snapshot",
            "version": current_product["version"],
            "price_cents": current_product["price_cents"],
        },
    }
    mongo_db["studio_drafts"].insert_one(legacy_doc)
    try:
        add = api_client.post(
            f"{BASE_URL}/api/studio/cart",
            headers=guest["headers"],
            json={"draft_id": draft_id, "quantity": 1},
            timeout=25,
        )
        assert add.status_code == 409
        detail = add.json().get("detail", "").lower()
        assert "korrigiert" in detail
        assert "abschluss" in detail
    finally:
        mongo_db["studio_cart"].delete_many({"guest": guest["guest"]})
        mongo_db["studio_drafts"].delete_one({"id": draft_id, "guest": guest["guest"]})

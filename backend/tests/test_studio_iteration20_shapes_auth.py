"""Iteration 20: shape APIs/validation, circular bounds, and admin auth security checks."""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from uuid import uuid4

import pytest
import requests
from PIL import Image
from pymongo import MongoClient

from test_studio_iteration18_templates_decorations import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    BASE_URL,
    ORIGIN,
    _create_product,
    _update_product,
)

pytest_plugins = ['test_studio_iteration18_templates_decorations']


def _load_env_value(env_path: Path, key: str) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    raise RuntimeError(f"Missing {key} in {env_path}")


MONGO_URL = _load_env_value(Path("/app/backend/.env"), "MONGO_URL")
DB_NAME = _load_env_value(Path("/app/backend/.env"), "DB_NAME")


@pytest.fixture(scope="session")
def mongo_db():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=7000)
    database = client[DB_NAME]
    try:
        yield database
    finally:
        client.close()


@pytest.fixture
def guest_headers():
    response = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20)
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def _decode_preview_image(payload: dict) -> Image.Image:
    encoded = payload["image"].split(",", 1)[1]
    data = base64.b64decode(encoded)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def _base_shape(shape_type: str, mode: str = "filled") -> dict:
    presets = {
        "line": {"w": 180, "h": 2, "stroke_width": 2, "shape_mode": "outline"},
        "circle": {"w": 180, "h": 180, "stroke_width": 4, "shape_mode": mode},
        "rectangle": {"w": 200, "h": 120, "stroke_width": 4, "shape_mode": mode},
        "heart": {"w": 176, "h": 160, "stroke_width": 3, "shape_mode": mode},
        "triangle": {"w": 184.75208614068026, "h": 160, "stroke_width": 3, "shape_mode": mode},
        "star": {"w": 168.23395587812272, "h": 160, "stroke_width": 3, "shape_mode": mode},
    }
    return {"shape_type": shape_type, **presets[shape_type]}


def _shape_element(identity: str, shape_type: str, x: float, y: float, w: float, h: float, stroke_width: float, shape_mode="filled"):
    return {
        "id": identity,
        "kind": "shape",
        "shape_type": shape_type,
        "shape_mode": shape_mode,
        "shape_proportional": shape_type != "rectangle",
        "ornament": None,
        "stroke_width": stroke_width,
        "decoration_id": None,
        "field_required": False,
        "field_max_length": None,
        "text": "",
        "font": "curated:open-sans:400:normal",
        "font_size": 0,
        "rotation": 0,
        "curvature": 0,
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
        "x": x,
        "y": y,
        "w": w,
        "h": h,
    }


# Module coverage: /shape-preview six basics and mode rendering keeps transparent outline centers
def test_shape_preview_renders_all_six_types_with_expected_centers():
    for shape_type in ["line", "circle", "rectangle", "heart", "triangle", "star"]:
        filled_payload = _base_shape(shape_type, mode="filled")
        filled = requests.post(f"{BASE_URL}/api/studio/shape-preview", json=filled_payload, timeout=25)
        assert filled.status_code == 200, filled.text
        filled_data = filled.json()
        assert filled_data["width"] == round(filled_payload["w"])
        assert filled_data["height"] == round(filled_payload["h"])
        assert filled_data["image"].startswith("data:image/png;base64,")

        filled_image = _decode_preview_image(filled_data)
        cx, cy = filled_image.width // 2, filled_image.height // 2
        filled_center_alpha = filled_image.getpixel((cx, cy))[3]
        assert filled_center_alpha > 0

        if shape_type == "line":
            continue

        outline_payload = _base_shape(shape_type, mode="outline")
        outlined = requests.post(f"{BASE_URL}/api/studio/shape-preview", json=outline_payload, timeout=25)
        assert outlined.status_code == 200, outlined.text
        outlined_image = _decode_preview_image(outlined.json())
        ocx, ocy = outlined_image.width // 2, outlined_image.height // 2
        outline_center_alpha = outlined_image.getpixel((ocx, ocy))[3]
        assert outline_center_alpha == 0


# Module coverage: /shape-preview validation errors for ratios, line constraints, stroke and non-finite values
def test_shape_preview_rejects_invalid_constraints_with_422():
    invalid_payloads = [
        {"shape_type": "line", "shape_mode": "outline", "w": 160, "h": 8, "stroke_width": 2},
        {"shape_type": "circle", "shape_mode": "filled", "w": 160, "h": 140, "stroke_width": 2},
        {"shape_type": "triangle", "shape_mode": "filled", "w": 160, "h": 160, "stroke_width": 2},
        {"shape_type": "circle", "shape_mode": "outline", "w": 30, "h": 30, "stroke_width": 11},
        {"shape_type": "rectangle", "shape_mode": "outline", "w": 6, "h": 6, "stroke_width": 2.8},
        {"shape_type": "star", "shape_mode": "filled", "w": "NaN", "h": 120, "stroke_width": 2},
    ]
    for payload in invalid_payloads:
        response = requests.post(f"{BASE_URL}/api/studio/shape-preview", json=payload, timeout=25)
        assert response.status_code == 422, response.text


# Module coverage: circle preview alpha stays within circular contour (no square-corner ink bleed)
def test_circle_preview_alpha_stays_within_outer_radius():
    payload = {"shape_type": "circle", "shape_mode": "outline", "w": 240, "h": 240, "stroke_width": 6}
    response = requests.post(f"{BASE_URL}/api/studio/shape-preview", json=payload, timeout=25)
    assert response.status_code == 200, response.text
    image = _decode_preview_image(response.json())
    cx = (image.width - 1) / 2
    cy = (image.height - 1) / 2
    radius = image.width / 2
    pad = 0.85

    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            alpha = pixels[x, y][3]
            if alpha == 0:
                continue
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            assert distance <= radius + pad


# Module coverage: shape-only drafts allowed and >12 total layers blocked
def test_shape_only_draft_save_allowed_but_layer_limit_enforced(guest_headers):
    base = {
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
        "elements": [
            _shape_element(
                "shape-only-circle",
                "circle",
                x=300,
                y=300,
                w=200,
                h=200,
                stroke_width=3,
                shape_mode="outline",
            )
        ],
        "editor_mode": "free",
        "template_id": None,
        "template_version": None,
        "template_revision_id": None,
        "allow_free_edit": True,
        "font_catalog_version": "manucreator-curated-1",
    }

    save_ok = requests.post(f"{BASE_URL}/api/studio/drafts", headers=guest_headers, json=base, timeout=35)
    assert save_ok.status_code == 200, save_ok.text
    assert save_ok.json().get("id")

    too_many = dict(base)
    too_many["elements"] = [
        _shape_element(
            f"shape-{index}",
            "line" if index % 2 else "rectangle",
            x=220,
            y=220 + index,
            w=160 if index % 2 else 120,
            h=2 if index % 2 else 90,
            stroke_width=2,
            shape_mode="outline",
        )
        for index in range(13)
    ]
    save_limit = requests.post(f"{BASE_URL}/api/studio/drafts", headers=guest_headers, json=too_many, timeout=35)
    assert save_limit.status_code == 422


# Module coverage: circular shape boundary checks use outer disk (not bounding square)
def test_circle_shape_inside_circular_area_uses_disk_envelope(admin_session, created_ids, guest_headers):
    product = _create_product(admin_session, created_ids, show_basic_templates=True)
    product = _update_product(
        admin_session,
        product,
        area={"x": 200, "y": 200, "w": 400, "h": 400, "shape": "circle"},
        area_mm="Ø 80 mm",
    )

    radius = product["area"]["w"] / 2
    shape_diameter = 180
    shape_radius = shape_diameter / 2
    center_x = product["area"]["x"] + radius + (radius - shape_radius - 0.5)
    center_y = product["area"]["y"] + radius
    inside_x = center_x - shape_radius
    inside_y = center_y - shape_radius

    inside_design = {
        "product_id": product["id"],
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
        "elements": [
            _shape_element(
                "circle-near-edge",
                "circle",
                x=inside_x,
                y=inside_y,
                w=shape_diameter,
                h=shape_diameter,
                stroke_width=4,
                shape_mode="outline",
            )
        ],
        "editor_mode": "free",
        "template_id": None,
        "template_version": None,
        "template_revision_id": None,
        "allow_free_edit": True,
        "font_catalog_version": "manucreator-curated-1",
    }

    accepted = requests.post(f"{BASE_URL}/api/studio/drafts", headers=guest_headers, json=inside_design, timeout=35)
    assert accepted.status_code == 200, accepted.text

    outside_design = dict(inside_design)
    outside = dict(inside_design["elements"][0])
    outside["x"] = inside_x + 2.2
    outside_design["elements"] = [outside]
    rejected = requests.post(f"{BASE_URL}/api/studio/drafts", headers=guest_headers, json=outside_design, timeout=35)
    assert rejected.status_code == 422


# Module coverage: admin auth cookies/cors/bcrypt and brute-force lockout threshold
def test_admin_auth_cookie_cors_and_lockout(mongo_db):
    admin = mongo_db["studio_admins"].find_one({"email": ADMIN_EMAIL.lower()}, {"_id": 0, "password_hash": 1})
    assert admin is not None
    assert admin["password_hash"].startswith("$2b$")

    session = requests.Session()
    login = session.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=25,
    )
    assert login.status_code == 200, login.text
    assert "admin_access" in session.cookies.get_dict()
    assert "admin_refresh" in session.cookies.get_dict()
    set_cookie = login.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=none" in set_cookie.lower() or "SameSite=None" in set_cookie
    assert login.headers.get("access-control-allow-credentials") == "true"

    me_ok = session.get(f"{BASE_URL}/api/admin/auth/me", headers={"Origin": ORIGIN}, timeout=20)
    assert me_ok.status_code == 200

    me_without_cookie = requests.get(f"{BASE_URL}/api/admin/auth/me", headers={"Origin": ORIGIN}, timeout=20)
    assert me_without_cookie.status_code == 401

    bad_email = f"lock-{uuid4().hex[:10]}@example.com"
    statuses = []
    for _ in range(6):
        attempt = requests.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers={"Origin": ORIGIN},
            json={"email": bad_email, "password": "wrong-password"},
            timeout=20,
        )
        statuses.append(attempt.status_code)
    assert 429 in statuses

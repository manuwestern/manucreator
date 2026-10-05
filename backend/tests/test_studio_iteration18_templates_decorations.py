"""Iteration 18 backend regression: admin decoration uploads, article templates, and guest restrictions."""

from __future__ import annotations

import io
import os
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

import pytest
import requests
from PIL import Image, ImageDraw
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
ORIGIN = BASE_URL
ADMIN_EMAIL = _load_env_value(Path("/app/backend/.env"), "ADMIN_EMAIL")
ADMIN_PASSWORD = _load_env_value(Path("/app/backend/.env"), "ADMIN_PASSWORD")
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


@pytest.fixture(scope="session")
def admin_session():
    session = requests.Session()
    login = session.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=25,
    )
    if login.status_code != 200:
        pytest.skip(f"Admin login failed: {login.status_code} {login.text}")
    session.headers.update({"Origin": ORIGIN})
    return session


@pytest.fixture
def guest_headers():
    response = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20)
    assert response.status_code == 200
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def created_ids(mongo_db):
    tracker = {
        "products": set(),
        "templates": set(),
        "template_revisions": set(),
        "decorations": set(),
        "drafts": set(),
        "cart": set(),
        "files": set(),
    }
    yield tracker

    if tracker["cart"]:
        mongo_db["studio_cart"].delete_many({"id": {"$in": list(tracker["cart"])}})
    if tracker["drafts"]:
        mongo_db["studio_drafts"].delete_many({"id": {"$in": list(tracker["drafts"])}})
    if tracker["template_revisions"]:
        mongo_db["studio_template_revisions"].delete_many({"id": {"$in": list(tracker["template_revisions"])}})
    if tracker["templates"]:
        mongo_db["studio_article_templates"].delete_many({"id": {"$in": list(tracker["templates"])}})
    if tracker["decorations"]:
        mongo_db["studio_decorations"].delete_many({"id": {"$in": list(tracker["decorations"])}})
        mongo_db["studio_decoration_grants"].delete_many({"decoration_id": {"$in": list(tracker["decorations"])}})
    if tracker["products"]:
        mongo_db["studio_products"].delete_many({"id": {"$in": list(tracker["products"])}})
    if tracker["files"]:
        mongo_db["studio_files"].delete_many({"id": {"$in": list(tracker["files"])}})


def _png_bytes(mode: str = "RGBA", size=(320, 240), alpha_shape: bool = True) -> bytes:
    image = Image.new(mode, size, (0, 0, 0, 0) if mode == "RGBA" else (255, 255, 255))
    if mode == "RGBA" and alpha_shape:
        draw = ImageDraw.Draw(image)
        draw.rectangle((20, 20, size[0] - 20, size[1] - 20), fill=(0, 0, 0, 200))
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _svg_safe_triangle() -> bytes:
    return b"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>
  <path d='M10 110 L60 10 L110 110 Z' fill='#000000'/>
</svg>"""


def _svg_unsafe_text() -> bytes:
    return b"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>
  <text x='10' y='40'>UNSAFE</text>
</svg>"""


def _upload_product_photo(admin: requests.Session, created_ids: dict) -> str:
    payload = _png_bytes(mode="RGB", size=(800, 800), alpha_shape=False)
    response = admin.post(
        f"{BASE_URL}/api/admin/products/photo",
        files={"file": ("TEST_product.png", payload, "image/png")},
        timeout=35,
    )
    assert response.status_code == 201, response.text
    file_id = response.json()["id"]
    created_ids["files"].add(file_id)
    return file_id


def _create_product(admin: requests.Session, created_ids: dict, *, show_basic_templates: bool = True, decoration_ids=None) -> dict:
    if decoration_ids is None:
        decoration_ids = []
    photo_id = _upload_product_photo(admin, created_ids)
    payload = {
        "name": f"TEST_iter18_product_{uuid4().hex[:8]}",
        "subtitle": "",
        "material": "Holz",
        "category": "holz",
        "price_cents": 1990,
        "dimensions": "120 x 120 x 10 mm",
        "area_mm": "80 x 80 mm",
        "max_text": 30,
        "area": {"x": 200, "y": 200, "w": 400, "h": 400, "shape": "rect"},
        "ink": "#493627",
        "templates": ["text", "photo", "logo"],
        "image_file_id": photo_id,
        "active": True,
        "is_sample": True,
        "version": 1,
        "show_basic_templates": show_basic_templates,
        "decoration_ids": decoration_ids,
    }
    response = admin.post(f"{BASE_URL}/api/admin/products", json=payload, timeout=35)
    assert response.status_code == 201, response.text
    product = response.json()
    created_ids["products"].add(product["id"])
    return product


def _update_product(admin: requests.Session, product: dict, **changes) -> dict:
    payload = {
        "name": product["name"],
        "subtitle": product.get("subtitle", ""),
        "material": product["material"],
        "category": product["category"],
        "price_cents": product["price_cents"],
        "dimensions": product["dimensions"],
        "area_mm": product["area_mm"],
        "max_text": product["max_text"],
        "area": product["area"],
        "ink": product["ink"],
        "templates": product["templates"],
        "image_file_id": product["image_file_id"],
        "active": product["active"],
        "is_sample": product["is_sample"],
        "version": product["version"],
        "show_basic_templates": product.get("show_basic_templates", True),
        "decoration_ids": product.get("decoration_ids", []),
    }
    payload.update(changes)
    response = admin.put(f"{BASE_URL}/api/admin/products/{product['id']}", json=payload, timeout=35)
    assert response.status_code == 200, response.text
    return response.json()


def _upload_decoration(admin: requests.Session, created_ids: dict, name: str, file_name: str, content: bytes, mime: str) -> dict:
    response = admin.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": name},
        files={"file": (file_name, content, mime)},
        timeout=35,
    )
    assert response.status_code == 201, response.text
    item = response.json()
    created_ids["decorations"].add(item["id"])
    return item


def _base_design(product_id: str) -> dict:
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
        "elements": [],
        "editor_mode": "free",
        "template_id": None,
        "template_version": None,
        "template_revision_id": None,
        "allow_free_edit": False,
        "font_catalog_version": "manucreator-curated-1",
    }


def _text_element(**overrides) -> dict:
    base = {
        "id": f"txt-{uuid4().hex[:8]}",
        "kind": "text",
        "x": 250,
        "y": 360,
        "w": 220,
        "h": 70,
        "ornament": None,
        "stroke_width": 1.5,
        "decoration_id": None,
        "field_required": True,
        "field_max_length": 24,
        "text": "Max",
        "font": "curated:open-sans:400:normal",
        "font_size": 34,
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
        "template_field": f"field-{uuid4().hex[:6]}",
        "field_label": "Name",
        "template_slot": {"x": 230, "y": 330, "w": 260, "h": 120},
    }
    base.update(overrides)
    return base


def _image_element(**overrides) -> dict:
    base = {
        "id": f"img-{uuid4().hex[:8]}",
        "kind": "image",
        "x": 280,
        "y": 230,
        "w": 180,
        "h": 110,
        "ornament": None,
        "stroke_width": 1.5,
        "decoration_id": None,
        "field_required": False,
        "field_max_length": None,
        "text": "",
        "font": "sans",
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
        "placeholder": True,
        "template_field": f"field-{uuid4().hex[:6]}",
        "field_label": "Dein Foto",
        "template_slot": {"x": 270, "y": 220, "w": 200, "h": 140},
    }
    base.update(overrides)
    return base


def _create_template(admin: requests.Session, created_ids: dict, product_id: str, elements: list[dict], allow_free_edit: bool = False, name: str | None = None) -> dict:
    design = _base_design(product_id)
    design["elements"] = elements
    payload = {
        "name": name or f"TEST_tpl_{uuid4().hex[:8]}",
        "design": design,
        "allow_free_edit": allow_free_edit,
        "sort_order": 0,
        "revision": 1,
    }
    response = admin.post(f"{BASE_URL}/api/admin/article-templates", json=payload, timeout=35)
    assert response.status_code == 201, response.text
    item = response.json()
    created_ids["templates"].add(item["id"])
    return item


def _publish_template(admin: requests.Session, created_ids: dict, template_id: str, revision: int) -> dict:
    response = admin.post(
        f"{BASE_URL}/api/admin/article-templates/{template_id}/publish",
        json={"revision": revision},
        timeout=35,
    )
    assert response.status_code == 200, response.text
    item = response.json()
    if item.get("published_revision_id"):
        created_ids["template_revisions"].add(item["published_revision_id"])
    return item


# Module coverage: auth origin/cookies/hash format
def test_admin_auth_origin_cookie_and_bcrypt_format(mongo_db):
    admin = mongo_db["studio_admins"].find_one({"email": ADMIN_EMAIL.lower()}, {"_id": 0, "password_hash": 1})
    assert admin and admin["password_hash"].startswith("$2b$")

    no_origin = requests.post(
        f"{BASE_URL}/api/admin/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert no_origin.status_code == 403

    with_origin = requests.post(
        f"{BASE_URL}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=20,
    )
    assert with_origin.status_code == 200
    set_cookie = with_origin.headers.get("set-cookie", "")
    assert "admin_access=" in set_cookie and "HttpOnly" in set_cookie and "Secure" in set_cookie


# Module coverage: lockout after repeated failed admin login on same account key
def test_admin_login_lockout_after_five_failed_attempts():
    fake_email = f"lockout_{uuid4().hex[:8]}@example.com"
    statuses = []
    for _ in range(6):
        response = requests.post(
            f"{BASE_URL}/api/admin/auth/login",
            headers={"Origin": ORIGIN},
            json={"email": fake_email, "password": "incorrect-pass"},
            timeout=20,
        )
        statuses.append(response.status_code)
    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429


# Module coverage: strict decoration upload normalization/validation rules
def test_admin_decoration_upload_validations(admin_session, created_ids):
    ok_png = _upload_decoration(
        admin_session,
        created_ids,
        name=f"TEST_png_{uuid4().hex[:6]}",
        file_name="ok.png",
        content=_png_bytes(mode="RGBA", size=(340, 240), alpha_shape=True),
        mime="image/png",
    )
    assert ok_png["state"] == "draft"
    assert ok_png["confirmed"] is False

    no_alpha = admin_session.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": f"TEST_no_alpha_{uuid4().hex[:6]}"},
        files={"file": ("opaque.png", _png_bytes(mode="RGB", size=(300, 240), alpha_shape=False), "image/png")},
        timeout=35,
    )
    assert no_alpha.status_code == 422

    fully_transparent = admin_session.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": f"TEST_empty_alpha_{uuid4().hex[:6]}"},
        files={"file": ("empty.png", _png_bytes(mode="RGBA", size=(320, 220), alpha_shape=False), "image/png")},
        timeout=35,
    )
    assert fully_transparent.status_code == 422

    oversized = admin_session.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": f"TEST_large_file_{uuid4().hex[:6]}"},
        files={"file": ("too_big.png", b"0" * (8 * 1024 * 1024 + 64), "image/png")},
        timeout=35,
    )
    assert oversized.status_code == 413

    huge_dimensions = Image.new("RGBA", (5000, 5000), (0, 0, 0, 1))
    huge_out = io.BytesIO()
    huge_dimensions.save(huge_out, format="PNG")
    megapixels = admin_session.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": f"TEST_20mp_{uuid4().hex[:6]}"},
        files={"file": ("large_dim.png", huge_out.getvalue(), "image/png")},
        timeout=35,
    )
    assert megapixels.status_code == 422

    ok_svg = _upload_decoration(
        admin_session,
        created_ids,
        name=f"TEST_svg_{uuid4().hex[:6]}",
        file_name="ok.svg",
        content=_svg_safe_triangle(),
        mime="image/svg+xml",
    )
    assert ok_svg["mime"] == "image/svg+xml"

    unsafe_svg = admin_session.post(
        f"{BASE_URL}/api/admin/decorations/upload",
        data={"name": f"TEST_svg_bad_{uuid4().hex[:6]}"},
        files={"file": ("unsafe.svg", _svg_unsafe_text(), "image/svg+xml")},
        timeout=35,
    )
    assert unsafe_svg.status_code == 422


# Module coverage: private original/sprite protection and grant-based customer asset access
def test_decoration_access_control_and_grant_flow(admin_session, created_ids):
    deco = _upload_decoration(
        admin_session,
        created_ids,
        name=f"TEST_access_{uuid4().hex[:6]}",
        file_name="access.png",
        content=_png_bytes(mode="RGBA", size=(300, 200), alpha_shape=True),
        mime="image/png",
    )

    original_guest = requests.get(f"{BASE_URL}/api/admin/decorations/{deco['id']}/original", timeout=20)
    sprite_guest = requests.get(f"{BASE_URL}/api/admin/decorations/{deco['id']}/sprite", timeout=20)
    assert original_guest.status_code == 401
    assert sprite_guest.status_code == 401

    assert admin_session.post(f"{BASE_URL}/api/admin/decorations/{deco['id']}/confirm", json={"confirmed": True}, timeout=20).status_code == 200
    assert admin_session.post(f"{BASE_URL}/api/admin/decorations/{deco['id']}/publish", timeout=20).status_code == 200

    product = _create_product(admin_session, created_ids, show_basic_templates=False, decoration_ids=[deco["id"]])

    guest_1 = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20).json()["token"]
    guest_2 = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20).json()["token"]
    h1 = {"Authorization": f"Bearer {guest_1}"}
    h2 = {"Authorization": f"Bearer {guest_2}"}

    denied_before_grant = requests.get(f"{BASE_URL}/api/studio/decoration-assets/{deco['id']}", headers=h1, timeout=20)
    assert denied_before_grant.status_code == 403

    offered = requests.get(f"{BASE_URL}/api/studio/own-decorations?product_id={product['id']}", headers=h1, timeout=20)
    assert offered.status_code == 200
    offered_ids = [item["id"] for item in offered.json()["items"]]
    assert deco["id"] in offered_ids

    grant = requests.post(
        f"{BASE_URL}/api/studio/own-decorations/{deco['id']}/use",
        headers=h1,
        json={"product_id": product["id"]},
        timeout=20,
    )
    assert grant.status_code == 200

    allowed = requests.get(f"{BASE_URL}/api/studio/decoration-assets/{deco['id']}", headers=h1, timeout=20)
    denied_other_guest = requests.get(f"{BASE_URL}/api/studio/decoration-assets/{deco['id']}", headers=h2, timeout=20)
    assert allowed.status_code == 200
    assert denied_other_guest.status_code == 403


# Module coverage: legacy prepared decorations removed from customer offering API
def test_studio_decorations_endpoint_is_explicitly_empty(guest_headers):
    response = requests.get(f"{BASE_URL}/api/studio/decorations", headers=guest_headers, timeout=20)
    assert response.status_code == 200
    assert response.json() == {"items": []}


# Module coverage: publish validation on article templates
def test_article_template_publish_validation_failures(admin_session, created_ids):
    product = _create_product(admin_session, created_ids)

    invalid_label = _create_template(
        admin_session,
        created_ids,
        product["id"],
        elements=[_text_element(field_label="")],
    )
    invalid_label_publish = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{invalid_label['id']}/publish",
        json={"revision": invalid_label["revision"]},
        timeout=30,
    )
    assert invalid_label_publish.status_code == 422

    invalid_length = _create_template(
        admin_session,
        created_ids,
        product["id"],
        elements=[_text_element(field_max_length=product["max_text"] + 1)],
    )
    invalid_length_publish = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{invalid_length['id']}/publish",
        json={"revision": invalid_length["revision"]},
        timeout=30,
    )
    assert invalid_length_publish.status_code == 422

    outside_area = _create_template(
        admin_session,
        created_ids,
        product["id"],
        elements=[_text_element(x=40, y=40, template_slot={"x": 40, "y": 40, "w": 160, "h": 80})],
    )
    outside_publish = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{outside_area['id']}/publish",
        json={"revision": outside_area["revision"]},
        timeout=30,
    )
    assert outside_publish.status_code == 422

    custom_deco = _upload_decoration(
        admin_session,
        created_ids,
        name=f"TEST_template_deco_{uuid4().hex[:6]}",
        file_name="deco.png",
        content=_png_bytes(mode="RGBA", size=(260, 180), alpha_shape=True),
        mime="image/png",
    )
    custom_deco_template = _create_template(
        admin_session,
        created_ids,
        product["id"],
        elements=[
            {
                "id": f"deco-{uuid4().hex[:8]}",
                "kind": "decoration",
                "x": 250,
                "y": 250,
                "w": 180,
                "h": 124.615,
                "ornament": "custom",
                "stroke_width": 1.5,
                "decoration_id": custom_deco["id"],
                "field_required": False,
                "field_max_length": None,
                "text": "",
                "font": "sans",
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
                "field_label": "Custom",
                "template_slot": None,
            }
        ],
    )
    unpublished_deco_publish = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{custom_deco_template['id']}/publish",
        json={"revision": custom_deco_template["revision"]},
        timeout=30,
    )
    assert unpublished_deco_publish.status_code == 422


# Module coverage: immutable published revision, republish update, duplicate/sort/archive, and basics toggle
def test_article_template_lifecycle_and_public_listing(admin_session, created_ids):
    product = _create_product(admin_session, created_ids, show_basic_templates=False)
    template = _create_template(admin_session, created_ids, product["id"], elements=[_text_element(text="TEST")], allow_free_edit=False, name="TEST Public V1")
    published = _publish_template(admin_session, created_ids, template["id"], template["revision"])
    assert published["published_revision_id"]

    listed_before = requests.get(f"{BASE_URL}/api/studio/templates?product_id={product['id']}", timeout=25)
    assert listed_before.status_code == 200
    items_before = listed_before.json()["items"]
    assert any(item["id"] == template["id"] and item["name"] == "TEST Public V1" for item in items_before)
    assert all(item.get("own") for item in items_before), "show_basic_templates=false should hide all six basics"

    get_admin = admin_session.get(f"{BASE_URL}/api/admin/article-templates/{template['id']}", timeout=20)
    assert get_admin.status_code == 200
    current = get_admin.json()
    changed_design = deepcopy(current["design"])
    changed_design["elements"][0]["text"] = "UPDATED"

    edited = admin_session.put(
        f"{BASE_URL}/api/admin/article-templates/{template['id']}",
        json={
            "name": "TEST Public V2 Draft",
            "design": changed_design,
            "allow_free_edit": False,
            "sort_order": 0,
            "revision": current["revision"],
        },
        timeout=30,
    )
    assert edited.status_code == 200

    listed_after_draft_edit = requests.get(f"{BASE_URL}/api/studio/templates?product_id={product['id']}", timeout=25).json()["items"]
    public_entry = next(item for item in listed_after_draft_edit if item["id"] == template["id"])
    assert public_entry["name"] == "TEST Public V1"

    republished = _publish_template(admin_session, created_ids, template["id"], edited.json()["revision"])
    listed_after_republish = requests.get(f"{BASE_URL}/api/studio/templates?product_id={product['id']}", timeout=25).json()["items"]
    republished_entry = next(item for item in listed_after_republish if item["id"] == template["id"])
    assert republished_entry["name"] == "TEST Public V2 Draft"
    created_ids["template_revisions"].add(republished["published_revision_id"])

    tightened = _update_product(
        admin_session,
        {**product, "version": product["version"], "show_basic_templates": False},
        area={"x": 360, "y": 360, "w": 120, "h": 120, "shape": "rect"},
        area_mm="35 x 35 mm",
    )
    assert tightened["version"] == product["version"] + 1
    unavailable_after_bounds_change = requests.get(
        f"{BASE_URL}/api/studio/templates?product_id={product['id']}",
        timeout=25,
    ).json()["items"]
    assert all(item["id"] != template["id"] for item in unavailable_after_bounds_change)

    # restore roomy area for duplicate/sort/archive checks in same test
    product = _update_product(
        admin_session,
        tightened,
        area={"x": 200, "y": 200, "w": 400, "h": 400, "shape": "rect"},
        area_mm="80 x 80 mm",
    )

    duplicate = admin_session.post(f"{BASE_URL}/api/admin/article-templates/{template['id']}/duplicate", timeout=25)
    assert duplicate.status_code == 201
    duplicate_item = duplicate.json()
    created_ids["templates"].add(duplicate_item["id"])
    assert duplicate_item["product_id"] == product["id"]

    t1 = admin_session.get(f"{BASE_URL}/api/admin/article-templates/{template['id']}", timeout=20).json()
    moved = admin_session.put(
        f"{BASE_URL}/api/admin/article-templates/{template['id']}",
        json={
            "name": t1["name"],
            "design": t1["design"],
            "allow_free_edit": t1["allow_free_edit"],
            "sort_order": 5,
            "revision": t1["revision"],
        },
        timeout=25,
    )
    assert moved.status_code == 200
    assert moved.json()["sort_order"] == 5

    archived = admin_session.post(f"{BASE_URL}/api/admin/article-templates/{template['id']}/archive", timeout=20)
    assert archived.status_code == 200
    listed_after_archive = requests.get(f"{BASE_URL}/api/studio/templates?product_id={product['id']}", timeout=25).json()["items"]
    assert all(item["id"] != template["id"] for item in listed_after_archive)


# Module coverage: restricted template application/save and forged payload rejection
def test_restricted_template_apply_and_forged_save_rejections(admin_session, created_ids):
    product = _create_product(admin_session, created_ids, show_basic_templates=False)
    template = _create_template(
        admin_session,
        created_ids,
        product["id"],
        elements=[_image_element(), _text_element(text="Mia")],
        allow_free_edit=False,
    )
    _publish_template(admin_session, created_ids, template["id"], template["revision"])

    guest = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20).json()["token"]
    headers = {"Authorization": f"Bearer {guest}"}
    applied = requests.post(
        f"{BASE_URL}/api/studio/article-templates/{template['id']}/apply",
        headers=headers,
        timeout=25,
    )
    assert applied.status_code == 200
    design = applied.json()

    forged_free = deepcopy(design)
    forged_free["editor_mode"] = "free"
    forged_free["allow_free_edit"] = True
    free_attempt = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=forged_free, timeout=30)
    assert free_attempt.status_code == 422

    forged_strip_revision = deepcopy(design)
    forged_strip_revision["template_revision_id"] = None
    strip_attempt = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=forged_strip_revision, timeout=30)
    assert strip_attempt.status_code == 422

    forged_reordered = deepcopy(design)
    forged_reordered["elements"] = list(reversed(forged_reordered["elements"]))
    reorder_attempt = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=forged_reordered, timeout=30)
    assert reorder_attempt.status_code == 422

    image_upload = requests.post(
        f"{BASE_URL}/api/studio/uploads",
        headers=headers,
        data={"rights_confirmed": "true"},
        files={"file": ("customer.png", _png_bytes(mode="RGBA", size=(420, 260), alpha_shape=True), "image/png")},
        timeout=30,
    )
    assert image_upload.status_code == 201, image_upload.text
    upload_id = image_upload.json()["id"]
    created_ids["files"].add(upload_id)

    valid = deepcopy(design)
    for element in valid["elements"]:
        if element["kind"] == "text":
            element["text"] = "Nora"
        if element["kind"] == "image":
            element["asset_id"] = upload_id
            element["placeholder"] = False
            element["original_asset_id"] = None

    saved = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=valid, timeout=35)
    assert saved.status_code == 200, saved.text
    draft = saved.json()
    created_ids["drafts"].add(draft["id"])
    assert draft["design"]["editor_mode"] == "simple"


# Module coverage: old non-current template ids rejected + product version change triggers cart review error
def test_template_id_rejection_and_cart_review_on_product_change(admin_session, created_ids, guest_headers):
    product = _create_product(admin_session, created_ids, show_basic_templates=True)

    own_decorations_empty = requests.get(
        f"{BASE_URL}/api/studio/own-decorations?product_id={product['id']}",
        headers=guest_headers,
        timeout=20,
    )
    assert own_decorations_empty.status_code == 200
    assert own_decorations_empty.json()["items"] == []

    invalid_apply = requests.post(
        f"{BASE_URL}/api/studio/templates/legacy-40-catalog-id/apply",
        headers=guest_headers,
        json={"product_id": product["id"]},
        timeout=20,
    )
    assert invalid_apply.status_code == 422

    free_design = {
        "product_id": product["id"],
        "template": "text",
        "text": "Test",
        "subtitle": "",
        "font": "classic",
        "size": "medium",
        "position": "center",
        "asset_id": None,
        "zoom": 1,
        "focal_x": 0,
        "focal_y": 0,
        "elements": [
            {
                "id": f"txt-{uuid4().hex[:8]}",
                "kind": "text",
                "x": 280,
                "y": 360,
                "w": 180,
                "h": 60,
                "ornament": None,
                "stroke_width": 1.5,
                "decoration_id": None,
                "field_required": False,
                "field_max_length": None,
                "text": "Test",
                "font": "curated:open-sans:400:normal",
                "font_size": 28,
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
            }
        ],
        "editor_mode": "free",
        "template_id": None,
        "template_version": None,
        "template_revision_id": None,
        "allow_free_edit": True,
        "font_catalog_version": "manucreator-curated-1",
    }
    draft = requests.post(f"{BASE_URL}/api/studio/drafts", headers=guest_headers, json=free_design, timeout=35)
    assert draft.status_code == 200, draft.text
    draft_id = draft.json()["id"]
    created_ids["drafts"].add(draft_id)

    updated_product = _update_product(admin_session, product, area_mm="70 x 70 mm")
    assert updated_product["version"] == product["version"] + 1

    cart_add = requests.post(
        f"{BASE_URL}/api/studio/cart",
        headers=guest_headers,
        json={"draft_id": draft_id, "quantity": 1},
        timeout=25,
    )
    assert cart_add.status_code == 409

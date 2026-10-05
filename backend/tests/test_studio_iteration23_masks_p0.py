"""Iteration 23: P0 engraving mask + exclusions regression (validation, persistence, pixel clipping)."""

from __future__ import annotations

import io
import os
import sys
import uuid
from copy import deepcopy
from pathlib import Path

import pytest
import requests
from PIL import Image

sys.path.append("/app/backend")

from studio.engraving_mask import engraving_mask
from studio.layer_rendering import render_layers
from studio.models import Box, Design, Element, Layout
from studio.rendering import render_design


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


@pytest.fixture(scope="session")
def created_ids(mongo_db):
    tracker = {
        "products": set(),
        "files": set(),
        "templates": set(),
        "template_revisions": set(),
        "drafts": set(),
    }
    yield tracker
    if tracker["drafts"]:
        mongo_db["studio_drafts"].delete_many({"id": {"$in": list(tracker["drafts"])}})
    if tracker["template_revisions"]:
        mongo_db["studio_template_revisions"].delete_many({"id": {"$in": list(tracker["template_revisions"])}})
    if tracker["templates"]:
        mongo_db["studio_article_templates"].delete_many({"id": {"$in": list(tracker["templates"])}})
    if tracker["products"]:
        mongo_db["studio_products"].delete_many({"id": {"$in": list(tracker["products"])}})
    if tracker["files"]:
        mongo_db["studio_files"].delete_many({"id": {"$in": list(tracker["files"])}})


def _png_bytes(size=(800, 800)) -> bytes:
    image = Image.new("RGB", size, (245, 246, 242))
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def _upload_product_photo(admin: requests.Session, created_ids: dict) -> str:
    response = admin.post(
        f"{BASE_URL}/api/admin/products/photo",
        files={"file": ("TEST_iter23_product.png", _png_bytes(), "image/png")},
        timeout=35,
    )
    assert response.status_code == 201, response.text
    file_id = response.json()["id"]
    created_ids["files"].add(file_id)
    return file_id


def _product_payload(photo_id: str) -> dict:
    return {
        "name": f"TEST_iter23_mask_{uuid.uuid4().hex[:8]}",
        "subtitle": "",
        "material": "Holz",
        "category": "holz",
        "price_cents": 2290,
        "dimensions": "100 x 100 x 10 mm",
        "area_mm": "80 x 80 mm",
        "max_text": 30,
        "area": {"x": 200, "y": 200, "w": 400, "h": 400, "shape": "rect"},
        "exclusions": [],
        "ink": "#493627",
        "templates": ["text", "photo", "logo"],
        "image_file_id": photo_id,
        "active": True,
        "is_sample": True,
        "version": 1,
        "show_basic_templates": True,
        "decoration_ids": [],
    }


# Module coverage: ProductInput exclusions strict validation (finite/min2/circle equality/in-photo/unique/max24)
def test_product_exclusions_validation_matrix(admin_session, created_ids):
    photo_id = _upload_product_photo(admin_session, created_ids)

    def create_with(exclusions, area=None):
        payload = _product_payload(photo_id)
        payload["exclusions"] = exclusions
        if area:
            payload["area"] = area
        return admin_session.post(f"{BASE_URL}/api/admin/products", json=payload, timeout=35)

    valid = create_with(
        [
            {"id": "hole_rect_ok", "shape": "rect", "x": 20, "y": 20, "w": 80, "h": 70},
            {"id": "hole_circle_ok", "shape": "circle", "x": 650, "y": 650, "w": 80, "h": 80},
        ],
        area={"x": 240, "y": 240, "w": 220, "h": 220, "shape": "rect"},
    )
    assert valid.status_code == 201, valid.text
    created_ids["products"].add(valid.json()["id"])

    invalid_cases = [
        [{"id": "small", "shape": "rect", "x": 20, "y": 20, "w": 1.9, "h": 12}],
        [{"id": "circle_bad", "shape": "circle", "x": 30, "y": 30, "w": 60, "h": 58}],
        [{"id": "outside", "shape": "rect", "x": 780, "y": 780, "w": 40, "h": 40}],
        [
            {"id": "dup", "shape": "rect", "x": 40, "y": 40, "w": 20, "h": 20},
            {"id": "dup", "shape": "rect", "x": 80, "y": 80, "w": 20, "h": 20},
        ],
        [{"id": "nan", "shape": "rect", "x": "NaN", "y": 20, "w": 20, "h": 20}],
        [
            {"id": f"many_{i}", "shape": "rect", "x": (i % 6) * 30, "y": (i // 6) * 30, "w": 20, "h": 20}
            for i in range(25)
        ],
    ]

    for exclusions in invalid_cases:
        response = create_with(exclusions)
        assert response.status_code == 422, response.text


# Module coverage: admin save/reload persistence and legacy default exclusions=[]
def test_product_exclusions_persist_and_default_empty(admin_session, created_ids):
    photo_id = _upload_product_photo(admin_session, created_ids)
    payload = _product_payload(photo_id)

    create = admin_session.post(f"{BASE_URL}/api/admin/products", json=payload, timeout=35)
    assert create.status_code == 201, create.text
    product = create.json()
    created_ids["products"].add(product["id"])
    assert product["exclusions"] == []

    payload_update = deepcopy(product)
    payload_update["exclusions"] = [
        {"id": "holeA", "shape": "rect", "x": 230, "y": 240, "w": 60, "h": 40},
        {"id": "holeB", "shape": "circle", "x": 460, "y": 430, "w": 50, "h": 50},
    ]
    response = admin_session.put(
        f"{BASE_URL}/api/admin/products/{product['id']}",
        json={k: payload_update[k] for k in [
            "name", "subtitle", "material", "category", "price_cents", "dimensions", "area_mm", "max_text", "area",
            "exclusions", "ink", "templates", "image_file_id", "active", "is_sample", "version", "show_basic_templates", "decoration_ids"
        ]},
        timeout=35,
    )
    assert response.status_code == 200, response.text
    updated = response.json()
    assert len(updated["exclusions"]) == 2

    listed = admin_session.get(f"{BASE_URL}/api/admin/products", timeout=30)
    assert listed.status_code == 200
    same = next(item for item in listed.json() if item["id"] == product["id"])
    assert [z["id"] for z in same["exclusions"]] == ["holeA", "holeB"]


# Module coverage: area payload remains strict (no leaked id=area field from canvas drag payload)
def test_area_payload_rejects_extra_id_field(admin_session, created_ids):
    photo_id = _upload_product_photo(admin_session, created_ids)
    payload = _product_payload(photo_id)
    payload["area"] = {"id": "area", "x": 200, "y": 200, "w": 400, "h": 400, "shape": "rect"}
    response = admin_session.post(f"{BASE_URL}/api/admin/products", json=payload, timeout=30)
    assert response.status_code == 422, response.text


# Module coverage: Pillow mask geometry for outer rectangle/circle and overlapping exclusion UNION
def test_engraving_mask_union_overlap_and_circle_outer_clip():
    product_rect = {
        "area": {"x": 100, "y": 100, "w": 500, "h": 500, "shape": "rect"},
        "exclusions": [
            {"id": "h1", "shape": "rect", "x": 220, "y": 220, "w": 220, "h": 180},
            {"id": "h2", "shape": "rect", "x": 320, "y": 260, "w": 220, "h": 180},
        ],
    }
    mask_rect = engraving_mask(product_rect)
    pix = mask_rect.load()
    assert pix[80, 80] == 0  # outside outer area
    assert pix[160, 160] == 255  # inside outer area
    assert pix[360, 300] == 0  # overlap of exclusions stays erased (UNION)

    product_circle = {
        "area": {"x": 100, "y": 100, "w": 500, "h": 500, "shape": "circle"},
        "exclusions": [],
    }
    mask_circle = engraving_mask(product_circle)
    c = mask_circle.load()
    assert c[100, 100] == 0  # corner clipped by circle
    assert c[350, 350] == 255  # center visible


# Module coverage: render_layers clips crossing/rotated content non-destructively (source geometry unchanged)
def test_render_layers_clips_crossing_shapes_without_mutating_source_geometry():
    blank = Image.new("RGB", (800, 800), "#f5f6f2")
    buf = io.BytesIO()
    blank.save(buf, format="PNG")
    blank_bytes = buf.getvalue()

    product = {
        "ink": "#111111",
        "area": {"x": 180, "y": 180, "w": 440, "h": 440, "shape": "rect"},
        "exclusions": [{"id": "hole", "shape": "circle", "x": 330, "y": 330, "w": 140, "h": 140}],
        "templates": ["text", "photo", "logo"],
        "max_text": 60,
    }
    design = Design(
        product_id="dummy",
        template="text",
        text="",
        subtitle="",
        elements=[
            Element(
                id="shape1",
                kind="shape",
                shape_type="rectangle",
                shape_mode="filled",
                x=120,
                y=320,
                w=420,
                h=120,
                rotation=22,
            )
        ],
    )
    before = design.elements[0].model_dump()
    image = Image.open(io.BytesIO(render_layers(design, product, blank_bytes, assets={}))).convert("RGB")
    after = design.elements[0].model_dump()

    assert before == after
    assert image.getpixel((390, 390)) == (245, 246, 242)  # exclusion hole stays blank


# Module coverage: legacy render_free path still applies engraving mask
def test_render_free_path_uses_mask_for_outside_and_holes():
    blank = Image.new("RGB", (800, 800), "#f5f6f2")
    buf = io.BytesIO()
    blank.save(buf, format="PNG")

    product = {
        "id": "dummy",
        "ink": "#111111",
        "area": {"x": 260, "y": 260, "w": 280, "h": 280, "shape": "rect"},
        "exclusions": [{"id": "inner-hole", "shape": "rect", "x": 360, "y": 360, "w": 80, "h": 80}],
        "templates": ["text", "photo", "logo"],
        "max_text": 60,
    }

    design = Design(
        product_id="dummy",
        template="text",
        text="MASK",
        subtitle="OUT",
        font="classic",
        layout=Layout(
            text=Box(x=220, y=220, w=280, h=120),
            subtitle=Box(x=260, y=470, w=220, h=70),
            image=Box(x=0, y=0, w=10, h=10),
        ),
    )
    rendered = Image.open(io.BytesIO(render_design(design, None, product, buf.getvalue()))).convert("RGB")

    assert rendered.getpixel((120, 120)) == (245, 246, 242)  # outside engraving area untouched
    assert rendered.getpixel((390, 390)) == (245, 246, 242)  # hole untouched


# Module coverage: own template publish/apply with crossing fixed shape + editable text slot remains valid
def test_own_template_with_crossing_fixed_shape_and_editable_text_can_publish_and_save(admin_session, created_ids):
    photo_id = _upload_product_photo(admin_session, created_ids)
    payload = _product_payload(photo_id)
    payload["exclusions"] = [{"id": "mid-hole", "shape": "circle", "x": 350, "y": 350, "w": 100, "h": 100}]
    product_create = admin_session.post(f"{BASE_URL}/api/admin/products", json=payload, timeout=35)
    assert product_create.status_code == 201, product_create.text
    product = product_create.json()
    created_ids["products"].add(product["id"])

    template_payload = {
        "name": f"TEST_iter23_template_{uuid.uuid4().hex[:6]}",
        "allow_free_edit": False,
        "sort_order": 0,
        "revision": 1,
        "design": {
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
            "editor_mode": "free",
            "template_id": None,
            "template_version": None,
            "template_revision_id": None,
            "allow_free_edit": False,
            "font_catalog_version": "manucreator-curated-1",
            "elements": [
                {
                    "id": "fixed-shape-1",
                    "kind": "shape",
                    "shape_type": "rectangle",
                    "shape_mode": "outline",
                    "shape_proportional": False,
                    "x": 260,
                    "y": 330,
                    "w": 280,
                    "h": 140,
                    "ornament": None,
                    "stroke_width": 4,
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
                    "locked": True,
                    "hidden": False,
                    "placeholder": False,
                    "template_field": None,
                    "field_label": "Rahmen",
                    "template_slot": None,
                },
                {
                    "id": "editable-text-1",
                    "kind": "text",
                    "x": 300,
                    "y": 360,
                    "w": 180,
                    "h": 70,
                    "ornament": None,
                    "stroke_width": 1.5,
                    "decoration_id": None,
                    "field_required": True,
                    "field_max_length": 24,
                    "text": "MAX",
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
                    "template_field": "name-slot",
                    "field_label": "Name",
                    "template_slot": {"x": 290, "y": 350, "w": 220, "h": 100},
                },
            ],
        },
    }
    template_create = admin_session.post(f"{BASE_URL}/api/admin/article-templates", json=template_payload, timeout=40)
    assert template_create.status_code == 201, template_create.text
    tpl = template_create.json()
    created_ids["templates"].add(tpl["id"])

    published = admin_session.post(
        f"{BASE_URL}/api/admin/article-templates/{tpl['id']}/publish",
        json={"revision": tpl["revision"]},
        timeout=35,
    )
    assert published.status_code == 200, published.text
    pub = published.json()
    if pub.get("published_revision_id"):
        created_ids["template_revisions"].add(pub["published_revision_id"])

    session_response = requests.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20)
    assert session_response.status_code == 200
    guest = session_response.json()["token"]
    headers = {"Authorization": f"Bearer {guest}"}

    applied = requests.post(f"{BASE_URL}/api/studio/article-templates/{tpl['id']}/apply", headers=headers, timeout=35)
    assert applied.status_code == 200, applied.text
    design = applied.json()

    for element in design["elements"]:
        if element.get("template_field") == "name-slot":
            element["text"] = "NORA"

    save_ok = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=design, timeout=40)
    assert save_ok.status_code == 200, save_ok.text
    created_ids["drafts"].add(save_ok.json()["id"])

    # protection must stay enforced: tampering fixed shape should still fail
    tampered = deepcopy(design)
    for element in tampered["elements"]:
        if element["kind"] == "shape":
            element["rotation"] = 20
            break
    save_bad = requests.post(f"{BASE_URL}/api/studio/drafts", headers=headers, json=tampered, timeout=35)
    assert save_bad.status_code == 422

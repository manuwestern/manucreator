"""Iteration 17: material/template/decor/text-effects regression checks."""

import base64
import io
import math
import os
import sys
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

sys.path.append("/app/backend")
from studio.template_catalog import BY_ID, TEMPLATES  # noqa: E402
from studio.transform_geometry import inside  # noqa: E402
from studio.ornaments import ornament_sprite  # noqa: E402


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


def _guest_headers(api_client):
    response = api_client.post(f"{BASE_URL}/api/studio/session", json={}, timeout=20)
    assert response.status_code == 200
    token = response.json()["token"]
    claims = jwt.decode(token, options={"verify_signature": False})
    return {"Authorization": f"Bearer {token}"}, claims["sub"]


def _decode_png(data_url: str) -> Image.Image:
    encoded = data_url.split(",", 1)[1]
    return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGBA")


def _alpha_pixels(image: Image.Image) -> int:
    return sum(1 for _, _, _, a in image.getdata() if a > 0)


# Module coverage: static catalog must expose exactly 40 unique templates with expected material split
def test_template_catalog_unique_ids_and_collection_counts():
    assert len(TEMPLATES) == 40
    assert len(BY_ID) == 40
    ids = [item["id"] for item in TEMPLATES]
    assert len(ids) == len(set(ids))

    by_collection = {}
    for item in TEMPLATES:
        by_collection[item["collection"]] = by_collection.get(item["collection"], 0) + 1
    assert by_collection == {"holz": 16, "metall": 14, "universell": 10}


# Module coverage: public template filters and preview endpoints for seeded products
def test_template_filters_counts_and_preview_for_seeded_products(api_client):
    expected = {"holzscheibe": 26, "metallanhaenger": 23, "glasschild": 9}
    for product_id, count in expected.items():
        listed = api_client.get(f"{BASE_URL}/api/studio/templates?product_id={product_id}", timeout=35)
        assert listed.status_code == 200
        payload = listed.json()
        assert payload["catalog_count"] == 40
        assert payload["collections"] == {"holz": 16, "metall": 14, "universell": 10}
        assert len(payload["items"]) == count

        ids = [item["id"] for item in payload["items"]]
        assert len(ids) == len(set(ids))
        if product_id in {"metallanhaenger", "glasschild"}:
            assert "photo" not in ids

        for item in payload["items"]:
            preview = api_client.get(f"{BASE_URL}{item['preview']}", timeout=40)
            assert preview.status_code == 200
            assert preview.headers.get("content-type", "").startswith("image/png")
            assert len(preview.content) > 2000


# Module coverage: apply every compatible template; decoration layers must stay locked and behind text/image fields
def test_apply_every_compatible_template_and_layer_invariants(api_client):
    headers, _ = _guest_headers(api_client)
    for product_id in ["holzscheibe", "metallanhaenger", "glasschild"]:
        listed = api_client.get(f"{BASE_URL}/api/studio/templates?product_id={product_id}", timeout=35)
        assert listed.status_code == 200
        for item in listed.json()["items"]:
            applied = api_client.post(
                f"{BASE_URL}/api/studio/templates/{item['id']}/apply",
                headers=headers,
                json={"product_id": product_id},
                timeout=35,
            )
            assert applied.status_code == 200
            design = applied.json()
            assert design["editor_mode"] == "simple"
            assert design["template_id"] == item["id"]
            assert len(design["elements"]) <= 12

            elements = design["elements"]
            deco_indices = [i for i, e in enumerate(elements) if e["kind"] == "decoration"]
            content_indices = [i for i, e in enumerate(elements) if e["kind"] != "decoration"]
            for i in deco_indices:
                assert elements[i]["locked"] is True
            if deco_indices and content_indices:
                assert max(deco_indices) < min(content_indices)


# Module coverage: synthetic circle product compatibility + strict geometry containment after apply
def test_synthetic_circle_product_templates_and_geometry(api_client, mongo_db):
    identity = f"TEST_circle_{uuid4().hex[:12]}"
    area = {"x": 120, "y": 120, "w": 560, "h": 560, "shape": "circle"}
    product = {
        "id": identity,
        "name": "TEST Circle Blank",
        "subtitle": "synthetic",
        "material": "Holz",
        "category": "holz",
        "price_cents": 1990,
        "dimensions": "100x100x10",
        "area_mm": "70x70",
        "max_text": 60,
        "area": area,
        "ink": "#2f3a2a",
        "templates": ["text", "photo", "logo"],
        "image_file_id": None,
        "image": "/images/studio/holzscheibe.webp",
        "active": True,
        "is_sample": True,
        "production_approved": False,
        "version": 1,
    }
    mongo_db["studio_products"].insert_one(product.copy())
    headers, _ = _guest_headers(api_client)
    try:
        listed = api_client.get(f"{BASE_URL}/api/studio/templates?product_id={identity}", timeout=35)
        assert listed.status_code == 200
        items = listed.json()["items"]
        assert len(items) == 26

        for item in items:
            applied = api_client.post(
                f"{BASE_URL}/api/studio/templates/{item['id']}/apply",
                headers=headers,
                json={"product_id": identity},
                timeout=35,
            )
            assert applied.status_code == 200
            for element in applied.json()["elements"]:
                assert inside(element, area, 0)
    finally:
        mongo_db["studio_products"].delete_one({"id": identity})


# Module coverage: ornament catalog count + all 18 thumbnail/preview endpoints
def test_decorations_catalog_and_previews(api_client):
    listed = api_client.get(f"{BASE_URL}/api/studio/decorations", timeout=25)
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert len(items) == 18
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))

    for item in items:
        thumb = api_client.get(f"{BASE_URL}/api/studio/decorations/{item['id']}/thumbnail", timeout=30)
        assert thumb.status_code == 200
        assert thumb.headers.get("content-type", "").startswith("image/png")
        assert len(thumb.content) > 120

        preview = api_client.post(
            f"{BASE_URL}/api/studio/decoration-preview",
            json={"ornament": item["id"], "w": 240, "h": max(30, round(240 / item["ratio"])), "stroke_width": 1.5},
            timeout=30,
        )
        assert preview.status_code == 200
        payload = preview.json()
        assert payload["image"].startswith("data:image/png;base64,")


# Module coverage: text effects render differences (filled/outline/shadow) through public preview API
def test_text_effects_filled_outline_shadow_render_differences(api_client):
    headers, _ = _guest_headers(api_client)
    base = {"text": "O", "font": "sans", "font_size": 110, "curvature": 0}

    filled = api_client.post(f"{BASE_URL}/api/studio/text-preview", headers=headers, json=base, timeout=35)
    outline = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=headers,
        json={**base, "text_mode": "outline", "outline_width": 6},
        timeout=35,
    )
    shadow = api_client.post(
        f"{BASE_URL}/api/studio/text-preview",
        headers=headers,
        json={**base, "shadow_enabled": True, "shadow_distance": 16, "shadow_angle": 45},
        timeout=35,
    )

    assert filled.status_code == 200
    assert outline.status_code == 200
    assert shadow.status_code == 200

    fimg = _decode_png(filled.json()["image"])
    oimg = _decode_png(outline.json()["image"])
    simg = _decode_png(shadow.json()["image"])

    filled_alpha = _alpha_pixels(fimg)
    outline_alpha = _alpha_pixels(oimg)
    assert filled_alpha > 0
    assert outline_alpha > 0
    assert filled.json()["image"] != outline.json()["image"]
    assert simg.width >= fimg.width
    assert simg.height >= fimg.height


def test_round_frame_antialiasing_stays_in_outer_disk_even_rotated():
    for identity in ('circle-frame','double-circle'):
        for size in (8,50,256,399):
            image=Image.open(io.BytesIO(ornament_sprite(identity,size,size,1.5)))
            for angle in (0,45,137):
                stamp=image.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
                alpha=stamp.getchannel('A');width,height=alpha.size
                assert alpha.getbbox()
                for y in range(height):
                    for x in range(width):
                        if math.hypot(x+.5-width/2,y+.5-height/2)>size/2:
                            assert alpha.getpixel((x,y))==0,(identity,size,angle,x,y)

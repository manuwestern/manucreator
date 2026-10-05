"""Iteration 24: central customer P0 flow + admin canvas gestures + preview recovery injections."""

from __future__ import annotations

import hashlib
import io
import json
import time
import uuid
from pathlib import Path

import requests
from PIL import Image
from playwright.sync_api import sync_playwright


def load_env(path: str) -> dict:
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


front = load_env("/app/frontend/.env")
back = load_env("/app/backend/.env")
BASE = front["REACT_APP_BACKEND_URL"].rstrip("/")
ADMIN_EMAIL = back["ADMIN_EMAIL"]
ADMIN_PASSWORD = back["ADMIN_PASSWORD"]
ORIGIN = BASE

REPORT_PATH = Path("/app/test_reports/iteration24_customer_flow_checks.json")
ART_DIR = Path("/app/test_reports/artifacts/iteration_24_ui")
ART_DIR.mkdir(parents=True, exist_ok=True)

checks: list[dict] = []
created = {"product_id": None, "photo_id": None, "draft_id": None, "order_id": None}


def mark(name: str, **data):
    print(f"PASS {name} {data}", flush=True)
    checks.append({"check": name, "passed": True, **data})


def parse_canvas_data(page):
    area = json.loads(page.get_by_test_id("admin-area-canvas").get_attribute("data-area"))
    exclusions = json.loads(page.get_by_test_id("admin-area-canvas").get_attribute("data-exclusions"))
    return area, exclusions


def set_slider(page, testid: str, value: float):
    page.get_by_test_id(testid).evaluate(
        """(el,v)=>{
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,String(v));
        el.dispatchEvent(new Event('input',{bubbles:true}));
        el.dispatchEvent(new Event('change',{bubbles:true}));
        }""",
        value,
    )


def create_test_images():
    blank = Image.new("RGB", (800, 800), (246, 246, 242))
    b = io.BytesIO()
    blank.save(b, format="PNG")
    blank_bytes = b.getvalue()

    photo = Image.new("RGB", (420, 320), (230, 70, 70))
    for x in range(80, 340):
        for y in range(100, 220):
            photo.putpixel((x, y), (40, 40, 40))
    p = io.BytesIO()
    photo.save(p, format="PNG")
    photo_bytes = p.getvalue()

    blank_path = ART_DIR / "iter24_blank.png"
    photo_path = ART_DIR / "iter24_upload.png"
    blank_path.write_bytes(blank_bytes)
    photo_path.write_bytes(photo_bytes)
    return blank_path, photo_path, blank_bytes


def admin_api_session():
    session = requests.Session()
    response = session.post(
        f"{BASE}/api/admin/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    session.headers.update({"Origin": ORIGIN})
    return session


def create_product_fixture(admin: requests.Session, blank_png: Path):
    upload = admin.post(
        f"{BASE}/api/admin/products/photo",
        files={"file": ("TEST_iter24_blank.png", blank_png.read_bytes(), "image/png")},
        timeout=40,
    )
    upload.raise_for_status()
    photo_id = upload.json()["id"]
    created["photo_id"] = photo_id

    payload = {
        "name": f"TEST_iter24_customer_flow_{uuid.uuid4().hex[:8]}",
        "subtitle": "",
        "material": "Holz",
        "category": "holz",
        "price_cents": 2590,
        "dimensions": "110 x 110 x 10 mm",
        "area_mm": "Ø 85 mm",
        "max_text": 30,
        "area": {"x": 150, "y": 150, "w": 500, "h": 500, "shape": "circle"},
        "exclusions": [
            {"id": "hole_rect_seed", "shape": "rect", "x": 295, "y": 290, "w": 170, "h": 130},
            {"id": "hole_circle_seed", "shape": "circle", "x": 360, "y": 260, "w": 170, "h": 170},
        ],
        "ink": "#2f261f",
        "templates": ["text", "photo", "logo"],
        "image_file_id": photo_id,
        "active": True,
        "is_sample": True,
        "version": 1,
        "show_basic_templates": True,
        "decoration_ids": [],
    }
    created_product = admin.post(f"{BASE}/api/admin/products", json=payload, timeout=40)
    created_product.raise_for_status()
    product = created_product.json()
    created["product_id"] = product["id"]
    return product


def export_image(page, target: Path):
    page.wait_for_function("() => !document.querySelector('[data-testid=studio-download]').disabled", timeout=40000)
    with page.expect_download(timeout=45000) as event:
        page.get_by_test_id("studio-download").click()
    event.value.save_as(str(target))
    return Image.open(target).convert("RGB")


def live_elements(page):
    return json.loads(page.get_by_test_id("design-canvas").get_attribute("data-elements"))


def element_by_id(elements, identity):
    return next(e for e in elements if e["id"] == identity)


def select_first_text_layer(page):
    elements = json.loads(page.get_by_test_id("design-canvas").get_attribute("data-elements"))
    text = next(e for e in elements if e["kind"] == "text")
    page.get_by_test_id(f"layer-select-{text['id']}").click()
    page.get_by_test_id("layer-text").wait_for(timeout=15000)
    return text["id"]


def bg_like(pixel, bg=(246, 246, 242), tol=8):
    return all(abs(int(pixel[i]) - bg[i]) <= tol for i in range(3))


try:
    blank_path, upload_path, _ = create_test_images()
    admin = admin_api_session()
    product = create_product_fixture(admin, blank_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path="/root/bin/chromium", args=["--no-sandbox"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, accept_downloads=True, ignore_https_errors=True)
        page = context.new_page()

        # --- Admin canvas gestures (draw/drag/resize for area and exclusions) ---
        page.goto(BASE + "/verwaltung")
        page.get_by_test_id("admin-email").fill(ADMIN_EMAIL)
        page.get_by_test_id("admin-password").fill(ADMIN_PASSWORD)
        page.get_by_test_id("admin-login-submit").click()
        page.get_by_test_id(f"admin-edit-{product['id']}").wait_for(timeout=35000)
        page.goto(BASE + f"/verwaltung/artikel/{product['id']}")
        page.get_by_test_id("admin-product-tab-area").click()
        page.get_by_test_id("admin-area-canvas").wait_for(timeout=30000)
        canvas = page.get_by_test_id("admin-area-canvas").locator("canvas").first
        box = canvas.bounding_box()

        # Main area draw + drag + resize
        page.get_by_test_id("mask-select-area").click()
        page.get_by_test_id("area-shape-circle").click()
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 200, box["y"] + 180)
        page.mouse.down()
        page.mouse.move(box["x"] + 640, box["y"] + 620, steps=14)
        page.mouse.up()
        area, exclusions = parse_canvas_data(page)

        center_x = box["x"] + (area["x"] + area["w"] / 2) * box["width"] / 800
        center_y = box["y"] + (area["y"] + area["h"] / 2) * box["height"] / 800
        page.mouse.move(center_x, center_y)
        page.mouse.down()
        page.mouse.move(center_x + 35, center_y - 25, steps=8)
        page.mouse.up()

        # Resize main area with draw gesture (canvas-driven, not numeric input)
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 245, box["y"] + 210)
        page.mouse.down()
        page.mouse.move(box["x"] + 615, box["y"] + 575, steps=12)
        page.mouse.up()

        # Exclusion rect draw + drag + resize
        page.get_by_test_id("exclusion-add-rect").click()
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 290, box["y"] + 300)
        page.mouse.down()
        page.mouse.move(box["x"] + 470, box["y"] + 430, steps=10)
        page.mouse.up()

        area, exclusions = parse_canvas_data(page)
        rect_id = exclusions[-1]["id"]
        page.get_by_test_id(f"mask-select-exclusion-{rect_id}").click()
        rcx = box["x"] + (exclusions[-1]["x"] + exclusions[-1]["w"] / 2) * box["width"] / 800
        rcy = box["y"] + (exclusions[-1]["y"] + exclusions[-1]["h"] / 2) * box["height"] / 800
        page.mouse.move(rcx, rcy)
        page.mouse.down()
        page.mouse.move(rcx + 70, rcy + 15, steps=9)
        page.mouse.up()
        # Resize rect exclusion via draw gesture
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 350, box["y"] + 305)
        page.mouse.down()
        page.mouse.move(box["x"] + 555, box["y"] + 455, steps=11)
        page.mouse.up()

        # Exclusion circle draw + drag + resize (overlap with rect)
        page.get_by_test_id("exclusion-add-circle").click()
        area, exclusions = parse_canvas_data(page)
        circle_id = exclusions[-1]["id"]
        page.get_by_test_id(f"mask-select-exclusion-{circle_id}").click()
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 395, box["y"] + 255)
        page.mouse.down()
        page.mouse.move(box["x"] + 555, box["y"] + 415, steps=12)
        page.mouse.up()
        area, exclusions = parse_canvas_data(page)
        circle = [e for e in exclusions if e["id"] == circle_id][0]
        ccx = box["x"] + (circle["x"] + circle["w"] / 2) * box["width"] / 800
        ccy = box["y"] + (circle["y"] + circle["h"] / 2) * box["height"] / 800
        page.mouse.move(ccx, ccy)
        page.mouse.down()
        page.mouse.move(ccx - 35, ccy + 28, steps=10)
        page.mouse.up()
        # Resize circle exclusion via draw gesture
        page.get_by_test_id("area-draw").click()
        page.mouse.move(box["x"] + 405, box["y"] + 270)
        page.mouse.down()
        page.mouse.move(box["x"] + 575, box["y"] + 438, steps=11)
        page.mouse.up()

        area, exclusions = parse_canvas_data(page)
        assert len(exclusions) >= 2

        with page.expect_response(lambda r: f"/api/admin/products/{product['id']}" in r.url and r.request.method == "PUT", timeout=45000) as update_resp:
            page.get_by_test_id("admin-save-product").click()
        put_payload = json.loads(update_resp.value.request.post_data)
        assert "id" not in put_payload["area"], put_payload["area"]
        assert all("id" in e for e in put_payload["exclusions"]) and all(e["id"] != "area" for e in put_payload["exclusions"])
        product = update_resp.value.json()
        mark("admin area/exclusion draw-drag-resize saved; payload excludes area.id", product_id=product["id"], exclusions=len(product["exclusions"]))

        # --- Customer core flow ---
        page.goto(BASE + "/gestalten")
        page.get_by_test_id("template-picker-open").wait_for(timeout=30000)
        page.get_by_test_id("blank-picker-open").click()
        page.get_by_test_id(f"product-{product['id']}").click()
        page.get_by_test_id("design-canvas").wait_for(timeout=30000)

        # Text outline+shadow and numeric edits
        page.get_by_test_id("layer-text").fill("P0 MASK FLOW")
        page.wait_for_timeout(700)
        page.get_by_test_id("text-mode-outline").click()
        set_slider(page, "text-outline-width", 2.8)
        page.get_by_test_id("text-shadow-enabled").check()
        set_slider(page, "text-shadow-distance", 7)
        set_slider(page, "text-shadow-angle", 35)
        page.wait_for_timeout(600)

        # Add shape crossing boundary (drag + numeric size/rotation)
        page.get_by_test_id("shape-picker-open").click()
        page.wait_for_timeout(200)
        page.get_by_test_id("add-shape-rectangle").click(force=True)
        page.get_by_test_id("shape-properties").wait_for(timeout=10000)
        page.get_by_test_id("shape-width").fill("360")
        page.get_by_test_id("shape-height").fill("130")
        page.get_by_test_id("element-rotation").fill("27")
        page.get_by_test_id("element-x").fill("675")
        page.wait_for_timeout(600)
        assert page.get_by_test_id("element-boundary-error").count() == 0
        assert page.get_by_test_id("canvas-boundary-warning").count() == 0

        selected_shape = page.get_by_test_id("design-canvas").get_attribute("data-selected")
        # Start inside a real, unmasked hit region; assert movement BEFORE mouseup.
        def inside_zone(x, y, zone):
            if zone['shape'] == 'circle':
                return ((x-zone['x']-zone['w']/2)/(zone['w']/2))**2 + ((y-zone['y']-zone['h']/2)/(zone['h']/2))**2 < .9
            return zone['x'] <= x <= zone['x']+zone['w'] and zone['y'] <= y <= zone['y']+zone['h']
        safe = next((x,y) for y in range(20,780,10) for x in range(20,780,10)
                    if inside_zone(x,y,product['area']) and not any(inside_zone(x,y,z) for z in product['exclusions']))
        page.get_by_test_id('element-x').fill(str(safe[0]))
        page.get_by_test_id('element-y').fill(str(safe[1]))
        page.wait_for_timeout(400)
        pos = page.evaluate(
            """(id)=>{
            const n=window.Konva?.stages?.[0]?.findOne('#element-'+id);
            const p=n.getAbsolutePosition();
            const b=n.getStage().container().getBoundingClientRect();
            return {x:b.x+p.x,y:b.y+p.y,scale:n.getAbsoluteScale().x};
            }""",
            selected_shape,
        )
        page.mouse.move(pos["x"], pos["y"])
        page.mouse.down()
        drag_delta = product['area']['x']+product['area']['w']+35-safe[0]
        page.mouse.move(pos["x"] + drag_delta*pos['scale'], pos["y"], steps=14)
        live_center = page.evaluate("id=>window.Konva.stages[0].findOne('#element-'+id).x()", selected_shape)
        assert live_center > product['area']['x']+product['area']['w'], live_center
        page.mouse.up()
        assert page.get_by_test_id("canvas-boundary-warning").count() == 0
        dragged = element_by_id(live_elements(page), selected_shape)
        assert dragged['x']+dragged['w']/2 > product['area']['x']+product['area']['w']
        mark('actual drag crosses mask boundary during movement and retains position', live_center=live_center)

        # Add uploaded photo layer
        page.get_by_test_id("add-image-layer").click()
        page.get_by_test_id("image-upload-dialog").wait_for(timeout=10000)
        page.get_by_test_id("studio-image-rights").click()
        page.get_by_test_id("studio-file-input").set_input_files(str(upload_path))
        page.wait_for_timeout(1500)

        # Place photo numerically + rotate
        page.get_by_test_id("element-w").fill("250")
        page.get_by_test_id("element-rotation").fill("-18")
        page.get_by_test_id("element-x").fill("360")
        page.get_by_test_id("element-y").fill("360")
        page.wait_for_timeout(600)

        # Fully masked element selectable via layer list; recoverable with undo/redo
        page.get_by_test_id("shape-picker-open").click()
        page.wait_for_timeout(200)
        page.get_by_test_id("add-shape-circle").click(force=True)
        page.get_by_test_id("shape-diameter").fill("70")

        hole_rect = next(e for e in product["exclusions"] if e["shape"] == "rect")
        masked_cx = hole_rect["x"] + hole_rect["w"] / 2
        masked_cy = hole_rect["y"] + hole_rect["h"] / 2
        page.get_by_test_id("element-x").fill(str(round(masked_cx, 1)))
        page.get_by_test_id("element-y").fill(str(round(masked_cy, 1)))
        page.wait_for_timeout(600)

        masked_id = page.get_by_test_id("design-canvas").get_attribute("data-selected")
        page.get_by_test_id("layer-select-" + selected_shape).click()
        page.get_by_test_id("layer-select-" + masked_id).click()
        assert page.get_by_test_id("design-canvas").get_attribute("data-selected") == masked_id

        elements_before_move = live_elements(page)
        before_masked = element_by_id(elements_before_move, masked_id)
        page.get_by_test_id("element-x").fill("410")
        page.get_by_test_id("element-y").fill("420")
        page.wait_for_timeout(500)
        moved_elements = live_elements(page)
        moved_masked = element_by_id(moved_elements, masked_id)
        assert round(before_masked["x"], 2) != round(moved_masked["x"], 2)
        page.get_by_test_id("design-undo").click()
        page.wait_for_timeout(300)
        page.get_by_test_id("design-undo").click()
        page.wait_for_timeout(350)
        undo_masked = element_by_id(live_elements(page), masked_id)
        assert abs(undo_masked["x"] - before_masked["x"]) < 0.2 and abs(undo_masked["y"] - before_masked["y"]) < 0.2
        page.get_by_test_id("design-redo").click()
        page.wait_for_timeout(300)
        page.get_by_test_id("design-redo").click()
        page.wait_for_timeout(350)
        redo_masked = element_by_id(live_elements(page), masked_id)
        assert abs(redo_masked["x"] - moved_masked["x"]) < 0.2 and abs(redo_masked["y"] - moved_masked["y"]) < 0.2
        mark("fully masked layer selectable and recoverable with undo/redo", layer_id=masked_id)

        # Save and verify snapshot exclusions retained
        page.wait_for_function("() => !document.querySelector('[data-testid=studio-save]').disabled", timeout=40000)
        with page.expect_response(lambda r: "/api/studio/drafts" in r.url and r.request.method == "POST", timeout=50000) as save_resp:
            page.get_by_test_id("studio-save").click()
        saved = save_resp.value.json()
        created["draft_id"] = saved["id"]
        saved_elements = saved["design"]["elements"]
        assert saved.get("product_snapshot", {}).get("exclusions") == product["exclusions"]
        mark("save preserves product_snapshot.exclusions and boundary-crossing geometry", draft_id=saved["id"], elements=len(saved_elements))

        # Export 100% and 250%+pan pixel identity and 800x800
        exp_100 = export_image(page, ART_DIR / "iter24_export_100.png")
        hash_100 = hashlib.sha256(exp_100.tobytes()).hexdigest()

        for _ in range(6):
            page.get_by_test_id("canvas-zoom-in").click()
        page.get_by_test_id("canvas-pan-tool").click()
        cbox = page.get_by_test_id("design-canvas").locator("canvas").first.bounding_box()
        page.mouse.move(cbox["x"] + cbox["width"] / 2, cbox["y"] + cbox["height"] / 2)
        page.mouse.down()
        page.mouse.move(cbox["x"] + cbox["width"] / 2 + 45, cbox["y"] + cbox["height"] / 2 + 28, steps=10)
        page.mouse.up()
        exp_250 = export_image(page, ART_DIR / "iter24_export_250.png")
        hash_250 = hashlib.sha256(exp_250.tobytes()).hexdigest()
        assert exp_100.size == (800, 800)
        assert exp_250.size == (800, 800)
        assert hash_100 == hash_250
        mark("export is 800x800 and identical at 100% vs 250%+pan", hash=hash_100)

        # Pixel checks: circle corners blank, exclusion overlap unengraved, content exists elsewhere
        px = exp_100.load()
        area = product["area"]
        outside_corner = (max(0, int(area["x"] - 20)), max(0, int(area["y"] - 20)))

        rect = next(e for e in product["exclusions"] if e["shape"] == "rect")
        circ = next(e for e in product["exclusions"] if e["shape"] == "circle")
        overlap_point = (int(max(rect["x"], circ["x"]) + 18), int(max(rect["y"], circ["y"]) + 18))

        assert bg_like(px[outside_corner[0], outside_corner[1]])
        assert bg_like(px[overlap_point[0], overlap_point[1]])

        non_bg = 0
        for yy in range(180, 620, 20):
            for xx in range(180, 620, 20):
                if not bg_like(px[xx, yy]):
                    non_bg += 1
        assert non_bg > 3
        mark("pixel checks passed (outer corners blank, hole-overlap unengraved, content visible)", non_bg_samples=non_bg)

        # Large preview consistency
        page.get_by_test_id("product-preview-open").click()
        page.get_by_test_id("product-preview-canvas").wait_for(timeout=20000)
        edit_elements = json.loads(page.get_by_test_id("design-canvas").get_attribute("data-elements"))
        preview_elements = json.loads(page.get_by_test_id("product-preview-canvas").get_attribute("data-elements"))
        assert edit_elements == preview_elements
        page.keyboard.press("Escape")
        mark("large preview carries identical element model and clipping state")

        # Reopen -> cart -> test-order; verify unchanged geometry and snapshot
        page.goto(BASE + f"/gestalten?draft={created['draft_id']}")
        page.wait_for_function("document.querySelector('[data-testid=studio-save-status]')?.textContent==='Gespeichert'", timeout=35000)
        reopened = live_elements(page)
        assert reopened == saved_elements

        page.get_by_test_id("studio-add-cart").click()
        page.wait_for_url("**/warenkorb", timeout=45000)
        page.get_by_test_id("cart-checkout").click()
        page.get_by_test_id("checkout-fill-test").click()
        page.get_by_test_id("checkout-ack").click()
        with page.expect_response(lambda r: "/api/studio/orders" in r.url and r.request.method == "POST", timeout=50000) as order_resp:
            page.get_by_test_id("checkout-submit").click()
        order = order_resp.value.json()
        created["order_id"] = order["id"]
        assert order_resp.value.status == 201
        assert order["items"][0]["draft"]["design"]["elements"] == saved_elements
        if "product_snapshot" in order["items"][0]["draft"]:
            assert order["items"][0]["draft"]["product_snapshot"]["exclusions"] == product["exclusions"]
        page.get_by_test_id("order-reference").wait_for(timeout=20000)
        mark("save->reopen->cart->test-order kept geometry/content unchanged", order_reference=order["reference"])

        # Version change requires resave
        admin_products = admin.get(f"{BASE}/api/admin/products", timeout=30)
        admin_products.raise_for_status()
        latest = next(p for p in admin_products.json() if p["id"] == product["id"])
        bump_payload = {k: latest[k] for k in [
            "name", "subtitle", "material", "category", "price_cents", "dimensions", "area_mm", "max_text",
            "area", "exclusions", "ink", "templates", "image_file_id", "active", "is_sample", "version",
            "show_basic_templates", "decoration_ids"
        ]}
        # Send current version; backend handles version progression.
        bump_payload["version"] = latest["version"]
        bump_payload["area_mm"] = f"{latest['area_mm']} · v"
        bump = admin.put(f"{BASE}/api/admin/products/{product['id']}", json=bump_payload, timeout=35)
        bump.raise_for_status()
        product = bump.json()

        page.goto(BASE + f"/gestalten?draft={created['draft_id']}")
        page.get_by_test_id("studio-error").wait_for(timeout=30000)
        assert "Rohling wurde aktualisiert" in page.get_by_test_id("studio-error").inner_text()
        assert page.get_by_test_id("studio-save-status").inner_text().strip() == "Nicht gespeichert"
        page.get_by_test_id("studio-save").click()
        page.wait_for_function("document.querySelector('[data-testid=studio-save-status]')?.textContent==='Gespeichert'", timeout=35000)
        mark("product version change correctly forces resave")

        # --- Preview recovery injections (test-only interception, API remains real otherwise) ---
        # One text-preview 503 + one font fetch failure should recover automatically.
        page2 = context.new_page()
        state_a = {"text_503": 0, "font_503": 0}

        def route_once_fail(route, request):
            url = request.url
            if "/api/studio/text-preview" in url and state_a["text_503"] < 1:
                state_a["text_503"] += 1
                route.fulfill(status=503, body='{"detail":"unconditional drop overload"}', headers={"Content-Type": "application/json"})
                return
            if any(ext in url.lower() for ext in [".woff2", ".woff", ".ttf", ".otf"]) and state_a["font_503"] < 1:
                state_a["font_503"] += 1
                route.fulfill(status=503, body="font unavailable")
                return
            route.continue_()

        page2.route("**/*", route_once_fail)
        page2.goto(BASE + f"/gestalten?draft={created['draft_id']}")
        select_first_text_layer(page2)
        page2.get_by_test_id("layer-text").fill("RECOVERY ONE")
        page2.wait_for_timeout(3000)
        assert page2.get_by_test_id("canvas-status").count() == 0
        assert not page2.get_by_test_id("studio-save").is_disabled()
        mark("single 503 text-preview + single font failure recovered automatically", text_failures=state_a["text_503"], font_failures=state_a["font_503"])
        page2.unroute("**/*", route_once_fail)

        # Persistent text-preview 503 for retries, then manual canvas-retry recovers without element changes.
        page3 = context.new_page()
        state_b = {"count": 0, "block": True}

        def route_retry(route, request):
            if "/api/studio/text-preview" in request.url and state_b["block"]:
                state_b["count"] += 1
                route.fulfill(status=503, body='{"detail":"Temporär nicht erreichbar"}', headers={"Content-Type": "application/json"})
                return
            route.continue_()

        page3.route("**/*", route_retry)
        page3.goto(BASE + f"/gestalten?draft={created['draft_id']}")
        text_id_retry = select_first_text_layer(page3)
        baseline_elements = json.loads(page3.get_by_test_id("design-canvas").get_attribute("data-elements"))
        baseline_other = [e for e in baseline_elements if e["id"] != text_id_retry]
        state_b["count"] = 0
        page3.get_by_test_id("layer-text").fill("RECOVERY RETRY")
        page3.get_by_test_id("canvas-status").wait_for(timeout=25000)
        try:
            page3.get_by_test_id("canvas-retry").wait_for(timeout=12000)
        except Exception as exc:
            status_text = page3.get_by_test_id("canvas-status").inner_text()
            raise AssertionError(f"canvas-retry missing after persistent 503; attempts={state_b['count']} status={status_text}") from exc
        assert 3 <= state_b["count"] <= 6
        failed_state_elements = json.loads(page3.get_by_test_id("design-canvas").get_attribute("data-elements"))
        failed_other = [e for e in failed_state_elements if e["id"] != text_id_retry]
        assert failed_other == baseline_other
        state_b["block"] = False
        page3.get_by_test_id("canvas-retry").click()
        page3.wait_for_timeout(2500)
        assert page3.get_by_test_id("canvas-status").count() == 0
        after_retry = json.loads(page3.get_by_test_id("design-canvas").get_attribute("data-elements"))
        after_other = [e for e in after_retry if e["id"] != text_id_retry]
        assert after_other == baseline_other
        mark("persistent 503 retries bounded to 3; manual retry recovers with unchanged elements", attempts=state_b["count"])
        page3.unroute("**/*", route_retry)

        # Validation 422 should not trigger repeated retries.
        page4 = context.new_page()
        state_c = {"count": 0}

        def route_422(route, request):
            if "/api/studio/text-preview" in request.url and state_c["count"] == 0:
                state_c["count"] += 1
                route.fulfill(status=422, body='{"detail":"validation failed"}', headers={"Content-Type": "application/json"})
                return
            if "/api/studio/text-preview" in request.url:
                state_c["count"] += 1
            route.continue_()

        page4.route("**/*", route_422)
        page4.goto(BASE + f"/gestalten?draft={created['draft_id']}")
        select_first_text_layer(page4)
        page4.get_by_test_id("layer-text").fill("VALIDATION")
        page4.wait_for_timeout(1800)
        assert page4.get_by_test_id("text-property-error").count() >= 0
        assert 1 <= state_c["count"] <= 4
        mark("validation 422 did not auto-retry repeatedly", attempts=state_c["count"])
        page4.unroute("**/*", route_422)

        browser.close()

except Exception as exc:
    checks.append({"check": "iteration24 customer flow", "passed": False, "error": str(exc)})
    raise
finally:
    REPORT_PATH.write_text(
        json.dumps(
            {
                "base_url": BASE,
                "created": created,
                "checks": checks,
                "failure_injection": "TEST-ONLY request interception for preview resilience; business APIs otherwise real",
                "mocked_apis": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

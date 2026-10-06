"""Mobile designer sweep: panels, snap, pinch, image shape, preview→cart→order."""
import io, json, sys, time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

BASE = [l.split('=', 1)[1].strip() for l in Path('/app/frontend/.env').read_text().splitlines() if l.startswith('REACT_APP_BACKEND_URL=')][0]
ART = Path('/app/test_reports/artifacts/mobile_sweep'); ART.mkdir(parents=True, exist_ok=True)
photo = Image.new('RGB', (400, 400), (30, 30, 30)); b = io.BytesIO(); photo.save(b, 'PNG'); (ART / 'dark.png').write_bytes(b.getvalue())
results = []
def ok(name, **d): print('PASS', name, d, flush=True); results.append({'check': name, 'passed': True, **d})
def elements(page): return json.loads(page.get_by_test_id('design-canvas').get_attribute('data-elements'))
def node_pos(page, eid): return page.evaluate("id=>{const n=window.Konva.stages[0].findOne('#element-'+id);const p=n.getAbsolutePosition();const b=n.getStage().container().getBoundingClientRect();return {x:b.x+p.x,y:b.y+p.y,s:n.getAbsoluteScale().x}}", eid)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/root/bin/chromium', args=['--no-sandbox'])
    ctx = browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True, accept_downloads=True, ignore_https_errors=True)
    page = ctx.new_page(); page.goto(BASE + '/gestalten')
    page.get_by_test_id('mobile-studio').wait_for(timeout=30000)
    page.wait_for_selector('[data-testid="design-canvas"][data-loaded="true"]', timeout=30000)
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    product = page.evaluate("()=>JSON.parse(localStorage.getItem('manucreator-studio-design')).design.product_id")
    products = page.request.get(BASE + '/api/studio/products').json()['products']; prod = next(x for x in products if x['id'] == product); area = prod['area']
    tid = elements(page)[0]['id']
    # object panel via tap
    pos = node_pos(page, tid); page.touchscreen.tap(pos['x'], pos['y']); page.get_by_test_id('ms-object-panel').wait_for(timeout=5000); ok('tap opens object panel')
    # curve
    page.get_by_test_id('ms-tile-wölbung').click(); page.get_by_test_id('ms-curve-up').click(); page.wait_for_timeout(1200)
    e = elements(page)[0]; assert e['curvature'] == 60; ok('curve applied', curvature=e['curvature'], w=e['w'])
    page.get_by_test_id('ms-sheet-done').click()
    # snap drag: move element away then towards centre
    page.get_by_test_id('ms-sheet-done').click()
    cx, cy = area['x'] + area['w'] / 2, area['y'] + area['h'] / 2
    pos = node_pos(page, tid); e = elements(page)[0]
    target_model_x = cx + 4  # 4px off centre → should snap exactly
    dx = (target_model_x - (e['x'] + e['w'] / 2)) * pos['s']; dy = (cy + 3 - (e['y'] + e['h'] / 2)) * pos['s']
    page.mouse.move(pos['x'], pos['y']); page.mouse.down(); page.mouse.move(pos['x'] + dx / 2, pos['y'] + dy / 2, steps=5); page.mouse.move(pos['x'] + dx, pos['y'] + dy, steps=8)
    guides = page.evaluate("()=>window.Konva.stages[0].find('Line').filter(l=>l.name()==='editor-decoration').length")
    page.mouse.up(); e = elements(page)[0]
    assert abs(e['x'] + e['w'] / 2 - cx) < .01 and abs(e['y'] + e['h'] / 2 - cy) < .01, e; assert guides >= 1
    assert page.evaluate("()=>window.Konva.stages[0].find('Line').filter(l=>l.name()==='editor-decoration').length") == 0
    ok('snap to centre with transient guides', guides=guides)
    page.get_by_test_id('ms-snap-toggle').click(); page.get_by_test_id('ms-sheet-done').click() if page.get_by_test_id('ms-sheet-done').count() else None
    pos = node_pos(page, tid); page.mouse.move(pos['x'], pos['y']); page.mouse.down(); page.mouse.move(pos['x'] + 12 * pos['s'], pos['y'], steps=6); page.mouse.up()
    e = elements(page)[0]; assert abs(e['x'] + e['w'] / 2 - cx) > 2 and abs(e['x'] + e['w'] / 2 - cx) < 25, e; ok('snap toggle off allows free placement', centre_offset=e['x'] + e['w'] / 2 - cx); page.get_by_test_id('ms-snap-toggle').click()
    # pinch zoom view only
    if page.get_by_test_id('ms-sheet-done').count(): page.get_by_test_id('ms-sheet-done').click()
    before = elements(page); box = page.get_by_test_id('design-canvas').bounding_box(); mx, my = box['x'] + box['width'] / 2, box['y'] + box['height'] * 0.8
    cdp = ctx.new_cdp_session(page)
    def tp(pts, t): cdp.send('Input.dispatchTouchEvent', {'type': t, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(pts)]})
    tp([(mx - 40, my), (mx + 40, my)], 'touchStart')
    for i in range(1, 8): tp([(mx - 40 - i * 12, my), (mx + 40 + i * 12, my)], 'touchMove')
    tp([], 'touchEnd'); page.wait_for_timeout(300)
    cam = json.loads(page.get_by_test_id('design-canvas').get_attribute('data-camera')); assert cam['zoom'] > 1.3, cam; assert elements(page) == before; ok('pinch zooms view only', zoom=cam['zoom'])
    # one finger pan on empty stage
    tp([(box['x'] + 12, box['y'] + 12)], 'touchStart'); tp([(box['x'] + 60, box['y'] + 40)], 'touchMove'); tp([], 'touchEnd'); page.wait_for_timeout(200)
    cam2 = json.loads(page.get_by_test_id('design-canvas').get_attribute('data-camera')); assert (cam2['x'], cam2['y']) != (cam['x'], cam['y']); assert elements(page) == before; ok('one-finger pan on empty area', cam=cam2)
    page.get_by_test_id('ms-fit-view').click(); page.wait_for_selector('[data-testid="design-canvas"][data-loaded="true"]', timeout=20000)
    assert json.loads(page.get_by_test_id('design-canvas').get_attribute('data-camera'))['zoom'] == 1; ok('fit view resets')
    # image upload + shape
    page.get_by_test_id('ms-bar-image').click(); page.get_by_test_id('ms-image-rights').check(); page.get_by_test_id('ms-image-input-gallery').set_input_files(str(ART / 'dark.png'))
    page.get_by_test_id('ms-object-panel').wait_for(timeout=20000); img = next(x for x in elements(page) if x['kind'] == 'image')
    page.get_by_test_id('ms-tile-form').click(); page.get_by_test_id('ms-image-shape-circle').click(); page.wait_for_timeout(600)
    assert next(x for x in elements(page) if x['kind'] == 'image')['image_shape'] == 'circle'
    corner = page.evaluate("id=>{const n=window.Konva.stages[0].findOne('#element-'+id).findOne('Image');const c=n.image();return c.getContext('2d').getImageData(1,1,1,1).data[3]}", img['id'])
    centre = page.evaluate("id=>{const n=window.Konva.stages[0].findOne('#element-'+id).findOne('Image');const c=n.image();return c.getContext('2d').getImageData(Math.floor(c.width/2),Math.floor(c.height/2),1,1).data[3]}", img['id'])
    assert corner == 0 and centre > 0; ok('circle image shape masks corners in canvas', corner=corner, centre=centre)
    page.get_by_test_id('ms-sheet-done').click(); page.get_by_test_id('ms-tile-löschen').click(); page.get_by_test_id('ms-notice').wait_for(timeout=4000)
    assert not any(x['kind'] == 'image' for x in elements(page)); page.get_by_test_id('ms-notice-undo').click(); page.wait_for_timeout(300)
    assert any(x['kind'] == 'image' for x in elements(page)); ok('delete notice with undo restores')
    # preview → save → cart → order
    page.get_by_test_id('ms-preview-open').click(); page.get_by_test_id('ms-preview').wait_for(timeout=10000); page.get_by_test_id('product-preview-canvas').wait_for(timeout=20000)
    page.wait_for_function("()=>!document.querySelector('[data-testid=ms-add-cart]').disabled", timeout=40000)
    with page.expect_response(lambda r: '/api/studio/drafts' in r.url and r.request.method == 'POST', timeout=60000) as resp: page.get_by_test_id('ms-add-cart').click()
    draft = resp.value.json(); saved_img = next(x for x in draft['design']['elements'] if x['kind'] == 'image'); assert saved_img['image_shape'] == 'circle'
    page.wait_for_url('**/warenkorb', timeout=45000)
    render = page.request.get(BASE + f"/api/studio/files/{draft['render_id']}", headers={'Authorization': 'Bearer ' + json.loads(page.evaluate("localStorage.getItem('manucreator-studio-guest-v1')"))['token']})
    im = Image.open(io.BytesIO(render.body())).convert('RGB'); cx_i = round(saved_img['x'] + saved_img['w'] / 2); cy_i = round(saved_img['y'] + saved_img['h'] / 2)
    blank = Image.open(io.BytesIO(page.request.get(BASE + prod['image'] if prod['image'].startswith('/api') else BASE + prod['image']).body())).convert('RGB').resize((800, 800))
    corner_px = (round(saved_img['x']) + 2, round(saved_img['y']) + 2)
    assert im.getpixel(corner_px) == blank.getpixel(corner_px) or sum(abs(a - b) for a, b in zip(im.getpixel(corner_px), blank.getpixel(corner_px))) < 12, (im.getpixel(corner_px), blank.getpixel(corner_px))
    assert sum(abs(a - b) for a, b in zip(im.getpixel((cx_i, cy_i)), blank.getpixel((cx_i, cy_i)))) > 30
    ok('server render masks circle image shape identically', draft=draft['id'])
    page.get_by_test_id('cart-checkout').click(); page.get_by_test_id('checkout-fill-test').click(); page.get_by_test_id('checkout-ack').click()
    with page.expect_response(lambda r: '/api/studio/orders' in r.url and r.request.method == 'POST', timeout=50000) as o: page.get_by_test_id('checkout-submit').click()
    assert o.value.status == 201; ok('mobile test order completed', reference=o.value.json()['reference'])
    for vp in [(360, 740), (740, 360)]:
        page.set_viewport_size({'width': vp[0], 'height': vp[1]}); page.goto(BASE + '/gestalten'); page.get_by_test_id('mobile-studio').wait_for(timeout=30000) if vp[0] <= 760 else page.get_by_test_id('precision-editor').wait_for(timeout=30000)
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth'); page.screenshot(path=str(ART / f'view_{vp[0]}x{vp[1]}.jpg'), quality=30)
    ok('viewports without horizontal overflow')
    browser.close()
Path('/app/test_reports/mobile-sweep.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))

"""Final shape E2E: real admin publish, customer save/download/checkout/archive replay."""
import hashlib
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

env={}
for path in ('/app/frontend/.env','/app/backend/.env'):
    for line in Path(path).read_text().splitlines():
        if '=' in line:
            key,value=line.split('=',1);env[key]=value.strip().strip('"').strip("'")
BASE=env['REACT_APP_BACKEND_URL'];checks=[];template_id=None

def check(name,**info):checks.append({'check':name,'passed':True,**info});print('PASS',name,info,flush=True)
def elements(page):return json.loads(page.get_by_test_id('design-canvas').get_attribute('data-elements'))
def settled(page):page.wait_for_timeout(500)
def add_shape(page,kind):
    page.get_by_test_id('shape-picker-open').click();page.get_by_test_id('add-shape-'+kind).click();page.get_by_test_id('shape-kind').wait_for();settled(page)
def ready(page,testid):page.wait_for_function('(id)=>!document.querySelector(`[data-testid="${id}"]`).disabled',arg=testid,timeout=30000)
def download(page,target):
    ready(page,'studio-download')
    with page.expect_download(timeout=30000) as event:page.get_by_test_id('studio-download').click()
    event.value.save_as(target)
    return Image.open(target).convert('RGBA')

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/root/bin/chromium',args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        admin=context.new_page();admin.goto(BASE+'/verwaltung')
        admin.get_by_test_id('admin-email').fill(env['ADMIN_EMAIL']);admin.get_by_test_id('admin-password').fill(env['ADMIN_PASSWORD']);admin.get_by_test_id('admin-login-submit').click();admin.get_by_test_id('admin-edit-holzscheibe').wait_for(timeout=30000)
        admin.goto(BASE+'/verwaltung/artikel/holzscheibe/vorlagen/neu')
        admin.get_by_test_id('admin-template-name').fill('TEST_SHAPES_FINAL_'+str(int(time.time())))
        admin.get_by_test_id('admin-template-add-text').click();admin.get_by_test_id('layer-text').fill('Mia');settled(admin)
        admin.get_by_test_id('field-label').fill('Vorname');admin.get_by_test_id('admin-template-allow-free').uncheck()
        add_shape(admin,'circle');admin.get_by_test_id('shape-diameter').fill('230');admin.get_by_test_id('shape-mode-outline').click();admin.get_by_test_id('shape-stroke-width').fill('3');settled(admin)
        before=elements(admin);admin.get_by_test_id('element-x').fill('780');settled(admin)
        assert elements(admin)==before
        message=admin.get_by_test_id('element-boundary-error').inner_text()
        assert 'Formproportionen' in message and 'Schriftgröße' not in message
        check('shape-specific boundary feedback preserves last state')
        add_shape(admin,'line');admin.get_by_test_id('shape-length').fill('150');admin.get_by_test_id('shape-stroke-width').fill('3');admin.get_by_test_id('element-y').fill('470');settled(admin)
        add_shape(admin,'heart');admin.get_by_test_id('shape-width').fill('60');admin.get_by_test_id('element-y').fill('420');admin.get_by_test_id('shape-mode-outline').click();settled(admin)
        shapes={e['shape_type']:e for e in elements(admin) if e['kind']=='shape'}
        assert set(shapes)=={'circle','line','heart'} and shapes['line']['h']==shapes['line']['stroke_width']==3
        ready(admin,'admin-template-publish')
        with admin.expect_response(lambda r:'/article-templates/' in r.url and r.url.endswith('/publish') and r.request.method=='POST',timeout=60000) as event:admin.get_by_test_id('admin-template-publish').click()
        published=event.value.json();assert event.value.status==200,published;template_id=published['id']
        check('admin UI publishes protected template with circle,line,heart and required text',template_id=template_id)
        page=context.new_page();page.goto(BASE+'/gestalten');page.get_by_test_id('template-picker-open').click(timeout=30000);page.get_by_test_id('template-'+template_id).click(timeout=30000)
        with page.expect_response(lambda r:r.url.endswith('/article-templates/'+template_id+'/apply') and r.request.method=='POST') as event:page.get_by_test_id('template-confirm-replace').click()
        applied=event.value.json();field=next(e for e in applied['elements'] if e.get('template_field'))
        page.get_by_test_id('template-field-'+field['template_field']).fill('Lena');settled(page)
        assert page.get_by_test_id('shape-picker-open').count()==0 and page.get_by_test_id('template-free-edit').count()==0
        assert len([e for e in elements(page) if e.get('template_field')])==1
        ready(page,'studio-save')
        with page.expect_response(lambda r:'/api/studio/drafts' in r.url and r.request.method=='POST',timeout=60000) as event:page.get_by_test_id('studio-save').click()
        saved=event.value.json();assert event.value.status==200,saved;expected=saved['design']['elements'];draft_id=saved['id']
        assert expected==elements(page)
        check('customer personalizes only approved text and saves exact shape snapshot',draft_id=draft_id)
        image100=download(page,'/tmp/shapes100.png')
        for _ in range(6):page.get_by_test_id('canvas-zoom-in').click()
        page.get_by_test_id('canvas-pan-tool').click();rect=page.get_by_test_id('design-canvas').locator('canvas').first.bounding_box()
        x,y=rect['x']+rect['width']/2,rect['y']+rect['height']/2
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+43,y+28,steps=8);page.mouse.up()
        camera=json.loads(page.get_by_test_id('design-canvas').get_attribute('data-camera'));assert camera['zoom']==2.5 and camera['x']!=0,camera
        image250=download(page,'/tmp/shapes250.png')
        assert image100.size==image250.size==(800,800) and image100.tobytes()==image250.tobytes()
        check('800x800 full exports pixel-identical at100 and250percent plus pan',rgba_sha256=hashlib.sha256(image100.tobytes()).hexdigest())
        page.get_by_test_id('product-preview-open').click();assert json.loads(page.get_by_test_id('product-preview-canvas').get_attribute('data-elements'))==expected;page.get_by_test_id('product-preview-dialog-close').click()
        check('large product preview uses identical shapes and text')
        page.goto(BASE+'/gestalten?draft='+draft_id);page.wait_for_function("document.querySelector('[data-testid=studio-save-status]')?.textContent==='Gespeichert'",timeout=30000)
        assert elements(page)==expected
        reopened=download(page,'/tmp/shapes-reopened.png');assert reopened.tobytes()==image100.tobytes()
        check('saved draft reopen restores exact geometry and pixel-identical full export')
        ready(page,'studio-add-cart');page.get_by_test_id('studio-add-cart').click();page.wait_for_url('**/warenkorb',timeout=60000);page.get_by_test_id('cart-checkout').click();page.get_by_test_id('checkout-fill-test').click();page.get_by_test_id('checkout-ack').click()
        with page.expect_response(lambda r:'/api/studio/orders' in r.url and r.request.method=='POST',timeout=60000) as event:page.get_by_test_id('checkout-submit').click()
        order=event.value.json();assert event.value.status==201,order
        assert order['is_test'] and order['payable_cents']==0 and not order['production_approved']
        assert order['items'][0]['draft']['design']['elements']==expected
        page.get_by_test_id('order-reference').wait_for(timeout=30000)
        check('complete customer cart/test-checkout preserves all shape properties',reference=order['reference'])
        archived=context.request.post(BASE+'/api/admin/article-templates/'+template_id+'/archive',headers={'Origin':BASE})
        assert archived.status==200,archived.text()
        page.goto(BASE+'/gestalten?draft='+draft_id);page.wait_for_function("document.querySelector('[data-testid=studio-save-status]')?.textContent==='Gespeichert'",timeout=30000)
        assert elements(page)==expected
        historical=download(page,'/tmp/shapes-historical.png');assert historical.tobytes()==image100.tobytes()
        check('archived template keeps historical draft and export pixel-identical')
        # An unchanged saved draft is intentionally reused without another POST.
        page.get_by_test_id('template-field-'+field['template_field']).fill('Nora');settled(page)
        ready(page,'studio-save')
        with page.expect_response(lambda r:'/api/studio/drafts' in r.url and r.request.method=='POST',timeout=60000) as event:page.get_by_test_id('studio-save').click()
        assert event.value.status==200,event.value.text()
        assert [e for e in event.value.json()['design']['elements'] if e['kind']=='shape']==[e for e in expected if e['kind']=='shape']
        page.get_by_test_id('template-picker-open').click();page.get_by_test_id('template-monogram').wait_for(timeout=30000)
        assert page.get_by_test_id('template-'+template_id).count()==0
        check('archiving removes new selection; permitted historical personalization remains saveable without changing shapes')
        browser.close()
except Exception as exc:
    checks.append({'passed':False,'error':str(exc)});raise
finally:
    Path('/app/test_reports/shapes-final-flow.json').write_text(json.dumps({'checks':checks,'template_id':template_id,'mocked_apis':False},ensure_ascii=False,indent=2))
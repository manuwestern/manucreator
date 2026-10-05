"""Focused post-iteration17 verification. No screenshots or paid providers."""
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=next(line.split('=',1)[1] for line in Path('/app/frontend/.env').read_text().splitlines() if line.startswith('REACT_APP_BACKEND_URL='))
REPORT=Path('/app/test_reports/materials-final-verification.json')
results=[]

def passed(name,**data):
    results.append({'check':name,'passed':True,**data});print('PASS',name,data,flush=True)

def elements(page):return json.loads(page.get_by_test_id('design-canvas').get_attribute('data-elements'))

def slider(page,testid,value):
    page.get_by_test_id(testid).evaluate("(el,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,String(v));el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}",value)
    page.wait_for_timeout(650)

def live_transform(page,identity,valid,invalid):
    result=page.evaluate("""({id,valid,invalid})=>{
      const node=window.Konva.stages[0].findOne('#element-'+id);
      node.fire('transformstart',{target:node});
      node.scale({x:valid,y:valid});node.fire('transform',{target:node});
      const accepted=node.scaleX();
      node.scale({x:invalid,y:invalid});node.fire('transform',{target:node});
      const restored=node.scaleX();
      const telemetry=JSON.parse(node.getStage().container().getAttribute('data-live-element'));
      node.fire('transformend',{target:node});
      return {accepted,restored,telemetry};
    }""",{'id':identity,'valid':valid,'invalid':invalid})
    assert abs(result['accepted']-valid)<.0001 and abs(result['restored']-valid)<.0001,result
    page.wait_for_timeout(700)
    return result

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/root/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1920,'height':800})
        page.goto(BASE+'/gestalten');page.get_by_test_id('layer-text').wait_for(timeout=30000)
        page.get_by_test_id('layer-text').fill('Mia');page.wait_for_timeout(600)
        page.get_by_test_id('text-font-size').fill('36');page.wait_for_timeout(600)
        page.get_by_test_id('text-mode-outline').click();page.wait_for_timeout(600)
        page.get_by_test_id('text-shadow-enabled').check();page.wait_for_timeout(600)
        slider(page,'text-curvature',60)
        page.get_by_test_id('element-rotation').fill('20');page.wait_for_timeout(300)
        e=elements(page)[0];theta=math.radians(e['rotation'])
        extent=(math.cos(theta)*e['w']+math.sin(theta)*e['h'])/2
        page.get_by_test_id('element-x').fill(str(550-extent-1));page.wait_for_timeout(300)
        before=elements(page)
        slider(page,'text-shadow-distance',30)
        assert elements(page)==before
        assert page.get_by_test_id('text-property-error').is_visible()
        passed('out-of-bounds shadow retains previous text,curve,rotation and geometry')
        slider(page,'text-shadow-distance',3)
        page.get_by_test_id('element-x').fill('400');page.wait_for_timeout(300)
        for _ in range(6):page.get_by_test_id('canvas-zoom-in').click()
        page.get_by_test_id('canvas-pan-tool').click()
        rect=page.get_by_test_id('design-canvas').locator('canvas').first.bounding_box()
        page.mouse.move(rect['x']+rect['width']/2,rect['y']+rect['height']/2);page.mouse.down()
        page.mouse.move(rect['x']+rect['width']/2+35,rect['y']+rect['height']/2+25,steps=6);page.mouse.up()
        page.get_by_test_id('canvas-pan-tool').click()
        state=live_transform(page,e['id'],1.15,8)
        passed('pre-commit rectangle transform restores last valid scale at250percent plus pan',scale=state['restored'])
        # Mouse-driven drag tries to leave the rectangle; full effect bounding box must remain inside.
        e=elements(page)[0]
        point=page.evaluate("id=>{const n=Konva.stages[0].findOne('#element-'+id);const p=n.getAbsolutePosition(),b=n.getStage().container().getBoundingClientRect();return {x:b.x+p.x,y:b.y+p.y}}",e['id'])
        page.mouse.move(point['x'],point['y']);page.mouse.down();page.mouse.move(point['x']+450,point['y']+50,steps=20);page.mouse.up();page.wait_for_timeout(350)
        e=elements(page)[0];t=math.radians(e['rotation']);cx=e['x']+e['w']/2;cy=e['y']+e['h']/2
        for u,v in [(-e['w']/2,-e['h']/2),(e['w']/2,-e['h']/2),(e['w']/2,e['h']/2),(-e['w']/2,e['h']/2)]:
            x=cx+u*math.cos(t)-v*math.sin(t);y=cy+u*math.sin(t)+v*math.cos(t)
            assert 249.99<=x<=550.01 and 254.99<=y<=545.01
        passed('mouse drag rotated curved outline with shadow constrained at250percent')
        page.get_by_test_id('blank-picker-open').click();page.get_by_test_id('product-TEST_material_round_final').click()
        page.get_by_test_id('canvas-zoom-fit').click()
        page.get_by_test_id('decoration-picker-open').click();page.get_by_test_id('add-decoration-circle-frame').click()
        page.get_by_test_id('element-w').fill('399');page.wait_for_timeout(400)
        e=next(e for e in elements(page) if e['kind']=='decoration')
        assert abs(e['w']-399)<.0001 and abs(e['h']-399)<.0001,e
        before=elements(page);slider(page,'decoration-stroke-width',8)
        assert elements(page)==before and page.get_by_test_id('decoration-boundary-error').is_visible(),{'before':before,'after':elements(page),'error_count':page.get_by_test_id('decoration-boundary-error').count(),'stroke_value':page.get_by_test_id('decoration-stroke-width').input_value()}
        passed('399px outer circle fits400px area; increasing stroke rejected unchanged')
        page.get_by_test_id('element-rotation').fill('137');page.wait_for_timeout(300)
        assert next(e for e in elements(page) if e['kind']=='decoration')['rotation']==137
        before=elements(page);page.get_by_test_id('element-x').fill('401');page.wait_for_timeout(300)
        assert elements(page)==before and page.get_by_test_id('element-boundary-error').is_visible()
        for _ in range(6):page.get_by_test_id('canvas-zoom-in').click()
        state=live_transform(page,e['id'],1,1.05)
        passed('circle contour independent of137degree rotation; invalid live scale restores last valid',scale=state['restored'])
        # Exactly twelve total layers, including decorations, then all adding/duplication is blocked.
        while len(elements(page))<12:
            selected=page.get_by_test_id('design-canvas').get_attribute('data-selected')
            page.get_by_test_id('layer-duplicate-'+selected).click();page.wait_for_timeout(100)
        assert page.get_by_test_id('add-text-layer').is_disabled() and page.get_by_test_id('decoration-picker-open').is_disabled()
        selected=page.get_by_test_id('design-canvas').get_attribute('data-selected')
        assert page.get_by_test_id('layer-duplicate-'+selected).is_disabled()
        passed('twelve-layer limit includes decorations')
        page.close()
        for width in (320,768,1024,1440):
            page=browser.new_page(viewport={'width':width,'height':800})
            page.goto(BASE+'/gestalten');page.get_by_test_id('template-picker-open').wait_for(timeout=30000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            box=page.get_by_test_id('workspace-canvas').bounding_box()
            assert box['width']>100 and box['height']>100 and box['y']+box['height']<801,box
            page.get_by_test_id('template-picker-open').click();page.get_by_test_id('template-wood-family').wait_for(timeout=30000)
            bounds=page.get_by_test_id('template-picker-dialog').bounding_box()
            assert bounds['x']>=0 and bounds['x']+bounds['width']<=width+1,bounds
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.get_by_test_id('template-picker-dialog-close').click()
            page.get_by_test_id('decoration-picker-open').click();page.get_by_test_id('add-decoration-laurel').wait_for()
            bounds=page.get_by_test_id('decoration-dialog').bounding_box()
            assert bounds['x']>=0 and bounds['x']+bounds['width']<=width+1,bounds
            passed('responsive bounded canvas,template and ornament dialogs',width=width)
            page.close()
        browser.close()
except Exception as exc:
    results.append({'passed':False,'error':str(exc)})
    raise
finally:
    REPORT.write_text(json.dumps({'checks':results},ensure_ascii=False,indent=2))
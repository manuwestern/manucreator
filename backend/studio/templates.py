import asyncio
import io
import math
from uuid import UUID
from PIL import Image,ImageDraw,ImageFont
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import Response
from pydantic import Field
from .common import StrictModel
from .models import Design,Element
from .session import guest_id
from .products import get_product,blank_bytes
from .curated_fonts import FAMILIES,path_for
from .text_engine import text_sprite
from .layer_rendering import render_layers

router=APIRouter(prefix='/api/studio/templates',tags=['Gestaltungsvorlagen'])
# x/y/w/h below describe fixed content slots inside the safe inner engraving rectangle.
TEMPLATES=[
 {'id':'monogram','name':'Name oder Monogramm','subtitle':'Ein Name. Dein Zeichen.','requires':'text','fields':[('initials','Initialen oder Name','M','cinzel',.08,.17,.84,.38),('tagline','Zusatzzeile','Dein Unikat','montserrat',.10,.63,.80,.12)]},
 {'id':'wedding','name':'Hochzeit','subtitle':'Für gemeinsame Erinnerungen.','requires':'text','fields':[('names','Zwei Namen','Anna & Ben','great-vibes',.04,.16,.92,.29),('date','Datum','14.06.2026','lora',.15,.51,.70,.12),('dedication','Widmung (optional)','Für immer','montserrat',.10,.73,.80,.10)]},
 {'id':'birthday','name':'Geburtstag oder Jubiläum','subtitle':'Ein besonderer Meilenstein.','requires':'text','fields':[('name','Name','Mia','dancing-script',.12,.08,.76,.17),('number','Zahl','30','bebas-neue',.12,.32,.76,.34),('message','Kurze Botschaft','Alles Liebe','open-sans',.08,.78,.84,.10)]},
 {'id':'photo','name':'Fotogeschenk','subtitle':'Dein Moment bleibt.','requires':'photo','fields':[('photo','Bild ersetzen',None,None,.14,.06,.72,.56),('caption','Bildunterschrift','Unser Moment','lora',.08,.72,.84,.15)]},
 {'id':'company','name':'Firma oder Verein','subtitle':'Ein Zeichen der Zugehörigkeit.','requires':'logo','fields':[('logo','Logo ersetzen',None,None,.22,.05,.56,.42),('company','Name','Dein Verein','oswald',.08,.55,.84,.17),('tagline','Zusatzzeile','Gemeinsam mehr','open-sans',.08,.81,.84,.09)]},
 {'id':'dedication','name':'Schlichte Widmung','subtitle':'Worte, die bleiben.','requires':'text','fields':[('message','Persönliche Botschaft','Für dich','cormorant-garamond',.07,.26,.86,.24),('signature','Absender oder Datum','Von Herzen','caveat',.16,.64,.68,.13)]}
]
BY_ID={t['id']:t for t in TEMPLATES}

class ApplyRequest(StrictModel):
    product_id:str=Field(min_length=2,max_length=80)

def compatible(template,product):
    return template['requires'] in product['templates'] and all(text is None or len(text)<=product['max_text'] for _,_,text,_,*rest in template['fields'])

def make_design(template,product):
    area=product['area'];inset=.15 if area.get('shape')=='circle' else .035
    safe={'x':area['x']+area['w']*inset,'y':area['y']+area['h']*inset,'w':area['w']*(1-inset*2),'h':area['h']*(1-inset*2)}
    elements=[]
    for key,label,text,family,x,y,w,h in template['fields']:
        slot={'x':safe['x']+x*safe['w'],'y':safe['y']+y*safe['h'],'w':w*safe['w'],'h':h*safe['h']}
        shared={'id':f"tpl-{template['id']}-{key}",'template_field':key,'field_label':label,'template_slot':slot,'rotation':0,'curvature':0,'hidden':False,'locked':False}
        if text is None:
            e=Element(**shared,**slot,kind='image',placeholder=True,image_type=template['requires'],asset_id=None)
        else:
            font=FAMILIES[family]['default'];size=min(90,max(4,slot['h']*1.05))
            for _ in range(12):
                _,(tw,th)=text_sprite(str(path_for(font)),text,size,0)
                if tw<=slot['w'] and th<=slot['h']:break
                size=max(4,size*min(slot['w']/tw,slot['h']/th)*.975)
            if tw>slot['w']+.1 or th>slot['h']+.1:raise HTTPException(422,'Diese Vorlage passt nicht in die kleine Gravurfläche.')
            e=Element(**shared,x=slot['x']+(slot['w']-tw)/2,y=slot['y']+(slot['h']-th)/2,w=tw,h=th,kind='text',text=text,font=font,font_size=round(size,4))
        elements.append(e)
    return Design(product_id=product['id'],elements=elements,template=template['requires'],editor_mode='simple',template_id=template['id'],template_version=1)

@router.get('')
async def list_templates(product_id:str):
    product=await get_product(product_id);items=[]
    for template in TEMPLATES:
        if not compatible(template,product):continue
        try:await asyncio.to_thread(make_design,template,product)
        except HTTPException:continue
        items.append({'id':template['id'],'name':template['name'],'subtitle':template['subtitle'],'requires':template['requires'],'version':1,'preview':f"/api/studio/templates/{template['id']}/preview?product_id={product_id}"})
    return {'items':items,'product_id':product_id}

@router.post('/{identity}/apply',response_model=Design)
async def apply_template(identity:str,payload:ApplyRequest,guest=Depends(guest_id)):
    product=await get_product(payload.product_id);template=BY_ID.get(identity)
    if not template or not compatible(template,product):raise HTTPException(422,'Diese Vorlage ist mit dem Rohling nicht vereinbar.')
    return await asyncio.to_thread(make_design,template,product)

def placeholder_png():
    image=Image.new('RGBA',(400,300),'#eeeeee');draw=ImageDraw.Draw(image)
    draw.rounded_rectangle((30,30,370,270),radius=8,outline='#777777',width=4)
    draw.ellipse((100,70,150,120),fill='#999999');draw.polygon([(55,245),(175,115),(245,200),(300,155),(345,245)],fill='#999999')
    out=io.BytesIO();image.save(out,'PNG');return out.getvalue()

@router.get('/{identity}/preview')
async def template_preview(identity:str,product_id:str):
    product=await get_product(product_id);template=BY_ID.get(identity)
    if not template or not compatible(template,product):raise HTTPException(404,'Vorlage nicht verfügbar.')
    design=await asyncio.to_thread(make_design,template,product);assets={}
    for e in design.elements:
        if e.kind=='image':
            e.asset_id=UUID('00000000-0000-0000-0000-000000000001');assets[str(e.asset_id)]=placeholder_png()
    paths={e.font:path_for(e.font) for e in design.elements if e.kind=='text'}
    png=await asyncio.to_thread(render_layers,design,product,await blank_bytes(product),assets,paths)
    return Response(png,media_type='image/png',headers={'Cache-Control':'public, max-age=180'})
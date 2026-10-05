import asyncio
import io
import json
import math
import re
from copy import deepcopy
from functools import lru_cache
from uuid import UUID
from PIL import Image, ImageDraw
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import Field
from .common import StrictModel
from .models import Design, Element
from .session import guest_id
from .products import get_product, blank_bytes
from .curated_fonts import FAMILIES, path_for
from .text_engine import text_sprite
from .engraving_effects import effect_args
from .transform_geometry import inside
from .ornaments import ROUND, BY_ID as ORNAMENTS
from .layer_rendering import render_layers
from .template_catalog import TEMPLATES, BY_ID

router=APIRouter(prefix='/api/studio/templates',tags=['Gestaltungsvorlagen'])

class ApplyRequest(StrictModel):
    product_id:str=Field(min_length=2,max_length=80)

def compact_product(product):
    numbers=re.findall(r'\d+(?:[.,]\d+)?',product.get('area_mm',''))
    return bool(numbers and min(float(n.replace(',','.')) for n in numbers)<45) or product['area']['w']/product['area']['h']>2.1

def compatible(template,product):
    if template['collection'] not in ('universell',product.get('category')):return False
    if template['requires'] not in product['templates'] or 'text' not in product['templates']:return False
    # Wood compositions rely on real decorative space; small metal areas get reduced layouts.
    if template['collection']=='holz' and compact_product(product):return False
    if template.get('wide') and product['area']['w']/product['area']['h']<1.15 and product['area'].get('shape')=='circle':return False
    return all(text is None or len(text)<=product['max_text'] for _,_,text,_,*rest in template['fields'])

def composition(template,product):
    t=deepcopy(template)
    if compact_product(product):
        # Retain each layout's identity but omit secondary flourishes and optional footers.
        t['decorations']=list(t['decorations'])[:1]
        if len(t['fields'])>2 and t['id'] not in ('metal-coordinates','metal-tool','metal-vehicle'):
            t['fields']=t['fields'][:2]
        t['effects']={}
    return t

@lru_cache(maxsize=180)
def _make_cached(identity,product_json):
    product=json.loads(product_json); template=composition(BY_ID[identity],product)
    area=product['area'];inset=.16 if area.get('shape')=='circle' else .04
    safe={'x':area['x']+area['w']*inset,'y':area['y']+area['h']*inset,'w':area['w']*(1-inset*2),'h':area['h']*(1-inset*2)}
    def slot_for(x,y,w,h):return {'x':safe['x']+x*safe['w'],'y':safe['y']+y*safe['h'],'w':w*safe['w'],'h':h*safe['h']}
    elements=[]
    for index,deco in enumerate(template['decorations']):
        slot=slot_for(deco['x'],deco['y'],deco['w'],deco['h'])
        if deco['ornament']=='line':
            slot['y']-=(max(4.5,slot['h'])-slot['h'])/2;slot['h']=max(4.5,slot['h'])
        if deco['ornament'] in ROUND:
            # A true circle, never a stretched ellipse. Circle frames can use the whole round area.
            if area.get('shape')=='circle' and deco['ornament'] in ('circle-frame','double-circle') and deco['w']>.85:
                slot={'x':area['x']+area['w']*.045,'y':area['y']+area['h']*.045,'w':area['w']*.91,'h':area['h']*.91}
            else:
                side=min(slot['w'],slot['h']);slot.update(x=slot['x']+(slot['w']-side)/2,y=slot['y']+(slot['h']-side)/2,w=side,h=side)
        elif deco['ornament'] not in {'rect-frame','double-rect','corner-marks','line'}:
            ratio=ORNAMENTS[deco['ornament']]['ratio'];t=math.radians(deco['rotation']);c,s=abs(math.cos(t)),abs(math.sin(t))
            h=min(slot['w']/(ratio*c+s),slot['h']/(ratio*s+c));w=h*ratio
            slot.update(x=slot['x']+(slot['w']-w)/2,y=slot['y']+(slot['h']-h)/2,w=w,h=h)
        stroke=min(deco['stroke_width'],max(.3,min(slot['w'],slot['h'])*.12))
        e=Element(id=f"tpl-{identity}-deco-{index}",kind='decoration',**slot,ornament=deco['ornament'],stroke_width=stroke,rotation=deco['rotation'],locked=True,field_label=ORNAMENTS[deco['ornament']]['name'])
        if min(e.w,e.h)<4 or not inside(e.model_dump(),area,0):raise HTTPException(422,'Diese Dekoration passt nicht in die Gravurfläche.')
        elements.append(e)
    for key,label,text,family,x,y,w,h in template['fields']:
        slot=slot_for(x,y,w,h)
        shared={'id':f'tpl-{identity}-{key}','template_field':key,'field_label':label,'template_slot':slot}
        if text is None:
            e=Element(**shared,**slot,kind='image',placeholder=True,image_type=template['requires'])
        else:
            font=FAMILIES[family]['default'];size=min(90,max(4,slot['h']*1.05));effects=template['effects'].get(key,{})
            probe=Element(id='probe',kind='text',x=0,y=0,w=1,h=1,**effects)
            for _ in range(15):
                _,(tw,th)=text_sprite(str(path_for(font)),text,size,probe.curvature,*effect_args(probe))
                if tw<=slot['w'] and th<=slot['h']:break
                size=max(4,size*min(slot['w']/tw,slot['h']/th)*.97)
            if tw>slot['w']+.01 or th>slot['h']+.01:raise HTTPException(422,'Diese Vorlage passt nicht in die kleine Gravurfläche.')
            e=Element(**shared,x=slot['x']+(slot['w']-tw)/2,y=slot['y']+(slot['h']-th)/2,w=tw,h=th,kind='text',text=text,font=font,font_size=round(size,4),**effects)
        if not inside(e.model_dump(),area,0):raise HTTPException(422,'Diese Vorlage passt nicht in die Form der Gravurfläche.')
        elements.append(e)
    return Design(product_id=product['id'],elements=elements,template=template['requires'],editor_mode='simple',template_id=identity,template_version=2).model_dump(mode='json')

def make_design(template,product):
    relevant={key:product.get(key) for key in ('id','area','area_mm','category','max_text')}
    return Design.model_validate(_make_cached(template['id'],json.dumps(relevant,sort_keys=True)))

@router.get('')
async def list_templates(product_id:str):
    product=await get_product(product_id);items=[]
    for template in TEMPLATES:
        if not compatible(template,product):continue
        try:await asyncio.to_thread(make_design,template,product)
        except HTTPException:continue
        items.append({key:template[key] for key in ('id','name','subtitle','requires','collection','occasion')} | {'version':2,'compact':compact_product(product),'preview':f"/api/studio/templates/{template['id']}/preview?product_id={product_id}&v={product['version']}"})
    return {'items':items,'product_id':product_id,'catalog_count':40,'collections':{'holz':16,'metall':14,'universell':10}}

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

@lru_cache(maxsize=90)
def preview_png(design_json,product_json,blank):
    design=Design.model_validate_json(design_json);product=json.loads(product_json);assets={}
    for e in design.elements:
        if e.kind=='image':
            e.asset_id=UUID('00000000-0000-0000-0000-000000000001');assets[str(e.asset_id)]=placeholder_png()
    paths={e.font:path_for(e.font) for e in design.elements if e.kind=='text'}
    png=render_layers(design,product,blank,assets,paths)
    image=Image.open(io.BytesIO(png));image.thumbnail((420,420),Image.Resampling.LANCZOS)
    out=io.BytesIO();image.save(out,'PNG');return out.getvalue()

@router.get('/{identity}/preview')
async def template_preview(identity:str,product_id:str):
    product=await get_product(product_id);template=BY_ID.get(identity)
    if not template or not compatible(template,product):raise HTTPException(404,'Vorlage nicht verfügbar.')
    design=await asyncio.to_thread(make_design,template,product)
    png=await asyncio.to_thread(preview_png,design.model_dump_json(),json.dumps(product,sort_keys=True),await blank_bytes(product))
    return Response(png,media_type='image/png',headers={'Cache-Control':'public, max-age=180'})
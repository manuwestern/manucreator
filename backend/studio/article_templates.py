import asyncio
import io
import re
import uuid
from copy import deepcopy
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import Response
from pydantic import BaseModel,Field,field_validator
from .common import StrictModel,db,now
from .admin_auth import current_admin
from .session import guest_id
from .models import Design,Box
from .products import get_product,blank_bytes
from .layer_rendering import validate_elements,render_layers
from .fonts import font_path
from .text_engine import validate_chars
from .decoration_library import record as decoration,normalized_bytes,grant,permitted

router=APIRouter(prefix='/api/admin/article-templates',tags=['Artikelvorlagen'],dependencies=[Depends(current_admin)])
public=APIRouter(prefix='/api/studio/article-templates',tags=['Artikelvorlagen'])

class TemplateInput(StrictModel):
    name:str=Field(min_length=2,max_length=80)
    design:Design
    allow_free_edit:bool=True
    sort_order:int=Field(default=0,ge=0,le=10000)
    revision:int=Field(default=1,ge=1)

    @field_validator('name')
    @classmethod
    def meaningful_name(cls,value):
        if len(value.strip())<2:raise ValueError('Bitte einen verständlichen Vorlagennamen angeben.')
        return value.strip()

class TemplateResponse(BaseModel):
    id:str
    product_id:str
    name:str
    design:Design
    allow_free_edit:bool
    sort_order:int
    revision:int
    archived:bool
    published_revision_id:str|None=None
    has_changes:bool=True
    availability_error:str|None=None

class Version(StrictModel):
    revision:int=Field(ge=1)

async def get_template(identity):
    item=await db().studio_article_templates.find_one({'id':identity},{'_id':0})
    if not item:raise HTTPException(404,'Vorlage nicht gefunden.')
    return item

async def check_template(design,product,publishing=True):
    checked=design.model_copy(deep=True);checked.editor_mode='simple'
    validate_elements(checked,product,allow_placeholders=True)
    fields=set()
    for e in design.elements or []:
        if e.kind=='text':
            validate_chars(await font_path(e.font),e.text)
            if 'text' not in product['templates']:raise HTTPException(422,'Text ist auf diesem Artikel nicht freigegeben.')
        if e.template_field:
            if e.template_field in fields or not (e.field_label or '').strip():raise HTTPException(422,'Kundenfelder benötigen eindeutige Kennungen und verständliche Bezeichnungen.')
            fields.add(e.template_field)
            if e.kind=='text' and (e.field_max_length or product['max_text'])>product['max_text']:raise HTTPException(422,'Die Feldlänge überschreitet das Textlimit des Artikels.')
            if e.kind=='text' and len(e.text)>(e.field_max_length or product['max_text']):raise HTTPException(422,'Ein Beispieltext ist länger als die für sein Kundenfeld freigegebene Zeichenanzahl.')
            if e.kind=='text' and e.field_required and not e.text.strip():raise HTTPException(422,'Pflichtfelder benötigen einen Beispielwert.')
        if e.kind=='image':
            if not e.template_field or e.image_type not in product['templates']:raise HTTPException(422,'Bildfelder müssen als zulässige Kundenfoto- oder Logofelder angelegt sein.')
            if e.asset_id:raise HTTPException(422,'Artikelvorlagen verwenden Bildplatzhalter, keine privaten Kundenbilder.')
        if e.kind=='decoration' and e.decoration_id:
            item=await decoration(str(e.decoration_id))
            if not item['confirmed'] or (publishing and item['state']!='published'):raise HTTPException(422,'Alle verwendeten eigenen Dekorationen müssen bestätigt und veröffentlicht sein.')
            if abs(e.w/e.h/item['ratio']-1)>.012:raise HTTPException(422,'Eigene Dekorationen müssen proportional bleiben.')

async def availability(item,product):
    if item['archived'] or not item.get('published_revision_id'):raise HTTPException(404,'Vorlage nicht veröffentlicht.')
    revision=await db().studio_template_revisions.find_one({'id':item['published_revision_id']},{'_id':0})
    if not revision:raise HTTPException(404,'Vorlagenversion nicht gefunden.')
    await check_template(Design.model_validate(revision['design']),product)
    return revision

async def decorate_status(item):
    result={**item,'availability_error':None}
    if item.get('published_revision_id') and not item['archived']:
        try:await availability(item,await get_product(item['product_id'],active=False))
        except HTTPException as e:result['availability_error']=e.detail
    return result

@router.get('',response_model=list[TemplateResponse])
async def list_admin(product_id:str):
    items=await db().studio_article_templates.find({'product_id':product_id},{'_id':0}).sort('sort_order',1).to_list(200)
    return [await decorate_status(i) for i in items]

@router.post('',response_model=TemplateResponse,status_code=201)
async def create(payload:TemplateInput):
    await get_product(payload.design.product_id,active=False)
    item={**payload.model_dump(mode='json'),'id':str(uuid.uuid4()),'product_id':payload.design.product_id,'revision':1,'archived':False,'published_revision_id':None,'has_changes':True,'created_at':now().isoformat()}
    await db().studio_article_templates.insert_one(item.copy());return item

@router.get('/{identity}',response_model=TemplateResponse)
async def get_admin(identity:str):return await decorate_status(await get_template(identity))

@router.put('/{identity}',response_model=TemplateResponse)
async def edit(identity:str,payload:TemplateInput):
    item=await get_template(identity)
    if payload.design.product_id!=item['product_id']:raise HTTPException(422,'Eine Vorlage gehört genau zu ihrem Artikel.')
    values=payload.model_dump(mode='json');values.update(revision=item['revision']+1,has_changes=True)
    changed=await db().studio_article_templates.update_one({'id':identity,'revision':payload.revision},{'$set':values})
    if not changed.modified_count:raise HTTPException(409,'Vorlage wurde zwischenzeitlich geändert. Bitte neu öffnen.')
    return await decorate_status(await get_template(identity))

@router.post('/{identity}/duplicate',response_model=TemplateResponse,status_code=201)
async def duplicate(identity:str):
    item=await get_template(identity)
    return await create(TemplateInput(name=(item['name']+' – Kopie')[:80],design=Design.model_validate(item['design']),allow_free_edit=item['allow_free_edit'],sort_order=min(10000,item['sort_order']+1)))

@router.post('/{identity}/archive',response_model=TemplateResponse)
async def archive(identity:str):
    await get_template(identity);await db().studio_article_templates.update_one({'id':identity},{'$set':{'archived':True},'$inc':{'revision':1}})
    return await get_template(identity)

@router.post('/{identity}/publish',response_model=TemplateResponse)
async def publish(identity:str,payload:Version):
    item=await get_template(identity)
    if item['revision']!=payload.revision:raise HTTPException(409,'Vorlage wurde geändert. Bitte neu öffnen.')
    product=await get_product(item['product_id']);design=Design.model_validate(item['design'])
    await check_template(design,product)
    revision_id=str(uuid.uuid4());design.editor_mode='simple';design.template_id=identity;design.template_revision_id=uuid.UUID(revision_id);design.allow_free_edit=item['allow_free_edit'];design.template_version=item['revision']
    for index,e in enumerate(design.elements):
        e.id=f'own-{uuid.UUID(revision_id).hex}-{index}'
        if e.template_field and not e.template_slot:e.template_slot=Box(x=e.x,y=e.y,w=e.w,h=e.h)
    revision={'id':revision_id,'template_id':identity,'product_id':item['product_id'],'name':item['name'],'design':design.model_dump(mode='json'),'allow_free_edit':item['allow_free_edit'],'created_at':now().isoformat()}
    await db().studio_template_revisions.insert_one(revision.copy())
    changed=await db().studio_article_templates.update_one({'id':identity,'revision':payload.revision},{'$set':{'published_revision_id':revision_id,'has_changes':False,'archived':False},'$inc':{'revision':1}})
    if not changed.modified_count:raise HTTPException(409,'Zwischenzeitliche Änderung. Veröffentlichung nicht übernommen.')
    return await get_template(identity)

async def rendered_preview(design,product):
    from .templates import placeholder_png
    assets={}
    for e in design.elements or []:
        if e.kind=='image':e.asset_id=uuid.UUID(int=1);assets[str(e.asset_id)]=placeholder_png()
        if e.kind=='decoration' and e.decoration_id:assets['decoration:'+str(e.decoration_id)]=await normalized_bytes(str(e.decoration_id))
    paths={e.font:await font_path(e.font) for e in design.elements or [] if e.kind=='text'}
    return await asyncio.to_thread(render_layers,design,product,await blank_bytes(product),assets,paths)

@router.get('/{identity}/preview')
async def admin_preview(identity:str):
    item=await get_template(identity);product=await get_product(item['product_id'],active=False)
    return Response(await rendered_preview(Design.model_validate(item['design']),product),media_type='image/png',headers={'Cache-Control':'no-store'})

async def public_items(product):
    items=await db().studio_article_templates.find({'product_id':product['id'],'archived':False,'published_revision_id':{'$ne':None}},{'_id':0}).sort('sort_order',1).to_list(200)
    result=[]
    for item in items:
        try:revision=await availability(item,product)
        except HTTPException:continue
        result.append({'id':item['id'],'name':revision['name'],'collection':'eigene','occasion':'Eigene Vorlagen','subtitle':'Für diesen Artikel','requires':revision['design']['template'],'own':True,'version':revision['id'],'preview':f'/api/studio/article-templates/{item["id"]}/preview?v={revision["id"]}'})
    return result

@public.get('/{identity}/preview')
async def customer_preview(identity:str):
    item=await get_template(identity);product=await get_product(item['product_id']);revision=await availability(item,product)
    return Response(await rendered_preview(Design.model_validate(revision['design']),product),media_type='image/png',headers={'Cache-Control':'no-store'})

@public.post('/{identity}/apply',response_model=Design)
async def apply(identity:str,guest=Depends(guest_id)):
    item=await get_template(identity);product=await get_product(item['product_id']);revision=await availability(item,product)
    await db().studio_template_uses.update_one({'guest':guest,'revision_id':revision['id']},{'$setOnInsert':{'created_at':now().isoformat()}},upsert=True)
    for e in revision['design']['elements']:
        if e.get('decoration_id'):await grant(guest,e['decoration_id'])
    return revision['design']

async def enforce_customer_template(design,guest):
    identities={str(design.template_revision_id)} if design.template_revision_id else set()
    for e in design.elements or []:
        match=re.fullmatch(r'own-([a-f0-9]{32})-\d+',e.id)
        if match:identities.add(str(uuid.UUID(match[1])))
    for identity in identities:
        revision=await db().studio_template_revisions.find_one({'id':identity},{'_id':0})
        used=await db().studio_template_uses.find_one({'guest':guest,'revision_id':identity},{'_id':0})
        if not revision or not used:raise HTTPException(403,'Diese Vorlagenversion gehört nicht zu deinem Entwurf.')
        if revision['allow_free_edit'] and design.editor_mode=='free':continue
        base=Design.model_validate(revision['design'])
        if str(design.template_revision_id)!=identity or design.product_id!=base.product_id or design.template_id!=base.template_id or design.editor_mode!='simple' or design.allow_free_edit!=base.allow_free_edit:
            raise HTTPException(422,'Diese Vorlage darf ausschließlich über ihre freigegebenen Kundenfelder personalisiert werden.')
        if [e.id for e in design.elements]!=[e.id for e in base.elements]:raise HTTPException(422,'Die festen Ebenen der Vorlage müssen erhalten bleiben.')
        for actual,original in zip(design.elements,base.elements):
            allowed=set()
            if original.template_field:
                allowed={'x','y','w','h','text'} if original.kind=='text' else {'x','y','w','h','asset_id','original_asset_id','crop','image_ratio','placeholder'}
                slot=original.template_slot
                if not slot or actual.x<slot.x-.1 or actual.y<slot.y-.1 or actual.x+actual.w>slot.x+slot.w+.1 or actual.y+actual.h>slot.y+slot.h+.1:raise HTTPException(422,'Ein Inhalt überschreitet sein freigegebenes Vorlagenfeld.')
                if actual.kind=='text' and ((original.field_required and not actual.text.strip()) or len(actual.text)>(original.field_max_length or 60)):raise HTTPException(422,'Bitte Pflichtfelder und freigegebene Textlängen beachten.')
            if actual.model_dump(exclude=allowed)!=original.model_dump(exclude=allowed):raise HTTPException(422,'Feste Inhalte oder Eigenschaften einer geschützten Vorlage wurden verändert.')

async def decoration_assets(design,guest):
    assets={}
    for e in design.elements or []:
        if e.kind=='decoration' and e.decoration_id:
            item=await permitted(str(e.decoration_id),guest)
            if abs(e.w/e.h/item['ratio']-1)>.012:raise HTTPException(422,'Dekorationen dürfen nicht verzerrt werden.')
            assets['decoration:'+str(e.decoration_id)]=await normalized_bytes(str(e.decoration_id))
    return assets
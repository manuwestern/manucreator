import asyncio
import hashlib
import json
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pymongo.errors import DuplicateKeyError
from .common import db, now, owned
from .models import Design, Layout
from .geometry import default_layout
from .products import get_product, blank_bytes, CatalogResponse
from .session import guest_id, SessionRequest, create_session
from .storage import save_file, read_file
from .rendering import clean_upload, validate_design, render_design
from .layer_rendering import validate_elements, render_layers
from .responses import DraftResponse
from .fonts import font_path
from .text_engine import validate_chars

router=APIRouter(prefix='/api/studio',tags=['Gestaltungsstudio'])

@router.get('/products',response_model=CatalogResponse)
async def products():
    return {'products':await db().studio_products.find({'active':True},{'_id':0}).to_list(500),'mode':'test','production_approved':False}

@router.post('/session')
async def session(payload:SessionRequest,request:Request):
    return await create_session(payload,request)

@router.post('/uploads',status_code=201)
async def upload(file:UploadFile=File(...),rights_confirmed:bool=Form(...),guest=Depends(guest_id)):
    if not rights_confirmed:
        raise HTTPException(422,'Bitte bestätige, dass du das Bild verwenden darfst.')
    if await db().studio_files.count_documents({'guest':guest,'kind':'upload','source_id':{'$exists':False},'is_deleted':False})>=12:
        raise HTTPException(429,'Für diesen Gastzugang sind höchstens 12 eigene Bilder möglich.')
    content=await file.read(8*1024*1024+1)
    if len(content)>8*1024*1024:
        raise HTTPException(413,'Bitte ein Bild mit höchstens 8 MB auswählen.')
    image,dimensions=await asyncio.to_thread(clean_upload,content)
    identity=await save_file(guest,image,'upload',extra={'original_name':(file.filename or 'Bild')[:160],'width':dimensions[0],'height':dimensions[1],'digest':hashlib.sha256(image).hexdigest(),'rights_confirmed':True})
    return {'id':identity,'width':dimensions[0],'height':dimensions[1],'warning':'Für feine Details ist ein größeres Bild empfehlenswert.' if min(dimensions)<600 else None}

@router.get('/files/{identity}')
async def file_bytes(identity:str,guest=Depends(guest_id)):
    content,record=await read_file(identity,guest)
    return Response(content=content,media_type=record['mime'],headers={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'})

@router.post('/drafts',response_model=DraftResponse)
async def save_draft(design:Design,guest=Depends(guest_id)):
    product=await get_product(design.product_id)
    if design.elements is not None:
        from .article_templates import enforce_customer_template
        await enforce_customer_template(design,guest)
        validate_elements(design,product)
        texts=[e.text for e in design.elements if e.kind=='text' and not e.hidden]
        design.text=texts[0] if texts else '';design.subtitle=texts[1][:36] if len(texts)>1 else ''
        images=[e for e in design.elements if e.kind=='image']
        identities={str(e.asset_id) for e in images}|{str(e.original_asset_id) for e in images if e.original_asset_id}
        design.asset_id=None;design.layout=None
    else:
        if not design.layout:
            design.layout=Layout(**default_layout(design,product))
        validate_design(design,product)
        if design.template=='text':
            design.asset_id=None;design.zoom=1;design.focal_x=0;design.focal_y=0
        identities={str(design.asset_id)} if design.asset_id else set()
    digests={}
    for identity in identities:
        asset=await owned('studio_files',identity,guest)
        if asset['kind']!='upload':
            raise HTTPException(422,'Bitte eigene Fotos oder Logos auswählen.')
        digests[identity]=asset['digest']
    config=design.model_dump(mode='json')
    hashed_config=json.loads(json.dumps(config))
    if design.elements is not None:
        for element in hashed_config['elements']:
            for field in ('asset_id','original_asset_id'):
                if element[field]:
                    element[field]=digests[element[field]]
    else:
        hashed_config['asset_id']=digests.get(str(design.asset_id),'')
    hashed_config['product_version']=product['version']
    fingerprint=hashlib.sha256(json.dumps(hashed_config,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    old=await db().studio_drafts.find_one({'guest':guest,'fingerprint':fingerprint},{'_id':0})
    if old:
        return old
    if await db().studio_drafts.count_documents({'guest':guest})>=30:
        raise HTTPException(429,'Du hast bereits 30 gespeicherte Musterentwürfe.')
    blank=await blank_bytes(product)
    if design.elements is not None:
        assets={identity:(await read_file(identity,guest))[0] for identity in {str(e.asset_id) for e in images}}
        from .article_templates import decoration_assets
        assets.update(await decoration_assets(design,guest))
        font_paths={e.font:await font_path(e.font) for e in design.elements if e.kind=='text'}
        for e in design.elements:
            if e.kind=='text':validate_chars(font_paths[e.font],e.text)
            if e.kind=='image' and e.image_ratio>0:
                from PIL import Image
                import io
                image=Image.open(io.BytesIO(assets[str(e.asset_id)]))
                ratio=image.width*e.crop.w/(image.height*e.crop.h)
                if abs(e.w/e.h/ratio-1)>.012:
                    raise HTTPException(422,'Das Bild muss proportional bleiben. Bitte den Zuschnitt oder die Größe im Editor erneut prüfen.')
        rendered=await asyncio.to_thread(render_layers,design,product,blank,assets,font_paths)
    else:
        content=(await read_file(str(design.asset_id),guest))[0] if design.asset_id else None
        rendered=await asyncio.to_thread(render_design,design,content,product,blank)
    render_id=await save_file(guest,rendered,'design_render')
    draft={'id':str(uuid.uuid4()),'guest':guest,'design':config,'product_snapshot':product,'fingerprint':fingerprint,'render_id':render_id,'ai_status':'none','ai_attempts':0,'is_sample':product['is_sample'],'production_approved':False,'created_at':now().isoformat()}
    try:
        await db().studio_drafts.insert_one(draft.copy())
    except DuplicateKeyError:
        return await db().studio_drafts.find_one({'guest':guest,'fingerprint':fingerprint},{'_id':0})
    return draft

@router.get('/drafts/{identity}',response_model=DraftResponse)
async def draft_detail(identity:str,guest=Depends(guest_id)):
    return await owned('studio_drafts',identity,guest)
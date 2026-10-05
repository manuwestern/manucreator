import asyncio
import base64
import uuid
from typing import Literal
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from .common import StrictModel, db, now
from .admin_auth import current_admin
from .session import guest_id
from .storage import save_file, read_file
from .products import get_product
from .decoration_uploads import normalize_decoration

OWNER='admin-decoration-library'
router=APIRouter(prefix='/api/admin/decorations',tags=['Eigene Dekorationen'],dependencies=[Depends(current_admin)])
public=APIRouter(prefix='/api/studio',tags=['Eigene Dekorationen'])

class DecorationResponse(BaseModel):
    id:str
    name:str
    published_name:str|None=None
    state:Literal['draft','published','archived']
    confirmed:bool
    width:int
    height:int
    ratio:float
    mime:str
    created_at:str

class Rename(StrictModel):
    name:str=Field(min_length=2,max_length=80)

class Confirmation(StrictModel):
    confirmed:Literal[True]

class Use(StrictModel):
    product_id:str=Field(max_length=80)

async def record(identity):
    item=await db().studio_decorations.find_one({'id':identity},{'_id':0})
    if not item:raise HTTPException(404,'Dekoration nicht gefunden.')
    return item

async def normalized_bytes(identity):
    item=await record(identity)
    return (await read_file(item['preview_file_id'],OWNER))[0]

async def grant(guest,identity):
    await db().studio_decoration_grants.update_one({'guest':guest,'decoration_id':identity},{'$setOnInsert':{'created_at':now().isoformat()}},upsert=True)

async def permitted(identity,guest):
    if not await db().studio_decoration_grants.find_one({'guest':guest,'decoration_id':identity},{'_id':0}):
        raise HTTPException(403,'Dieses Motiv ist für diesen Entwurf nicht freigegeben.')
    return await record(identity)

def sprite(data,item):return {'image':'data:image/png;base64,'+base64.b64encode(data).decode(),'width':item['width'],'height':item['height']}

@router.get('',response_model=list[DecorationResponse])
async def library():return await db().studio_decorations.find({},{'_id':0}).sort('created_at',-1).to_list(500)

@router.post('/upload',response_model=DecorationResponse,status_code=201)
async def upload(file:UploadFile=File(...),name:str=Form(...)):
    name=name.strip()
    if not 2<=len(name)<=80:raise HTTPException(422,'Bitte einen Namen mit 2–80 Zeichen angeben.')
    content=await file.read(8*1024*1024+1)
    png,(w,h),mime=await asyncio.to_thread(normalize_decoration,content,file.filename or '')
    original=await save_file(OWNER,content,'decoration_original',mime)
    preview=await save_file(OWNER,png,'decoration_preview')
    item={'id':str(uuid.uuid4()),'name':name,'published_name':None,'state':'draft','confirmed':False,'original_file_id':original,'preview_file_id':preview,'width':w,'height':h,'ratio':w/h,'mime':mime,'created_at':now().isoformat()}
    await db().studio_decorations.insert_one(item.copy());return item

@router.patch('/{identity}',response_model=DecorationResponse)
async def rename(identity:str,payload:Rename):
    await record(identity);await db().studio_decorations.update_one({'id':identity},{'$set':{'name':payload.name}});return await record(identity)

@router.post('/{identity}/confirm',response_model=DecorationResponse)
async def confirm(identity:str,payload:Confirmation):
    await record(identity);await db().studio_decorations.update_one({'id':identity},{'$set':{'confirmed':True}});return await record(identity)

@router.post('/{identity}/publish',response_model=DecorationResponse)
async def publish(identity:str):
    item=await record(identity)
    if not item['confirmed']:raise HTTPException(422,'Bitte zuerst die einfarbige Darstellung ausdrücklich bestätigen.')
    await db().studio_decorations.update_one({'id':identity},{'$set':{'state':'published','published_name':item['name']}});return await record(identity)

@router.post('/{identity}/archive',response_model=DecorationResponse)
async def archive(identity:str):
    await record(identity);await db().studio_decorations.update_one({'id':identity},{'$set':{'state':'archived'}});return await record(identity)

@router.get('/{identity}/sprite')
async def admin_sprite(identity:str):return sprite(await normalized_bytes(identity),await record(identity))

@router.get('/{identity}/original')
async def original(identity:str):
    item=await record(identity);data,_=await read_file(item['original_file_id'],OWNER)
    return Response(data,media_type='application/octet-stream',headers={'Content-Disposition':f'attachment; filename="Dekoration-{identity}.{"svg" if item["mime"]=="image/svg+xml" else "png"}"','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})

@public.get('/own-decorations')
async def offered(product_id:str):
    product=await get_product(product_id)
    items=await db().studio_decorations.find({'id':{'$in':product.get('decoration_ids',[])},'state':'published','confirmed':True},{'_id':0}).to_list(500)
    return {'items':[{'id':i['id'],'name':i['published_name'],'ratio':i['ratio'],'category':'Eigene Motive','preview':f'/api/studio/own-decorations/{i["id"]}/thumbnail?product_id={product_id}'} for i in items]}

async def offered_item(identity,product_id):
    product=await get_product(product_id);item=await record(identity)
    if identity not in product.get('decoration_ids',[]) or item['state']!='published' or not item['confirmed']:raise HTTPException(404,'Dekoration für diesen Artikel nicht freigegeben.')
    return item

@public.get('/own-decorations/{identity}/thumbnail')
async def thumbnail(identity:str,product_id:str):
    await offered_item(identity,product_id)
    return Response(await normalized_bytes(identity),media_type='image/png',headers={'Cache-Control':'no-store'})

@public.post('/own-decorations/{identity}/use')
async def use(identity:str,payload:Use,guest=Depends(guest_id)):
    item=await offered_item(identity,payload.product_id);await grant(guest,identity)
    return {'id':identity,'name':item['published_name'],'ratio':item['ratio']}

@public.get('/decoration-assets/{identity}')
async def customer_sprite(identity:str,guest=Depends(guest_id)):
    item=await permitted(identity,guest);return sprite(await normalized_bytes(identity),item)
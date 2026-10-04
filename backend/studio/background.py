import asyncio
import base64
import hashlib
import io
import logging
import os
from uuid import UUID
from datetime import timedelta
from PIL import Image,ImageOps
from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field
from pymongo.errors import DuplicateKeyError
from .common import StrictModel,db,now,owned
from .session import guest_id
from .storage import read_file,save_file

router=APIRouter(prefix='/api/studio/uploads',tags=['GPT-Freistellung'])

class CutoutRequest(StrictModel):
    request_id:UUID
    consent:bool=Field(...)

@router.get('/background-capabilities')
async def capabilities():
    return {'configured':bool(os.environ.get('OPENAI_API_KEY')),'provider':'OpenAI','model':os.environ['OPENAI_IMAGE_MODEL'],'reason':None if os.environ.get('OPENAI_API_KEY') else 'OpenAI-API-Zugang nicht eingerichtet.','requires_consent':True}

def result_shape(item,reused=False):
    return {key:item[key] for key in ['id','original_id','width','height']}|{'reused':reused,'provider':'OpenAI'}

async def reserve_quota(guest):
    reserved=[]
    for scope,limit in [('global',int(os.environ['STUDIO_BG_GLOBAL_DAILY_LIMIT'])),(guest,int(os.environ['STUDIO_BG_DAILY_LIMIT']))]:
        identity=now().date().isoformat()+':gpt-cutout:'+scope
        try:await db().studio_quotas.update_one({'_id':identity},{'$setOnInsert':{'count':0}},upsert=True)
        except DuplicateKeyError:pass
        result=await db().studio_quotas.update_one({'_id':identity,'count':{'$lt':limit}},{'$inc':{'count':1}})
        if not result.modified_count:
            for key in reserved:await db().studio_quotas.update_one({'_id':key},{'$inc':{'count':-1}})
            raise HTTPException(429,'Das heutige Freistell-Limit ist erreicht.')
        reserved.append(identity)

def normalize_result(data,source_size):
    image=Image.open(io.BytesIO(data)).convert('RGBA')
    alpha=image.getchannel('A')
    low,high=alpha.getextrema()
    if low==255 or high==0:raise ValueError('No valid transparent foreground')
    # Uniform containment, never stretch/crop the provider output into the source frame.
    image=ImageOps.contain(image,source_size,Image.Resampling.LANCZOS)
    framed=Image.new('RGBA',source_size)
    framed.alpha_composite(image,((source_size[0]-image.width)//2,(source_size[1]-image.height)//2))
    out=io.BytesIO();framed.save(out,'PNG');return out.getvalue()

@router.post('/{identity}/remove-background')
async def remove_background(identity:str,payload:CutoutRequest,guest=Depends(guest_id)):
    record=await owned('studio_files',identity,guest)
    if record['kind']!='upload':raise HTTPException(422,'Bitte ein eigenes Foto oder Logo auswählen.')
    if not payload.consent:raise HTTPException(422,'Bitte die Übertragung an OpenAI und mögliche API-Kosten ausdrücklich bestätigen.')
    if not os.environ.get('OPENAI_API_KEY'):raise HTTPException(503,'OpenAI-API-Zugang nicht eingerichtet. Es erfolgt keine Ersatzverarbeitung.')
    source=record.get('source_id') or identity
    fingerprint=hashlib.sha256((source+':'+os.environ['OPENAI_IMAGE_MODEL']+':cutout-v1').encode()).hexdigest()
    cached=await db().studio_processed.find_one({'guest':guest,'fingerprint':fingerprint},{'_id':0})
    if cached:return result_shape(cached,True)
    query={'guest':guest,'request_id':str(payload.request_id)}
    prior=await db().studio_bg_requests.find_one(query,{'_id':0})
    if prior:
        if prior['source']!=source:raise HTTPException(409,'Diese Anfragekennung gehört zu einem anderen Bild.')
        raise HTTPException(409,'Diese Anfrage läuft bereits oder ist abgeschlossen. Es wird kein weiterer kostenpflichtiger Aufruf gestartet.')
    try:
        await db().studio_bg_requests.insert_one({**query,'source':source,'status':'processing','consent':True,'consent_version':'gpt-cutout-v1','created_at':now().isoformat()})
    except DuplicateKeyError:raise HTTPException(409,'Diese Freistellung wurde bereits gestartet.')
    lock_id=guest+':'+fingerprint
    try:
        await db().studio_bg_locks.update_one({'_id':lock_id},{'$setOnInsert':{'busy_until':now()-timedelta(seconds=1)}},upsert=True)
    except DuplicateKeyError:pass
    locked=await db().studio_bg_locks.update_one({'_id':lock_id,'busy_until':{'$lt':now()}},{'$set':{'busy_until':now()+timedelta(minutes=4)}})
    if not locked.modified_count:
        await db().studio_bg_requests.update_one(query,{'$set':{'status':'duplicate'}})
        raise HTTPException(409,'Für dieses Bild läuft bereits eine Freistellung. Es wurde kein weiterer Aufruf gestartet.')
    try:
        await reserve_quota(guest)
        content,_=await read_file(source,guest)
        original_size=Image.open(io.BytesIO(content)).size
        from openai import AsyncOpenAI
        client=AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'],base_url=os.environ['OPENAI_API_BASE_URL'],max_retries=0,timeout=160)
        async with client:
            response=await client.images.edit(model=os.environ['OPENAI_IMAGE_MODEL'],image=('source.png',content,'image/png'),prompt='Remove only the background of the provided image. Preserve the entire foreground subject, its identity, proportions, colors, textures, facial details, logos and readable text. Do not recreate or restyle the subject. No cropping. Keep subject orientation and framing. Return actual transparent pixels, not a checkerboard or solid backdrop.',background='transparent',output_format='png',quality='high',size='auto',n=1)
        result=await asyncio.to_thread(normalize_result,base64.b64decode(response.data[0].b64_json),original_size)
        file_id=await save_file(guest,result,'upload',extra={'source_id':source,'width':original_size[0],'height':original_size[1],'digest':hashlib.sha256(result).hexdigest(),'rights_confirmed':True,'processor':'openai-image-edit'})
        item={'id':file_id,'original_id':source,'guest':guest,'fingerprint':fingerprint,'width':original_size[0],'height':original_size[1],'created_at':now().isoformat(),'provider':'OpenAI'}
        try:await db().studio_processed.insert_one(item.copy())
        except DuplicateKeyError:
            item=await db().studio_processed.find_one({'guest':guest,'fingerprint':fingerprint},{'_id':0})
        await db().studio_bg_requests.update_one(query,{'$set':{'status':'succeeded','result_id':item['id']}})
        return result_shape(item)
    except HTTPException:
        await db().studio_bg_requests.update_one(query,{'$set':{'status':'failed'}});raise
    except Exception:
        logging.getLogger(__name__).warning('GPT cutout failed; original preserved; request_id=%s',payload.request_id)
        await db().studio_bg_requests.update_one(query,{'$set':{'status':'failed'}})
        raise HTTPException(502,'OpenAI konnte keine gültige Freistellung liefern. Das Original bleibt unverändert. Es wurde kein automatischer Wiederholungsaufruf ausgelöst.')
    finally:
        await db().studio_bg_locks.update_one({'_id':lock_id},{'$set':{'busy_until':now()-timedelta(seconds=1)}})
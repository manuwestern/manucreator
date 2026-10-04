import asyncio
import hashlib
import io
import logging
import os
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError
from .common import db, now, owned
from .session import guest_id
from .storage import read_file, save_file

router=APIRouter(prefix='/api/studio/uploads',tags=['Bildbearbeitung'])
processing_lock=asyncio.Lock()

class ProcessedImage(BaseModel):
    id: str
    original_id: str
    width: int
    height: int
    reused: bool = False

@lru_cache(maxsize=1)
def model_session():
    import onnxruntime as ort
    from rembg.sessions.u2netp import U2netpSession
    model=os.environ['STUDIO_BG_MODEL']
    if model!='u2netp':
        raise RuntimeError('Only the explicitly approved u2netp model is permitted')
    path=Path(os.environ['REMBG_HOME']) / 'models' / 'u2netp' / 'u2netp.onnx'
    if not path.is_file():
        raise RuntimeError('Local background removal model missing')
    options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
    return U2netpSession(model,options,providers=['CPUExecutionProvider'])

def segment(content):
    from rembg import remove
    result=remove(content,session=model_session(),force_return_bytes=True)
    image=Image.open(io.BytesIO(result)).convert('RGBA')
    if image.getchannel('A').getextrema()[1]==0:
        raise ValueError('No foreground detected')
    return result, image.size

@router.post('/{identity}/remove-background',response_model=ProcessedImage)
async def remove_background(identity:str,guest=Depends(guest_id)):
    original=await owned('studio_files',identity,guest)
    if original['kind']!='upload':
        raise HTTPException(422,'Bitte ein eigenes Foto oder Logo auswählen.')
    source=original.get('source_id') or identity
    fingerprint=hashlib.sha256((source+':u2netp:v1').encode()).hexdigest()
    query={'guest':guest,'fingerprint':fingerprint}
    async def cached():
        item=await db().studio_processed.find_one(query,{'_id':0})
        return {**item,'reused':True} if item else None
    old=await cached()
    if old:
        return old
    if processing_lock.locked():
        raise HTTPException(429,'Eine Freistellung läuft gerade. Bitte in einem Moment erneut versuchen.')
    async with processing_lock:
        old=await cached()
        if old:
            return old
        if await db().studio_processed.count_documents({'guest':guest,'created_at':{'$gte':now().date().isoformat()}})>=int(os.environ['STUDIO_BG_DAILY_LIMIT']):
            raise HTTPException(429,'Das heutige Freistell-Limit ist erreicht. Zuschnitt und Ebenen funktionieren weiterhin.')
        content,_=await read_file(source,guest)
        try:
            result,(width,height)=await asyncio.to_thread(segment,content)
        except Exception as exc:
            logging.getLogger(__name__).exception('Local background removal failed')
            raise HTTPException(503,'Der Hintergrund konnte nicht entfernt werden. Dein Original bleibt erhalten. Bitte erneut versuchen oder ein anderes Motiv verwenden.') from exc
        file_id=await save_file(guest,result,'upload',extra={'source_id':source,'width':width,'height':height,'digest':hashlib.sha256(result).hexdigest(),'rights_confirmed':True,'processor':'u2netp'})
        item={'id':file_id,'original_id':source,'guest':guest,'fingerprint':fingerprint,'width':width,'height':height,'created_at':now().isoformat()}
        try:
            await db().studio_processed.insert_one(item.copy())
        except DuplicateKeyError:
            return await cached()
        return item
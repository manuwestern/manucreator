"""Bundled selection plus read-only access to faces used by older designs."""
import os
import re
from pathlib import Path
from fastapi import APIRouter,HTTPException
from fastapi.responses import Response
from .common import db
from .storage import operation
from .catalog import FONT_FILES,ASSET_DIR
from .curated_fonts import MANIFEST,path_for

router=APIRouter(prefix='/api/studio/fonts',tags=['Schriften'])
memory={}

@router.get('')
async def catalog():return MANIFEST

def public_face(item):
    return {k:item[k] for k in ['id','family','font_id','weight','style','license','version']}|{'font':'fs:'+item['id'],'url':f"/api/studio/fonts/assets/{item['id']}.woff2",'license_url':f"/api/studio/fonts/licenses/{item['id']}",'legacy':True}

async def font_record(identity):
    if not re.fullmatch(r'[a-f0-9]{32}',identity):raise HTTPException(404,'Schrift nicht gefunden.')
    row=await db().studio_font_assets.find_one({'id':identity},{'_id':0})
    if not row:raise HTTPException(422,'Die bisherige Schrift ist nicht verfügbar. Bitte bewusst eine neue Schrift wählen; es wird keine Ersatzschrift eingesetzt.')
    return row

async def font_path(key):
    if key in FONT_FILES:return ASSET_DIR/FONT_FILES[key]
    if key.startswith('curated:'):return path_for(key)
    if key in memory and memory[key].is_file():return memory[key]
    row=await font_record(key.removeprefix('fs:'))
    path=Path(os.environ['FONT_CACHE_DIR'])/(row['id']+'.ttf')
    if not path.is_file():
        data=(await operation('GET',row['paths']['ttf'])).content;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    memory[key]=path;return path

@router.get('/assets/{filename}')
async def font_asset(filename:str):
    match=re.fullmatch(r'([a-f0-9]{32})\.(woff2|ttf)',filename)
    if not match:raise HTTPException(404,'Schriftdatei nicht gefunden.')
    identity,fmt=match.groups();row=await font_record(identity);path=Path(os.environ['FONT_CACHE_DIR'])/filename
    if not path.is_file():
        response=await operation('GET',row['paths'][fmt]);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(response.content)
    return Response(path.read_bytes(),media_type='font/'+fmt,headers={'Cache-Control':'public, max-age=31536000, immutable'})

@router.get('/faces/{identity}')
async def face(identity:str):return public_face(await font_record(identity))

@router.get('/licenses/{identity}')
async def license_text(identity:str):return Response((await font_record(identity))['license_text'],media_type='text/plain')
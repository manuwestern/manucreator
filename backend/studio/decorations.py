import asyncio
import base64
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import Field
from .common import StrictModel
from .ornaments import BY_ID, ornament_sprite

router = APIRouter(prefix='/api/studio', tags=['Gravurdekorationen'])

class DecorationSpec(StrictModel):
    ornament: str = Field(max_length=40)
    w: float = Field(ge=4, le=800, allow_inf_nan=False)
    h: float = Field(ge=4, le=800, allow_inf_nan=False)
    stroke_width: float = Field(default=1.5, ge=.1, le=12, allow_inf_nan=False)

@router.get('/decorations')
async def decorations():
    return {'items': []}

@router.get('/decorations/{identity}/thumbnail')
async def thumbnail(identity: str):
    item=BY_ID.get(identity)
    if not item: raise HTTPException(404,'Dekoration nicht verfügbar.')
    data=await asyncio.to_thread(ornament_sprite,identity,180,180/item['ratio'],1.5)
    return Response(data,media_type='image/png',headers={'Cache-Control':'public, max-age=86400'})

@router.post('/decoration-preview')
async def preview(spec: DecorationSpec):
    if spec.ornament not in BY_ID: raise HTTPException(422,'Unbekannte Dekoration.')
    data=await asyncio.to_thread(ornament_sprite,spec.ornament,spec.w,spec.h,spec.stroke_width)
    return {'width':round(spec.w),'height':round(spec.h),'image':'data:image/png;base64,'+base64.b64encode(data).decode()}
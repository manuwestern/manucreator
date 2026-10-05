"""Six basic engraving shapes, independent of the decoration library."""
import asyncio
import base64
import io
import math
from functools import lru_cache
from typing import Literal
from fastapi import APIRouter,HTTPException
from pydantic import Field
from PIL import Image,ImageDraw
from .common import StrictModel

ShapeType=Literal['line','circle','rectangle','heart','triangle','star']
RATIOS={'circle':1,'heart':1.1,'triangle':2/math.sqrt(3),'star':1.0514622242382672}

def validate_shape(e):
    kind=e.get('shape_type');w=e['w'];h=e['h'];stroke=e.get('stroke_width',2)
    if kind not in {'line','circle','rectangle','heart','triangle','star'}:raise HTTPException(422,'Unbekannte Grundform.')
    if kind=='line':
        if w<4 or abs(h-stroke)>.02:raise HTTPException(422,'Linien benötigen eine gültige Länge und eine Höhe entsprechend ihrer Strichstärke.')
    elif min(w,h)<4:raise HTTPException(422,'Diese Form ist zu klein.')
    elif e.get('shape_mode','filled')=='outline' and stroke*{'circle':2,'rectangle':2,'heart':5,'triangle':4,'star':6}[kind]+(10 if kind=='circle' else 4)>=min(w,h):raise HTTPException(422,'Die Kontur ist für diese Form zu stark. Bitte die Form vergrößern oder die Strichstärke verringern.')
    if kind in RATIOS and abs(w/h/RATIOS[kind]-1)>.002:raise HTTPException(422,'Diese Grundform muss ihre Proportionen behalten.')

class ShapeSpec(StrictModel):
    shape_type:ShapeType
    shape_mode:Literal['filled','outline']='filled'
    w:float=Field(ge=.1,le=800,allow_inf_nan=False)
    h:float=Field(ge=.1,le=800,allow_inf_nan=False)
    stroke_width:float=Field(default=2,ge=.1,le=12,allow_inf_nan=False)

@lru_cache(maxsize=240)
def shape_sprite(kind,mode,width,height,stroke_width):
    density=4;w=max(1,round(width));h=max(1,round(height))
    image=Image.new('RGBA',(w*density,h*density));draw=ImageDraw.Draw(image)
    if kind=='line':
        # Butt ends. The element's height IS its stroke; changing length never changes it.
        draw.rectangle((0,0,w*density-1,h*density-1),fill='black')
    else:
        clearance=4 if kind=='circle' else 1
        pad=min((stroke_width/2 if mode=='outline' and kind not in {'circle','rectangle'} else 0)+clearance,min(w,h)/2-.5)*density
        aw,ah=w*density-pad*2,h*density-pad*2
        stroke=max(1,round(stroke_width*density))
        bounds=(pad,pad,w*density-pad-1,h*density-pad-1)
        if kind=='circle':draw.ellipse(bounds,fill='black' if mode=='filled' else None,outline='black' if mode=='outline' else None,width=stroke)
        elif kind=='rectangle':draw.rectangle(bounds,fill='black' if mode=='filled' else None,outline='black' if mode=='outline' else None,width=stroke)
        else:
            if kind=='triangle':points=[(.5,0),(1,1),(0,1)]
            elif kind=='heart':
                raw=[(16*math.sin(t)**3,-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))) for t in [i/240*math.tau for i in range(240)]]
                left=min(x for x,y in raw);top=min(y for x,y in raw);right=max(x for x,y in raw);bottom=max(y for x,y in raw)
                points=[((x-left)/(right-left),(y-top)/(bottom-top)) for x,y in raw]
            else:
                raw=[((1 if i%2==0 else .38196601125)*math.cos(-math.pi/2+i*math.pi/5),(1 if i%2==0 else .38196601125)*math.sin(-math.pi/2+i*math.pi/5)) for i in range(10)]
                left=min(x for x,y in raw);top=min(y for x,y in raw);right=max(x for x,y in raw);bottom=max(y for x,y in raw)
                points=[((x-left)/(right-left),(y-top)/(bottom-top)) for x,y in raw]
            coords=[(pad+x*(aw-1),pad+y*(ah-1)) for x,y in points]
            if mode=='filled':draw.polygon(coords,fill='black')
            else:draw.line(coords+[coords[0]],fill='black',width=stroke,joint='curve')
    image=image.resize((w,h),Image.Resampling.LANCZOS);out=io.BytesIO();image.save(out,'PNG');return out.getvalue()

router=APIRouter(prefix='/api/studio',tags=['Grundformen'])

@router.post('/shape-preview')
async def preview(spec:ShapeSpec):
    validate_shape(spec.model_dump())
    data=await asyncio.to_thread(shape_sprite,spec.shape_type,spec.shape_mode,spec.w,spec.h,spec.stroke_width)
    return {'width':max(1,round(spec.w)),'height':max(1,round(spec.h)),'image':'data:image/png;base64,'+base64.b64encode(data).decode()}
import asyncio
import base64
import io
import math
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field
from fontTools.ttLib import TTFont
from .common import StrictModel
from .fonts import font_path
from .session import guest_id

router=APIRouter(prefix='/api/studio',tags=['Textdarstellung'])

class TextSpec(StrictModel):
    text:str=Field(max_length=60)
    font:str=Field(max_length=80)
    font_size:float=Field(ge=4,le=200,allow_inf_nan=False)
    curvature:float=Field(default=0,ge=-150,le=150,allow_inf_nan=False)

@lru_cache(maxsize=80)
def characters(path):
    with TTFont(path) as font:return set((font.getBestCmap() or {}).keys())

def validate_chars(path,text):
    if any(ord(c)<32 or ord(c) not in characters(str(path)) for c in text):
        raise HTTPException(422,'Die ausgewählte Schrift enthält nicht alle eingegebenen Zeichen. Bitte Text oder Schrift anpassen.')

@lru_cache(maxsize=200)
def text_sprite(path,text,size,curve):
    # Fourfold rasterization gives identical anti-aliased glyph placement in canvas and saved PNG.
    density=4;size=max(4,float(size));font=ImageFont.truetype(path,max(4,round(size*density)))
    text=text or ' ';validate_chars(path,text)
    ascent,descent=font.getmetrics();advance=font.getlength(text)
    if advance/density>2400:
        raise HTTPException(422,'Dieser Text ist für die Arbeitsfläche zu breit. Bitte die Schriftgröße reduzieren.')
    width=max(1,math.ceil(advance));height=ascent+descent
    if abs(curve)<.01 or advance<1:
        box=font.getbbox(text,anchor='ls');left=min(0,box[0]);right=max(width,box[2])
        image=Image.new('RGBA',(max(1,right-left+8),max(1,height+8)))
        ImageDraw.Draw(image).text((4-left,4+ascent),text,font=font,fill='black',anchor='ls')
    else:
        theta=math.radians(abs(curve));radius=advance/theta;direction=1 if curve>0 else -1
        parts=[];cursor=0
        for i,char in enumerate(text):
            length=font.getlength(text[:i+1])-font.getlength(text[:i]);angle=(cursor+length/2)/radius-theta/2
            center_x=radius*math.sin(angle);center_y=direction*radius*(1-math.cos(angle))
            glyphbox=font.getbbox(char,anchor='ls');gw=max(math.ceil(length),glyphbox[2]-min(0,glyphbox[0]))+12
            glyph=Image.new('RGBA',(max(1,gw),height+12));ImageDraw.Draw(glyph).text((gw/2,6+ascent),char,font=font,fill='black',anchor='ms')
            # Tangent slope in screen coordinates; PIL rotates counter-clockwise.
            turned=glyph.rotate(-direction*math.degrees(angle),resample=Image.Resampling.BICUBIC,expand=True)
            parts.append((turned,center_x-turned.width/2,center_y-turned.height/2));cursor+=length
        xmin=math.floor(min(x for _,x,y in parts))-4;ymin=math.floor(min(y for _,x,y in parts))-4
        xmax=math.ceil(max(x+g.width for g,x,y in parts))+4;ymax=math.ceil(max(y+g.height for g,x,y in parts))+4
        image=Image.new('RGBA',(max(1,xmax-xmin),max(1,ymax-ymin)))
        for glyph,x,y in parts:image.alpha_composite(glyph,(round(x-xmin),round(y-ymin)))
    # Trim only transparent padding. The full visible glyph silhouette is retained.
    bounds=image.getbbox()
    if bounds:image=image.crop((max(0,bounds[0]-4),max(0,bounds[1]-4),min(image.width,bounds[2]+4),min(image.height,bounds[3]+4)))
    target=(max(5,math.ceil(image.width/density)),max(5,math.ceil(image.height/density)))
    image=image.resize(target,Image.Resampling.LANCZOS)
    out=io.BytesIO();image.save(out,'PNG');return out.getvalue(),target

@router.post('/text-preview')
async def preview(spec:TextSpec,guest=Depends(guest_id)):
    path=await font_path(spec.font)
    image,(w,h)=await asyncio.to_thread(text_sprite,str(path),spec.text,spec.font_size,spec.curvature)
    return {'width':w,'height':h,'image':'data:image/png;base64,'+base64.b64encode(image).decode()}
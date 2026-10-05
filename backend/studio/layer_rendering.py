import io
from PIL import Image, ImageOps, ImageDraw, ImageChops
from fastapi import HTTPException
from .transform_geometry import inside
from .ornaments import BY_ID as ORNAMENTS, ROUND, ornament_sprite
from .engraving_effects import effect_args
from .shapes import validate_shape,shape_sprite

def validate_elements(design, product, allow_placeholders=False):
    elements = design.elements
    if len({e.id for e in elements}) != len(elements):
        raise HTTPException(422,'Jede Ebene benötigt eine eindeutige Kennung.')
    if not any(not e.hidden and (e.text.strip() if e.kind=='text' else e.shape_type if e.kind=='shape' else e.ornament if e.kind=='decoration' else e.asset_id or allow_placeholders and e.placeholder) for e in elements):
        raise HTTPException(422,'Bitte mindestens eine sichtbare Text- oder Bildebene ergänzen.')
    for e in elements:
        box=e.model_dump(include={'x','y','w','h','rotation','kind','ornament','shape_type'})
        if not inside(box,product['area']):
            raise HTTPException(422,'Eine Ebene liegt außerhalb der freigegebenen Gravurfläche.')
        if e.kind=='shape':
            validate_shape(e.model_dump())
            if e.template_field:raise HTTPException(422,'Formen sind feste Gestaltungselemente, keine Kunden-Eingabefelder.')
        elif e.kind=='text':
            if 'text' not in product['templates']:raise HTTPException(422,'Text ist für diesen Artikel nicht freigegeben.')
            if len(e.text)>product['max_text']:
                raise HTTPException(422,f"Pro Textebene sind höchstens {product['max_text']} Zeichen möglich.")
            if any(not c.isprintable() for c in e.text):
                raise HTTPException(422,'Bitte eine einzelne Textzeile ohne Steuerzeichen verwenden.')
        elif e.kind=='decoration':
            if e.ornament=='custom' and e.decoration_id:pass
            elif e.ornament not in ORNAMENTS or min(e.w,e.h)<4 or e.stroke_width+2>=min(e.w,e.h):
                raise HTTPException(422,'Diese Dekoration oder Strichstärke passt nicht in die verfügbare Fläche.')
            if e.ornament in ROUND and abs(e.w-e.h)>.1:
                raise HTTPException(422,'Runde Dekorationen dürfen nicht verzerrt werden.')
        elif e.image_type not in product['templates'] or (not allow_placeholders and (e.placeholder or not e.asset_id)):
            raise HTTPException(422,'Bitte Bildplatzhalter durch ein eigenes zulässiges Foto oder Logo ersetzen.')
        if design.editor_mode=='simple' and e.template_slot:
            slot=e.template_slot
            if e.x<slot.x-.1 or e.y<slot.y-.1 or e.x+e.w>slot.x+slot.w+.1 or e.y+e.h>slot.y+slot.h+.1:
                raise HTTPException(422,'Ein Inhalt passt nicht in das feste Vorlagenfeld. Bitte kürzen oder bewusst frei bearbeiten.')

def render_layers(design, product, blank, assets, font_paths=None):
    from .rendering import fitted_font
    base=Image.open(io.BytesIO(blank)).convert('RGBA').resize((800,800))
    overlay=Image.new('RGBA',base.size); draw=ImageDraw.Draw(overlay)
    for e in design.elements:
        if e.hidden:
            continue
        stamp=Image.new('RGBA',(max(1,round(e.w)),max(1,round(e.h))))
        if e.kind=='text' and e.text:
            if e.font_size>0:
                from .text_engine import text_sprite
                data,_=text_sprite(str(font_paths[e.font]),e.text,e.font_size,e.curvature,*effect_args(e))
                text=Image.open(io.BytesIO(data)).convert('RGBA')
                s=min(1,e.w/text.width,e.h/text.height)
                if s<1:text=text.resize((max(1,round(text.width*s)),max(1,round(text.height*s))),Image.Resampling.LANCZOS)
                ink=Image.new('RGBA',text.size,product['ink']);ink.putalpha(text.getchannel('A'))
                stamp.alpha_composite(ink,((stamp.width-ink.width)//2,(stamp.height-ink.height)//2))
            else:
                font=fitted_font(e.text,e.font,max(6,int(e.h*.76)),max(1,e.w-4),minimum=6)
                ImageDraw.Draw(stamp).text((stamp.width/2,stamp.height/2),e.text,font=font,fill=product['ink'],anchor='mm')
        elif e.kind=='shape':
            motif=Image.open(io.BytesIO(shape_sprite(e.shape_type,e.shape_mode,e.w,e.h,e.stroke_width)))
            ink=Image.new('RGBA',motif.size,product['ink']);ink.putalpha(motif.getchannel('A'));stamp.alpha_composite(ink)
        elif e.kind=='decoration':
            motif=Image.open(io.BytesIO(assets['decoration:'+str(e.decoration_id)] if e.ornament=='custom' else ornament_sprite(e.ornament,e.w,e.h,e.stroke_width)))
            if e.ornament=='custom':motif=ImageOps.contain(motif,stamp.size,Image.Resampling.LANCZOS)
            ink=Image.new('RGBA',motif.size,product['ink']);ink.putalpha(motif.getchannel('A'))
            stamp.alpha_composite(ink,((stamp.width-ink.width)//2,(stamp.height-ink.height)//2))
        elif e.kind=='image':
            image=Image.open(io.BytesIO(assets[str(e.asset_id)])).convert('RGBA')
            c=e.crop; image=image.crop((c.x*image.width,c.y*image.height,(c.x+c.w)*image.width,(c.y+c.h)*image.height))
            image=ImageOps.contain(image,(max(1,round(e.w)),max(1,round(e.h))),Image.Resampling.LANCZOS)
            gray=ImageOps.invert(image.convert('RGB').convert('L')).point(lambda v: round(v*.78))
            alpha=ImageChops.multiply(gray,image.getchannel('A'))
            ink=Image.new('RGBA',image.size,product['ink']);ink.putalpha(alpha)
            stamp.alpha_composite(ink,((stamp.width-ink.width)//2,(stamp.height-ink.height)//2))
        if abs(e.rotation)>.001:
            stamp=stamp.rotate(-e.rotation,resample=Image.Resampling.BICUBIC,expand=True)
        overlay.alpha_composite(stamp,(round(e.x+e.w/2-stamp.width/2),round(e.y+e.h/2-stamp.height/2)))
    a=product['area'];mask=Image.new('L',base.size,0);draw=ImageDraw.Draw(mask)
    (draw.ellipse if a.get('shape')=='circle' else draw.rectangle)((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),fill=255)
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask));base.alpha_composite(overlay)
    out=io.BytesIO();base.convert('RGB').save(out,'PNG');return out.getvalue()
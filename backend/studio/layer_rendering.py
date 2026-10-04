import io
from PIL import Image, ImageOps, ImageDraw, ImageChops
from fastapi import HTTPException
from .geometry import constrain

def validate_elements(design, product):
    elements = design.elements
    if len({e.id for e in elements}) != len(elements):
        raise HTTPException(422,'Jede Ebene benötigt eine eindeutige Kennung.')
    if not any(not e.hidden and (e.text.strip() if e.kind=='text' else e.asset_id) for e in elements):
        raise HTTPException(422,'Bitte mindestens eine sichtbare Text- oder Bildebene ergänzen.')
    for e in elements:
        box=e.model_dump(include={'x','y','w','h'}); bounded=constrain(box,product['area'])
        if any(abs(box[k]-bounded[k])>.1 for k in box):
            raise HTTPException(422,'Eine Ebene liegt außerhalb der freigegebenen Gravurfläche.')
        if e.kind=='text':
            if len(e.text)>product['max_text']:
                raise HTTPException(422,f"Pro Textebene sind höchstens {product['max_text']} Zeichen möglich.")
            if any(not (32<=ord(c)<=591 or c in '–—„“’') for c in e.text):
                raise HTTPException(422,'Bitte lateinische Buchstaben und Satzzeichen ohne Emojis oder Zeilenumbrüche verwenden.')
        elif not e.asset_id or e.image_type not in product['templates']:
            raise HTTPException(422,'Für diese Bildebene fehlt ein zulässiges Foto oder Logo.')

def render_layers(design, product, blank, assets):
    from .rendering import fitted_font
    base=Image.open(io.BytesIO(blank)).convert('RGBA').resize((800,800))
    overlay=Image.new('RGBA',base.size); draw=ImageDraw.Draw(overlay)
    for e in design.elements:
        if e.hidden:
            continue
        if e.kind=='text' and e.text:
            font=fitted_font(e.text,e.font,max(6,int(e.h*.76)),max(1,e.w-4),minimum=6)
            # Draw on a separate layer so lower content is composited, not erased.
            layer=Image.new('RGBA',base.size)
            ImageDraw.Draw(layer).text((e.x+e.w/2,e.y+e.h/2),e.text,font=font,fill=product['ink'],anchor='mm')
            overlay.alpha_composite(layer)
        elif e.kind=='image':
            image=Image.open(io.BytesIO(assets[str(e.asset_id)])).convert('RGBA')
            c=e.crop; image=image.crop((c.x*image.width,c.y*image.height,(c.x+c.w)*image.width,(c.y+c.h)*image.height))
            image=image.resize((max(1,round(e.w)),max(1,round(e.h))),Image.Resampling.LANCZOS)
            gray=ImageOps.invert(image.convert('RGB').convert('L')).point(lambda v: round(v*.78))
            alpha=ImageChops.multiply(gray,image.getchannel('A'))
            stamp=Image.new('RGBA',image.size,product['ink']);stamp.putalpha(alpha)
            overlay.alpha_composite(stamp,(round(e.x),round(e.y)))
    a=product['area'];mask=Image.new('L',base.size,0);draw=ImageDraw.Draw(mask)
    (draw.ellipse if a.get('shape')=='circle' else draw.rectangle)((a['x'],a['y'],a['x']+a['w'],a['y']+a['h']),fill=255)
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask));base.alpha_composite(overlay)
    out=io.BytesIO();base.convert('RGB').save(out,'PNG');return out.getvalue()
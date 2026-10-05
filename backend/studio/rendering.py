import io
import warnings
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageChops, UnidentifiedImageError
from fastapi import HTTPException
from .catalog import ASSET_DIR, FONT_FILES
from .geometry import default_layout
from .engraving_mask import engraving_mask

Image.MAX_IMAGE_PIXELS = 20000000

def clean_upload(content):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(content))
            if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                raise ValueError()
            image.load()
            image = ImageOps.exif_transpose(image).convert('RGBA')
            if min(image.size) < 100:
                raise HTTPException(422, 'Das Bild ist zu klein. Bitte mindestens 100 × 100 Pixel hochladen.')
            original_size = image.size
            image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.save(output, 'PNG')
            return output.getvalue(), original_size
    except HTTPException:
        raise
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        raise HTTPException(422, 'Bitte ein gültiges JPG-, PNG- oder WebP-Bild mit höchstens 20 Megapixeln verwenden.') from exc

def validate_design(design, product):
    if design.template not in product['templates']:
        raise HTTPException(422, 'Diese Vorlage ist für den gewählten Rohling nicht vorgesehen.')
    if len(design.text) > product['max_text']:
        raise HTTPException(422, f"Für diesen Rohling sind höchstens {product['max_text']} Zeichen im Haupttext möglich.")
    if design.template == 'text' and not design.text:
        raise HTTPException(422, 'Bitte einen Haupttext ergänzen.')
    if design.template != 'text' and not design.asset_id:
        raise HTTPException(422, 'Bitte zuerst ein eigenes Foto oder Logo hochladen.')
    for character in design.text + design.subtitle:
        if not (32 <= ord(character) <= 591 or character in '–—„“’'):
            raise HTTPException(422, 'Bitte lateinische Buchstaben, Ziffern und Satzzeichen verwenden – keine Emojis oder Zeilenumbrüche.')
    return product

def fitted_font(text, family, size, max_width, minimum=14):
    while size >= minimum:
        font = ImageFont.truetype(str(ASSET_DIR / FONT_FILES[family]), size)
        if font.getlength(text) <= max_width:
            return font
        size -= 1
    raise HTTPException(422, 'Der Text ist für diese Fläche zu lang. Bitte kürzen.')

def render_design(design, asset_bytes, product, blank):
    validate_design(design, product)
    base = Image.open(io.BytesIO(blank)).convert('RGBA').resize((800, 800))
    if design.layout:
        return render_free(design, product, base, asset_bytes)
    overlay = Image.new('RGBA', base.size)
    draw = ImageDraw.Draw(overlay)
    area = product['area']; x, y, w, h = [area[k] for k in ('x', 'y', 'w', 'h')]
    offset = {'top': -12, 'center': 0, 'bottom': 12}[design.position]
    center_x = x + w / 2
    size = {'small': 26, 'medium': 32, 'large': 38}[design.size]
    if design.template != 'text':
        image = Image.open(io.BytesIO(asset_bytes)).convert('RGBA')
        flat = Image.new('RGBA', image.size, 'white'); flat.alpha_composite(image)
        side = int(min(w * .68, h * .52, h - 112))
        source = min(flat.size) / design.zoom
        cx = flat.width / 2 + (flat.width - source) * design.focal_x / 60
        cy = flat.height / 2 + (flat.height - source) * design.focal_y / 60
        crop = flat.crop((int(cx-source/2), int(cy-source/2), int(cx+source/2), int(cy+source/2))).convert('L').resize((side, side), Image.Resampling.LANCZOS)
        alpha = ImageOps.invert(crop).point(lambda v: round(v * .78))
        stamp = Image.new('RGBA', (side, side), product['ink']); stamp.putalpha(alpha)
        overlay.alpha_composite(stamp, (int(center_x-side/2), int(y+20+offset)))
        text_y = y + 20 + side + 30 + offset
    else:
        text_y = y + h / 2 - 13 + offset
    font = fitted_font(design.text, design.font, size, w - 24)
    sub_font = fitted_font(design.subtitle, 'modern', 17, w - 24, 12)
    draw.text((center_x, text_y), design.text, font=font, fill=product['ink'], anchor='mm')
    if design.subtitle:
        draw.text((center_x, text_y + 34), design.subtitle, font=sub_font, fill=product['ink'], anchor='mm')
    mask = engraving_mask(product, base.size)
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'), mask))
    base.alpha_composite(overlay)
    output = io.BytesIO(); base.convert('RGB').save(output, 'PNG')
    return output.getvalue()

def render_free(design, product, base, asset_bytes):
    overlay = Image.new('RGBA', base.size)
    boxes = design.layout.model_dump() if design.layout else default_layout(design, product)
    draw = ImageDraw.Draw(overlay)
    for key, text, family in [('text', design.text, design.font), ('subtitle', design.subtitle, 'modern')]:
        if not text:
            continue
        b = boxes[key]
        font = fitted_font(text, family, max(6, int(b['h']*.76)), max(1,b['w']-4), minimum=6)
        draw.text((b['x']+b['w']/2, b['y']+b['h']/2), text, font=font, fill=product['ink'], anchor='mm')
    if design.template != 'text' and asset_bytes:
        b = boxes['image']
        image = Image.open(io.BytesIO(asset_bytes)).convert('RGBA')
        flat = Image.new('RGBA', image.size, 'white'); flat.alpha_composite(image)
        ratio = b['w']/b['h']; width = min(flat.width, flat.height*ratio)/design.zoom; height = width/ratio
        cx = flat.width/2 + (flat.width-width)*design.focal_x/60
        cy = flat.height/2 + (flat.height-height)*design.focal_y/60
        image = flat.crop((cx-width/2,cy-height/2,cx+width/2,cy+height/2)).convert('L').resize((max(1,round(b['w'])),max(1,round(b['h']))),Image.Resampling.LANCZOS)
        stamp = Image.new('RGBA', image.size, product['ink'])
        stamp.putalpha(ImageOps.invert(image).point(lambda v: round(v*.78)))
        overlay.alpha_composite(stamp,(round(b['x']),round(b['y'])))
    mask = engraving_mask(product, base.size)
    overlay.putalpha(ImageChops.multiply(overlay.getchannel('A'),mask))
    base.alpha_composite(overlay)
    output=io.BytesIO();base.convert('RGB').save(output,'PNG');return output.getvalue()
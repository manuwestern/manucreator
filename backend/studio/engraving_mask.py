"""Non-destructive product mask; exclusions are a union, never an XOR."""
from PIL import Image, ImageDraw


def engraving_mask(product, size=(800, 800)):
    density = 4
    mask = Image.new('L', (size[0]*density, size[1]*density), 0)
    draw = ImageDraw.Draw(mask)

    def region(zone, fill):
        x, y, w, h = (zone[key]*density for key in ('x', 'y', 'w', 'h'))
        bounds = (x, y, x+w-1, y+h-1)
        (draw.ellipse if zone.get('shape') == 'circle' else draw.rectangle)(bounds, fill=fill)

    region(product['area'], 255)
    for zone in product.get('exclusions', []):
        region(zone, 0)
    # BOX prevents ringing / engraving pixels bleeding into fully excluded pixels.
    return mask.resize(size, Image.Resampling.BOX)
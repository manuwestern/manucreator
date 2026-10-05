"""Monochrome engraving masks; no blur, lighting or external service."""
import math
from PIL import Image, ImageChops, ImageFilter
from pydantic import Field
from typing import Literal
from .common import StrictModel


class TextEffects(StrictModel):
    text_mode: Literal['filled', 'outline'] = 'filled'
    outline_width: float = Field(default=1, ge=.1, le=12, allow_inf_nan=False)
    shadow_enabled: bool = False
    shadow_distance: float = Field(default=3, ge=0, le=40, allow_inf_nan=False)
    shadow_angle: float = Field(default=45, ge=-180, le=180, allow_inf_nan=False)


def effect_args(element):
    return (element.text_mode, element.outline_width, element.shadow_enabled,
            element.shadow_distance, element.shadow_angle)


def apply_effects(image, density, mode, width, shadow, distance, angle):
    if mode == 'filled' and not shadow:
        return image
    radius = max(1, round(width * density / 2)) if mode == 'outline' else 0
    dx = round(math.cos(math.radians(angle)) * distance * density) if shadow else 0
    dy = round(math.sin(math.radians(angle)) * distance * density) if shadow else 0
    pad = radius + 2 * density
    x, y = pad + max(0, -dx), pad + max(0, -dy)
    size = (image.width + 2 * pad + abs(dx), image.height + 2 * pad + abs(dy))
    mask = Image.new('L', size)
    mask.paste(image.getchannel('A'), (x, y))
    front = mask
    if mode == 'outline':
        front = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(radius * 2 + 1)),
                                    mask.filter(ImageFilter.MinFilter(radius * 2 + 1)))
    if shadow:
        back = Image.new('L', size)
        back.paste(image.getchannel('A'), (x + dx, y + dy))
        front = ImageChops.lighter(front, back)
    result = Image.new('RGBA', size, 'black')
    result.putalpha(front)
    return result
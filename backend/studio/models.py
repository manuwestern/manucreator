from typing import Literal
from uuid import UUID
from pydantic import EmailStr, Field, model_validator
from .common import StrictModel
from .engraving_effects import TextEffects

class Box(StrictModel):
    x: float = Field(ge=-800, le=800, allow_inf_nan=False)
    y: float = Field(ge=-800, le=800, allow_inf_nan=False)
    w: float = Field(ge=.1, le=800, allow_inf_nan=False)
    h: float = Field(ge=.1, le=800, allow_inf_nan=False)

class Layout(StrictModel):
    text: Box
    subtitle: Box
    image: Box

class Exclusion(StrictModel):
    id: str = Field(min_length=1, max_length=60, pattern=r'^[a-zA-Z0-9_-]+$')
    shape: Literal['rect', 'circle'] = 'rect'
    x: float = Field(ge=0, le=798, allow_inf_nan=False)
    y: float = Field(ge=0, le=798, allow_inf_nan=False)
    w: float = Field(ge=2, le=800, allow_inf_nan=False)
    h: float = Field(ge=2, le=800, allow_inf_nan=False)

    @model_validator(mode='after')
    def valid_exclusion(self):
        if self.x + self.w > 800.01 or self.y + self.h > 800.01:
            raise ValueError('Die Aussparung muss vollständig im Produktfoto liegen.')
        if self.shape == 'circle' and abs(self.w-self.h) > .1:
            raise ValueError('Eine runde Aussparung benötigt gleiche Seiten.')
        return self

class Crop(StrictModel):
    x: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)
    y: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)
    w: float = Field(default=1, gt=0.001, le=1, allow_inf_nan=False)
    h: float = Field(default=1, gt=0.001, le=1, allow_inf_nan=False)

    @model_validator(mode='after')
    def inside_image(self):
        if self.x + self.w > 1.00001 or self.y + self.h > 1.00001:
            raise ValueError('Der Zuschnitt muss im Bild liegen.')
        return self

Font = Literal['modern','classic','bold','sans','sans-bold','sans-italic','serif','serif-italic','mono','narrow']

class Element(Box, TextEffects):
    id: str = Field(min_length=1, max_length=60, pattern=r'^[a-zA-Z0-9_-]+$')
    kind: Literal['text','image','decoration','shape']
    shape_type: Literal['line','circle','rectangle','heart','triangle','star'] | None = None
    shape_mode: Literal['filled','outline'] = 'filled'
    shape_proportional: bool = True
    ornament: str | None = Field(default=None,max_length=40)
    stroke_width: float = Field(default=1.5,ge=.1,le=12,allow_inf_nan=False)
    decoration_id: UUID | None = None
    field_required: bool = False
    field_max_length: int | None = Field(default=None,ge=1,le=60)
    text: str = Field(default='',max_length=60)
    font: str = Field(default='sans',max_length=80,pattern=r'^(modern|classic|bold|sans|sans-bold|sans-italic|serif|serif-italic|mono|narrow|fs:[a-f0-9]{32}|curated:[a-z0-9-]+:[1-9][0-9]{2}:normal|curated:[a-z0-9-]+:[1-9][0-9]{2}:italic)$')
    font_size: float = Field(default=0,ge=0,le=200,allow_inf_nan=False)
    rotation: float = Field(default=0,ge=-360,le=360,allow_inf_nan=False)
    curvature: float = Field(default=0,ge=-150,le=150,allow_inf_nan=False)
    asset_id: UUID | None = None
    original_asset_id: UUID | None = None
    image_type: Literal['photo','logo'] = 'photo'
    image_ratio: float = Field(default=0,ge=0,le=10000,allow_inf_nan=False)
    crop: Crop = Field(default_factory=Crop)
    locked: bool = False
    hidden: bool = False
    placeholder: bool = False
    template_field: str | None = Field(default=None,max_length=40)
    field_label: str | None = Field(default=None,max_length=60)
    template_slot: Box | None = None

class Design(StrictModel):
    product_id: str = Field(min_length=2, max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    template: Literal['text', 'photo', 'logo'] = 'text'
    text: str = Field(default='', max_length=60)
    subtitle: str = Field(default='', max_length=36)
    font: Literal['modern', 'classic', 'bold'] = 'classic'
    size: Literal['small', 'medium', 'large'] = 'medium'
    position: Literal['top', 'center', 'bottom'] = 'center'
    asset_id: UUID | None = None
    zoom: float = Field(default=1, ge=1, le=1.6)
    focal_x: float = Field(default=0, ge=-30, le=30)
    focal_y: float = Field(default=0, ge=-30, le=30)
    layout: Layout | None = None
    elements: list[Element] | None = Field(default=None, max_length=12)
    editor_mode: Literal['free','simple'] = 'free'
    template_id: str | None = Field(default=None,max_length=40)
    template_version: int | None = Field(default=None,ge=1)
    template_revision_id: UUID | None = None
    allow_free_edit: bool = True
    font_catalog_version: str = Field(default='manucreator-curated-1',max_length=50)

class CartAdd(StrictModel):
    draft_id: str = Field(min_length=32, max_length=80)
    quantity: int = Field(default=1, ge=1, le=20)

class Quantity(StrictModel):
    quantity: int = Field(ge=1, le=20)

class AIRequest(StrictModel):
    confirmed: Literal[True]

class TestOrder(StrictModel):
    request_id: UUID
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=254)
    note: str = Field(default='', max_length=500)
    acknowledge_test: Literal[True]
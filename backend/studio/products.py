import asyncio
import io
import uuid
from typing import Literal
from PIL import Image, ImageOps
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .admin_auth import current_admin
from .common import StrictModel, db, now
from .catalog import PRODUCTS, ASSET_DIR
from .storage import save_file, read_file

class Area(StrictModel):
    x: float = Field(ge=0, le=780, allow_inf_nan=False)
    y: float = Field(ge=0, le=780, allow_inf_nan=False)
    w: float = Field(ge=30, le=800, allow_inf_nan=False)
    h: float = Field(ge=30, le=800, allow_inf_nan=False)
    shape: Literal['rect', 'circle'] = 'rect'

    @model_validator(mode='after')
    def valid_area(self):
        if self.x + self.w > 800.01 or self.y + self.h > 800.01 or (self.shape == 'circle' and abs(self.w-self.h) > .1):
            raise ValueError('Die Gravurfläche muss vollständig im Foto liegen; ein Kreis braucht gleiche Seiten.')
        return self

class ProductInput(StrictModel):
    name: str = Field(min_length=2, max_length=80)
    subtitle: str = Field(default='', max_length=160)
    material: str = Field(min_length=2, max_length=50)
    category: Literal['holz', 'glas', 'metall', 'kunststoff', 'schiefer', 'textil']
    price_cents: int = Field(ge=0, le=1000000)
    dimensions: str = Field(min_length=2, max_length=80)
    area_mm: str = Field(min_length=2, max_length=80)
    max_text: int = Field(ge=1, le=60)
    area: Area
    ink: str = Field(pattern=r'^#[0-9a-fA-F]{6}$')
    templates: list[Literal['text', 'photo', 'logo']] = Field(min_length=1, max_length=3)
    image_file_id: str | None = None
    active: bool = True
    is_sample: bool = True
    version: int = Field(default=1, ge=1)

class ProductResponse(ProductInput):
    model_config = ConfigDict(extra='ignore')
    id: str
    image: str
    production_approved: Literal[False] = False

class CatalogResponse(BaseModel):
    products: list[ProductResponse]
    mode: Literal['test'] = 'test'
    production_approved: Literal[False] = False

async def initialize_products():
    await db().studio_products.create_index('id', unique=True)
    for item in PRODUCTS:
        seed = {**item, 'area': {**item['area'], 'shape': 'rect'}, 'image': f"/images/studio/{item['id']}.webp", 'image_file_id': None, 'active': True, 'is_sample': True, 'production_approved': False, 'version': 1}
        await db().studio_products.update_one({'id': item['id']}, {'$setOnInsert': seed}, upsert=True)

async def get_product(identity, active=True):
    query = {'id': identity}
    if active:
        query['active'] = True
    product = await db().studio_products.find_one(query, {'_id': 0})
    if not product:
        raise HTTPException(404, 'Dieser Rohling ist nicht mehr verfügbar. Bitte wähle einen anderen.')
    return product

async def blank_bytes(product):
    if product.get('image_file_id'):
        return (await read_file(product['image_file_id'], 'product-catalog'))[0]
    return (ASSET_DIR / f"{product['id']}.png").read_bytes()

router = APIRouter(prefix='/api/admin/products', tags=['Rohlinge'], dependencies=[Depends(current_admin)])
public_router = APIRouter(prefix='/api/studio')

@router.get('', response_model=list[ProductResponse])
async def list_products():
    return await db().studio_products.find({}, {'_id': 0}).to_list(500)

def normalize_photo(content):
    from .rendering import clean_upload
    cleaned, _ = clean_upload(content)
    image = Image.open(io.BytesIO(cleaned)).convert('RGBA')
    image = ImageOps.contain(image, (800, 800), Image.Resampling.LANCZOS)
    base = Image.new('RGBA', (800, 800), '#f5f6f2')
    base.alpha_composite(image, ((800-image.width)//2, (800-image.height)//2))
    out = io.BytesIO(); base.convert('RGB').save(out, 'PNG')
    return out.getvalue()

@router.post('/photo', status_code=201)
async def upload_photo(file: UploadFile = File(...)):
    content = await file.read(8*1024*1024+1)
    if len(content) > 8*1024*1024:
        raise HTTPException(413, 'Das Foto darf höchstens 8 MB groß sein.')
    image = await asyncio.to_thread(normalize_photo, content)
    identity = await save_file('product-catalog', image, 'product_blank')
    return {'id': identity, 'image': f'/api/studio/product-images/{identity}'}

@public_router.get('/product-images/{identity}')
async def product_image(identity: str):
    record = await db().studio_files.find_one({'id': identity, 'guest': 'product-catalog', 'kind': 'product_blank', 'is_deleted': False}, {'_id': 0})
    if not record:
        raise HTTPException(404, 'Produktfoto nicht verfügbar.')
    content, record = await read_file(identity, 'product-catalog')
    return Response(content=content, media_type=record['mime'], headers={'Cache-Control': 'public, max-age=86400', 'X-Content-Type-Options': 'nosniff'})

async def checked_values(payload, old=None):
    values = payload.model_dump()
    if payload.image_file_id:
        record = await db().studio_files.find_one({'id': payload.image_file_id, 'guest': 'product-catalog', 'kind': 'product_blank', 'is_deleted': False}, {'_id': 0})
        if not record:
            raise HTTPException(422, 'Bitte ein gültiges Rohlingfoto hochladen.')
        values['image'] = f'/api/studio/product-images/{payload.image_file_id}'
    elif old and not old.get('image_file_id'):
        values['image'] = old['image']
    else:
        raise HTTPException(422, 'Bitte zuerst ein Rohlingfoto hochladen.')
    return {**values, 'production_approved': False, 'updated_at': now().isoformat()}

@router.post('', response_model=ProductResponse, status_code=201)
async def create_product(payload: ProductInput):
    item = {**await checked_values(payload), 'id': str(uuid.uuid4()), 'version': 1}
    await db().studio_products.insert_one(item.copy())
    return item

@router.put('/{identity}', response_model=ProductResponse)
async def edit_product(identity: str, payload: ProductInput):
    old = await get_product(identity, active=False)
    item = {**await checked_values(payload, old), 'version': old['version']+1}
    result = await db().studio_products.update_one({'id': identity, 'version': payload.version}, {'$set': item})
    if not result.modified_count:
        raise HTTPException(409, 'Der Rohling wurde zwischenzeitlich geändert. Bitte neu öffnen.')
    return {**old, **item}

@router.delete('/{identity}', response_model=ProductResponse)
async def archive_product(identity: str):
    await get_product(identity, active=False)
    await db().studio_products.update_one({'id': identity}, {'$set': {'active': False}, '$inc': {'version': 1}})
    return await get_product(identity, active=False)
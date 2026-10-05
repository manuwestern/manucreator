import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'], serverSelectionTimeoutMS=5000)
db = client[os.environ['DB_NAME']]
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.inquiries.create_index('id', unique=True)
    from studio.setup import initialize
    await initialize(db)
    yield
    client.close()


app = FastAPI(title='ManuCreator', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ['CORS_ORIGINS'].split(','),
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allow_headers=['Content-Type', 'Authorization'],
)


class InquiryCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    request_id: UUID
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr = Field(max_length=254)
    material: Literal['holz', 'kunststoff', 'glas', 'metall', 'schiefer', 'textil', 'offen']
    quantity: int = Field(ge=1, le=100000)
    message: str = Field(min_length=10, max_length=5000)
    # Kept only for old clients; precontractual inquiry handling does not require
    # an additional consent. Do not store it as a new consent record.
    consent: bool | None = Field(default=None, exclude=True)
    website: str = Field(default='', max_length=0)


class InquiryReceipt(BaseModel):
    id: str
    message: str


@app.get('/api/health')
async def health():
    try:
        await db.command('ping')
    except PyMongoError:
        raise HTTPException(503, 'Der Dienst ist vorübergehend nicht erreichbar.')
    return {'status': 'ok'}


@app.post('/api/inquiries', response_model=InquiryReceipt, status_code=201)
async def create_inquiry(inquiry: InquiryCreate):
    inquiry_id = str(inquiry.request_id)
    document = inquiry.model_dump(exclude={'request_id', 'website'})
    document.update(id=inquiry_id, created_at=datetime.now(timezone.utc).isoformat(), status='new', privacy_notice_version='2026-10-04')
    try:
        await db.inquiries.insert_one(document)
    except DuplicateKeyError:
        # A repeated submission returns the same receipt, never duplicate customer data.
        pass
    except PyMongoError:
        logger.exception('Inquiry could not be saved')
        raise HTTPException(503, 'Deine Anfrage konnte nicht gespeichert werden. Bitte versuche es noch einmal.')
    # Never expose the MongoDB document or customer data through a public read endpoint.
    return InquiryReceipt(id=inquiry_id, message='Deine Anfrage wurde erfolgreich gespeichert.')

from studio.router import router as studio_router
from studio.cart import router as studio_cart_router
app.include_router(studio_router)
app.include_router(studio_cart_router)
from studio.admin_auth import router as admin_auth_router
from studio.products import router as products_router, public_router as product_images_router
app.include_router(admin_auth_router)
app.include_router(products_router)
app.include_router(product_images_router)
from studio.background import router as background_router
app.include_router(background_router)
from studio.fonts import router as font_router
from studio.text_engine import router as text_router
app.include_router(font_router)
app.include_router(text_router)
from studio.decorations import router as decorations_router
app.include_router(decorations_router)
from studio.decoration_library import router as decoration_library_router,public as decoration_assets_router
app.include_router(decoration_library_router)
app.include_router(decoration_assets_router)
from studio.article_templates import router as article_templates_router,public as article_templates_public
app.include_router(article_templates_router)
app.include_router(article_templates_public)
from studio.shapes import router as shapes_router
app.include_router(shapes_router)
from studio.templates import router as templates_router
app.include_router(templates_router)
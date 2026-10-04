from typing import Literal
from pydantic import BaseModel
from .models import Design

class DraftResponse(BaseModel):
    id: str
    guest: str
    design: Design
    fingerprint: str
    render_id: str
    ai_status: Literal['none', 'generating', 'ready', 'failed']
    ai_attempts: int
    is_sample: bool
    product_snapshot: dict | None = None
    production_approved: Literal[False]
    created_at: str
    ai_file_id: str | None = None
    ai_started: str | None = None
    ai_finished: str | None = None
    ai_requested_at: str | None = None
    ai_notice_version: str | None = None
    ai_error: str | None = None
    reused: bool = False

class CartItemResponse(BaseModel):
    id: str
    guest: str
    draft_id: str
    quantity: int
    created_at: str
    draft: DraftResponse
    product_name: str
    price_cents: int
    subtotal_cents: int

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_cents: int
    count: int
    mode: Literal['test']
    payable_cents: Literal[0]

class CustomerResponse(BaseModel):
    name: str
    email: str
    note: str

class OrderResponse(BaseModel):
    id: str
    reference: str
    guest: str
    request_id: str
    customer: CustomerResponse
    items: list[CartItemResponse]
    example_total_cents: int
    payable_cents: Literal[0]
    status: Literal['test_saved']
    is_test: Literal[True]
    production_approved: Literal[False]
    created_at: str
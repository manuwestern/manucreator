import uuid
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from .session import guest_id
from .common import db, now, owned
from .products import get_product
from .models import CartAdd, Quantity, TestOrder
from .responses import CartResponse, OrderResponse

router = APIRouter(prefix='/api/studio', tags=['Test-Warenkorb'])

async def contents(guest):
    items = await db().studio_cart.find({'guest': guest, 'quantity': {'$gt': 0}}, {'_id': 0}).sort('created_at', 1).to_list(30)
    result = []
    for item in items:
        draft = await owned('studio_drafts', item['draft_id'], guest)
        product = draft.get('product_snapshot') or await get_product(draft['design']['product_id'], active=False)
        result.append({**item, 'draft': draft, 'product_name': product['name'], 'price_cents': product['price_cents'], 'subtotal_cents': product['price_cents'] * item['quantity']})
    return {'items': result, 'total_cents': sum(i['subtotal_cents'] for i in result), 'count': sum(i['quantity'] for i in result), 'mode': 'test', 'payable_cents': 0}

@router.get('/cart', response_model=CartResponse)
async def cart(guest=Depends(guest_id)):
    return await contents(guest)

@router.post('/cart', response_model=CartResponse)
async def add(payload: CartAdd, guest=Depends(guest_id)):
    draft = await owned('studio_drafts', payload.draft_id, guest)
    await check_available(draft)
    if await db().studio_cart.count_documents({'guest': guest, 'quantity': {'$gt': 0}}) >= 15:
        raise HTTPException(422, 'Der Muster-Warenkorb ist auf 15 Entwürfe begrenzt.')
    await db().studio_cart.update_one({'guest': guest, 'draft_id': payload.draft_id}, {'$set': {'quantity': payload.quantity}, '$setOnInsert': {'id': str(uuid.uuid4()), 'guest': guest, 'draft_id': payload.draft_id, 'created_at': now().isoformat()}}, upsert=True)
    return await contents(guest)

@router.patch('/cart/{identity}', response_model=CartResponse)
async def quantity(identity: str, payload: Quantity, guest=Depends(guest_id)):
    await owned('studio_cart', identity, guest)
    await db().studio_cart.update_one({'id': identity, 'guest': guest}, {'$set': {'quantity': payload.quantity}})
    return await contents(guest)

@router.delete('/cart/{identity}', response_model=CartResponse)
async def remove(identity: str, guest=Depends(guest_id)):
    await db().studio_cart.delete_one({'id': identity, 'guest': guest})
    return await contents(guest)

@router.post('/orders', status_code=201, response_model=OrderResponse)
async def test_order(payload: TestOrder, guest=Depends(guest_id)):
    old = await db().studio_orders.find_one({'guest': guest, 'request_id': str(payload.request_id)}, {'_id': 0})
    if old:
        return old
    current = await contents(guest)
    if not current['items']:
        raise HTTPException(422, 'Dein Test-Warenkorb ist leer.')
    for item in current['items']:
        await check_available(item['draft'])
    order = {'id': str(uuid.uuid4()), 'reference': 'TEST-' + uuid.uuid4().hex[:8].upper(), 'guest': guest, 'request_id': str(payload.request_id), 'customer': {'name': payload.name, 'email': str(payload.email), 'note': payload.note}, 'items': current['items'], 'example_total_cents': current['total_cents'], 'payable_cents': 0, 'status': 'test_saved', 'is_test': True, 'production_approved': False, 'created_at': now().isoformat()}
    try:
        await db().studio_orders.insert_one(order.copy())
    except DuplicateKeyError:
        return await db().studio_orders.find_one({'guest': guest, 'request_id': str(payload.request_id)}, {'_id': 0})
    # Snapshot quantities are immutable in the order; only clear items included.
    for item in current['items']:
        await db().studio_cart.delete_one({'id': item['id'], 'guest': guest, 'quantity': item['quantity']})
    return order

@router.get('/orders/{identity}', response_model=OrderResponse)
async def order_detail(identity: str, guest=Depends(guest_id)):
    return await owned('studio_orders', identity, guest)

async def check_available(draft):
    current = await get_product(draft['design']['product_id'])
    snapshot = draft.get('product_snapshot')
    if snapshot and snapshot['version'] != current['version']:
        raise HTTPException(409, 'Der Rohling wurde geändert. Bitte den Entwurf im Studio erneut prüfen und speichern.')
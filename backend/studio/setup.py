import logging
from . import common
from .storage import init_storage

async def initialize(database):
    common.database = database
    from .admin_auth import seed_admin
    from .products import initialize_products
    await seed_admin()
    await initialize_products()
    await database.studio_processed.create_index([('guest',1),('fingerprint',1)],unique=True)
    for collection in ['studio_guests', 'studio_files', 'studio_drafts', 'studio_cart', 'studio_orders', 'studio_chats']:
        await database[collection].create_index('id', unique=True)
    await database.studio_guests.create_index('expires_at', expireAfterSeconds=0)
    await database.studio_guest_counters.create_index('expires_at', expireAfterSeconds=0)
    await database.studio_quotas.create_index('expires_at', expireAfterSeconds=0)
    await database.studio_drafts.create_index([('guest', 1), ('fingerprint', 1)], unique=True)
    await database.studio_cart.create_index([('guest', 1), ('draft_id', 1)], unique=True)
    await database.studio_orders.create_index([('guest', 1), ('request_id', 1)], unique=True)
    try:
        await init_storage()
    except Exception:
        logging.getLogger(__name__).warning('Studio storage unavailable at startup; operations will retry initialization.')
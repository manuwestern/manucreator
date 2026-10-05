import asyncio
import logging
import os
import uuid
import httpx
from fastapi import HTTPException
from .common import db, now, owned

STORAGE_BASE = os.environ['INTEGRATION_PROXY_URL'].strip()
STORAGE_URL = STORAGE_BASE.rstrip('/') + '/objstore/api/v1/storage'
storage_key = None
lock = asyncio.Lock()
_client = None
logger = logging.getLogger(__name__)

def storage_client():
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=100, limits=httpx.Limits(max_connections=12, max_keepalive_connections=6))
    return _client

async def close_storage():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

def log_failure(action, exc):
    # No object paths, credentials, customer IDs, URLs or response bodies in logs.
    response = getattr(exc, 'response', None)
    logger.warning('Storage %s failed: kind=%s upstream_status=%s', action, type(exc).__name__, response.status_code if response is not None else 'none')

async def init_storage(force=False):
    global storage_key
    async with lock:
        if storage_key and not force:
            return storage_key
        response = await storage_client().post(f'{STORAGE_URL}/init', json={'emergent_key': os.environ['EMERGENT_LLM_KEY']}, timeout=40)
        response.raise_for_status()
        storage_key = response.json()['storage_key']
        return storage_key

async def operation(method, path, data=None, content_type=None):
    for attempt in range(2):
        key = await init_storage(force=bool(attempt))
        headers = {'X-Storage-Key': key}
        if content_type:
            headers['Content-Type'] = content_type
        response = await storage_client().request(method, f'{STORAGE_URL}/objects/{path}', headers=headers, content=data)
        if response.status_code == 404 and attempt == 0:
            continue
        response.raise_for_status()
        return response

async def save_file(guest, content, kind, mime='image/png', extra=None):
    identity = str(uuid.uuid4())
    suffix = {'image/png':'png','image/webp':'webp','image/svg+xml':'svg'}.get(mime,'bin')
    path = f"{os.environ['STUDIO_APP_PREFIX']}/uploads/{guest}/{identity}.{suffix}"
    try:
        response = await operation('PUT', path, content, mime)
    except httpx.HTTPError as exc:
        log_failure('write', exc)
        raise HTTPException(503, 'Die Bildspeicherung ist gerade nicht verfügbar. Bitte erneut versuchen.') from exc
    record = {'id': identity, 'guest': guest, 'storage_path': response.json()['path'], 'mime': mime, 'size': len(content), 'kind': kind, 'is_deleted': False, 'created_at': now().isoformat(), **(extra or {})}
    await db().studio_files.insert_one(record.copy())
    return identity

async def read_file(identity, guest):
    record = await owned('studio_files', identity, guest)
    try:
        response = await operation('GET', record['storage_path'])
    except httpx.HTTPError as exc:
        log_failure('read', exc)
        raise HTTPException(503, 'Das Bild konnte gerade nicht geladen werden.') from exc
    return response.content, record
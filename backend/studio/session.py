import hashlib
import hmac
import os
import secrets
from datetime import timedelta
import jwt
from fastapi import Header, HTTPException, Request
from pydantic import Field
from .common import StrictModel, db, now
from .guest_limiter import reserve_guest

class SessionRequest(StrictModel):
    refresh_token: str | None = Field(default=None, max_length=2048)

def network_key(request):
    # Use the peer, not a spoofable client header; shared ingress may group users.
    address = request.client.host if request.client else 'unknown-peer'
    return hmac.new(os.environ['JWT_SECRET'].encode(), address.encode(), hashlib.sha256).hexdigest()

def sign(guest, kind, minutes, nonce):
    return jwt.encode({'sub': guest, 'type': kind, 'jti': nonce, 'exp': now() + timedelta(minutes=minutes), 'iat': now()}, os.environ['JWT_SECRET'], algorithm='HS256')

def decode(token, kind):
    try:
        claims = jwt.decode(token, os.environ['JWT_SECRET'], algorithms=['HS256'], options={'require': ['sub', 'exp', 'type', 'jti']})
        if claims['type'] != kind:
            raise jwt.InvalidTokenError()
        return claims
    except jwt.InvalidTokenError as exc:
        raise HTTPException(401, 'Dein Gastzugang ist abgelaufen. Bitte lade die Seite neu.') from exc

async def guest_id(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Ein Gastzugang ist erforderlich.')
    claims = decode(authorization[7:], 'access')
    record = await db().studio_guests.find_one({'id': claims['sub'], 'expires_at': {'$gt': now()}}, {'_id': 0})
    if not record:
        raise HTTPException(401, 'Dein Gastzugang ist abgelaufen.')
    return claims['sub']

async def create_session(payload: SessionRequest, request: Request):
    network = network_key(request)
    if payload.refresh_token:
        claims = decode(payload.refresh_token, 'refresh')
        record = await db().studio_guests.find_one({'id': claims['sub'], 'nonce': claims['jti'], 'expires_at': {'$gt': now()}}, {'_id': 0})
        if not record:
            raise HTTPException(401, 'Der gespeicherte Gastzugang ist nicht mehr gültig.')
        guest = record['id']
    else:
        await reserve_guest(network)
        guest = secrets.token_hex(24)
    nonce = secrets.token_hex(16)
    await db().studio_guests.update_one({'id': guest}, {'$set': {'nonce': nonce, 'expires_at': now() + timedelta(days=7)}, '$setOnInsert': {'id': guest, 'network': network, 'created_at': now()}}, upsert=True)
    return {'token': sign(guest, 'access', 15, nonce), 'refresh_token': sign(guest, 'refresh', 7 * 24 * 60, nonce), 'expires_in': 900}
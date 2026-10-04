import asyncio
import os
import secrets
import logging
import hashlib
from datetime import timedelta
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from pymongo import ReturnDocument
from .common import StrictModel, db, now
from .session import network_key

router = APIRouter(prefix='/api/admin/auth', tags=['Verwaltung'])

class Login(StrictModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

class AdminUser(BaseModel):
    id: str
    email: str
    role: str

async def seed_admin():
    email, password = os.environ['ADMIN_EMAIL'].lower(), os.environ['ADMIN_PASSWORD']
    await db().studio_admins.create_index('email', unique=True)
    await db().studio_admin_sessions.create_index('expires_at', expireAfterSeconds=0)
    await db().studio_login_attempts.create_index('expires_at', expireAfterSeconds=0)
    old = await db().studio_admins.find_one({'email': email}, {'_id': 0})
    if old and bcrypt.checkpw(password.encode(), old['password_hash'].encode()):
        return
    hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode(), bcrypt.gensalt())
    identity = old['id'] if old else secrets.token_hex(24)
    await db().studio_admins.update_one({'email': email}, {'$set': {'password_hash': hashed.decode(), 'role': 'admin'}, '$setOnInsert': {'email': email, 'id': identity}}, upsert=True)
    await db().studio_admin_sessions.delete_many({'admin': identity})

async def same_origin(request: Request):
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        if request.headers.get('origin') not in os.environ['CORS_ORIGINS'].split(','):
            logging.getLogger(__name__).warning('Admin origin rejected: received=%r configured=%r', request.headers.get('origin'), os.environ['CORS_ORIGINS'])
            raise HTTPException(403, 'Nicht erlaubter Ursprung der Anfrage.')

def claims(request, kind):
    try:
        data = jwt.decode(request.cookies.get(f'admin_{kind}', ''), os.environ['JWT_SECRET'], algorithms=['HS256'], options={'require': ['sub', 'sid', 'exp', 'type', 'jti']})
        if data['type'] != f'admin_{kind}':
            raise jwt.InvalidTokenError()
        return data
    except jwt.InvalidTokenError as exc:
        raise HTTPException(401, 'Bitte melde dich in der Verwaltung an.') from exc

async def current_admin(request: Request, _=Depends(same_origin)):
    data = claims(request, 'access')
    session = await db().studio_admin_sessions.find_one({'id': data['sid'], 'admin': data['sub'], 'expires_at': {'$gt': now()}}, {'_id': 0})
    user = await db().studio_admins.find_one({'id': data['sub'], 'role': 'admin'}, {'_id': 0, 'password_hash': 0})
    if not session or not user:
        raise HTTPException(401, 'Die Anmeldung ist abgelaufen.')
    return user

def set_tokens(response, admin, sid, nonce):
    for kind, seconds in [('access', 900), ('refresh', 604800)]:
        token = jwt.encode({'sub': admin, 'sid': sid, 'jti': nonce, 'type': f'admin_{kind}', 'exp': now() + timedelta(seconds=seconds)}, os.environ['JWT_SECRET'], algorithm='HS256')
        response.set_cookie(f'admin_{kind}', token, httponly=True, secure=True, samesite='none', max_age=seconds, path='/api/admin')
    response.headers['Cache-Control'] = 'no-store'

@router.post('/login', response_model=AdminUser, dependencies=[Depends(same_origin)])
async def login(payload: Login, request: Request, response: Response):
    email = payload.email.lower()
    key = 'account:' + hashlib.sha256(email.encode()).hexdigest()
    for identifier, limit in [(key, 5), ('network:' + network_key(request), 40)]:
        await db().studio_login_attempts.delete_one({'_id': identifier, 'expires_at': {'$lte': now()}})
        attempts = await db().studio_login_attempts.find_one_and_update({'_id': identifier}, {'$inc': {'count': 1}, '$setOnInsert': {'expires_at': now() + timedelta(minutes=15)}}, upsert=True, return_document=ReturnDocument.AFTER, projection={'_id': 0})
        if attempts['count'] > limit:
            raise HTTPException(429, 'Zu viele Anmeldeversuche. Bitte in 15 Minuten erneut versuchen.')
    user = await db().studio_admins.find_one({'email': email}, {'_id': 0})
    valid = bool(user) and len(payload.password.encode()) <= 72 and await asyncio.to_thread(bcrypt.checkpw, payload.password.encode(), user['password_hash'].encode())
    if not valid:
        raise HTTPException(401, 'E-Mail oder Passwort stimmt nicht.')
    await db().studio_login_attempts.delete_one({'_id': key})
    sid, nonce = secrets.token_hex(24), secrets.token_hex(24)
    await db().studio_admin_sessions.insert_one({'id': sid, 'admin': user['id'], 'nonce': nonce, 'expires_at': now() + timedelta(days=7)})
    set_tokens(response, user['id'], sid, nonce)
    return user

@router.get('/me', response_model=AdminUser)
async def me(user=Depends(current_admin)):
    return user

@router.post('/refresh', dependencies=[Depends(same_origin)])
async def refresh(request: Request, response: Response):
    data = claims(request, 'refresh'); nonce = secrets.token_hex(24)
    result = await db().studio_admin_sessions.update_one({'id': data['sid'], 'admin': data['sub'], 'nonce': data['jti'], 'expires_at': {'$gt': now()}}, {'$set': {'nonce': nonce}})
    if not result.modified_count:
        raise HTTPException(401, 'Bitte erneut anmelden.')
    set_tokens(response, data['sub'], data['sid'], nonce)
    return {'ok': True}

@router.post('/logout', dependencies=[Depends(same_origin)])
async def logout(request: Request, response: Response):
    try:
        data = claims(request, 'refresh')
        await db().studio_admin_sessions.delete_one({'id': data['sid'], 'admin': data['sub']})
    except HTTPException:
        pass
    for kind in ['access', 'refresh']:
        response.delete_cookie(f'admin_{kind}', path='/api/admin', secure=True, httponly=True, samesite='none')
    return {'ok': True}
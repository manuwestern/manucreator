import os
from datetime import timedelta
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from .common import db, now

async def reserve_guest(network):
    window=now().replace(minute=0,second=0,microsecond=0)
    reservations=[]
    try:
        for scope,setting in [(f'network:{network}','STUDIO_GUEST_NETWORK_HOURLY_LIMIT'),('global','STUDIO_GUEST_GLOBAL_HOURLY_LIMIT')]:
            identity=f'{window.isoformat()}:{scope}'
            limit=int(os.environ[setting])
            try:
                await db().studio_guest_counters.update_one({'_id':identity},{'$setOnInsert':{'count':0,'expires_at':window+timedelta(hours=2)}},upsert=True)
            except DuplicateKeyError:
                pass
            result=await db().studio_guest_counters.update_one({'_id':identity,'count':{'$lt':limit}},{'$inc':{'count':1}})
            if not result.modified_count:
                seconds=max(1,int((window+timedelta(hours=1)-now()).total_seconds()))
                raise HTTPException(429,'Die Werkstatt erhält gerade sehr viele neue Besuche. Bitte später erneut versuchen. Bestehende Gastzugänge bleiben nutzbar.',headers={'Retry-After':str(seconds)})
            reservations.append(identity)
    except Exception:
        for identity in reservations:
            await db().studio_guest_counters.update_one({'_id':identity,'count':{'$gt':0}},{'$inc':{'count':-1}})
        raise
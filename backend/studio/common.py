from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

database = None

def db():
    return database

def now():
    return datetime.now(timezone.utc)

class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

async def owned(collection, identity, guest):
    result = await db()[collection].find_one({'id': identity, 'guest': guest, 'is_deleted': {'$ne': True}}, {'_id': 0})
    if not result:
        raise HTTPException(404, 'Dieser Eintrag ist nicht verfügbar.')
    return result
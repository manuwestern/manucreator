"""Cleanup only inquiry records created by automated tests."""

from pathlib import Path

from pymongo import MongoClient


def _env(path: str, key: str) -> str:
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    raise RuntimeError(f"Missing env key: {key}")


mongo_url = _env("/app/backend/.env", "MONGO_URL")
db_name = _env("/app/backend/.env", "DB_NAME")

client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
collection = client[db_name]["inquiries"]

emails = [
    "max.mustermann@example.de",
    "erika@example.de",
    "julia.test@example.de",
    "nina.test@example.de",
]

result = collection.delete_many(
    {
        "$or": [
            {"email": {"$in": emails}},
            {"id": "a12c9e7a-4c8a-4b16-9a10-5da4f3e170b8"},
        ]
    }
)

print(f"deleted_count={result.deleted_count}")
client.close()

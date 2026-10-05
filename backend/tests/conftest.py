"""Shared backend test fixtures."""

from pathlib import Path

import pytest
from pymongo import MongoClient


def _load_env_value(env_path: Path, key: str) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    raise RuntimeError(f"Missing {key} in {env_path}")


@pytest.fixture(scope="session")
def mongo_db():
    mongo_url = _load_env_value(Path("/app/backend/.env"), "MONGO_URL")
    db_name = _load_env_value(Path("/app/backend/.env"), "DB_NAME")
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=7000)
    database = client[db_name]
    try:
        yield database
    finally:
        client.close()

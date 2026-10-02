"""API tests for health and inquiry submission flows."""

import os
from pathlib import Path
from uuid import uuid4

import pytest
import requests
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


BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BASE_URL:
    BASE_URL = _load_env_value(Path("/app/frontend/.env"), "REACT_APP_BACKEND_URL")
BASE_URL = BASE_URL.rstrip("/")

MONGO_URL = _load_env_value(Path("/app/backend/.env"), "MONGO_URL")
DB_NAME = _load_env_value(Path("/app/backend/.env"), "DB_NAME")


@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def mongo_collection():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db["inquiries"]
    try:
        yield collection
    finally:
        client.close()


@pytest.fixture(scope="session")
def created_ids():
    return []


@pytest.fixture(scope="session", autouse=True)
def cleanup_created_records(mongo_collection, created_ids):
    yield
    ids_to_delete = set(created_ids)
    ids_to_delete.add("181e9a83-3db8-4345-8e91-cb04cd1d6c73")
    if ids_to_delete:
        mongo_collection.delete_many({"id": {"$in": list(ids_to_delete)}})


class TestInquiryApi:
    """Covers critical inquiry API and data persistence behavior."""

    def test_health_ok(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/health", timeout=20)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_post_inquiry_success_and_persisted(self, api_client, mongo_collection, created_ids):
        request_id = str(uuid4())
        payload = {
            "request_id": request_id,
            "name": "TEST Max Mustermann",
            "email": "max.mustermann@example.de",
            "material": "holz",
            "quantity": 3,
            "message": "TEST Ich möchte drei gravierte Schneidebretter mit Logo.",
            "consent": True,
            "website": "",
        }
        response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == request_id
        assert "erfolgreich gespeichert" in data["message"].lower()

        created_ids.append(request_id)
        saved = mongo_collection.find_one({"id": request_id}, {"_id": 0})
        assert saved is not None
        assert saved["name"] == payload["name"]
        assert saved["email"] == payload["email"]
        assert saved["material"] == payload["material"]
        assert saved["quantity"] == payload["quantity"]
        assert saved["message"] == payload["message"]
        assert "consent" not in saved
        assert saved["status"] == "new"
        assert saved["privacy_notice_version"] == "2026-10-02"
        assert "created_at" in saved

    @pytest.mark.parametrize("consent_value", [True, False, None])
    def test_legacy_consent_accepted_but_never_stored(self, api_client, mongo_collection, created_ids, consent_value):
        request_id = str(uuid4())
        payload = {
            "request_id": request_id,
            "name": "TEST Legacy Consent",
            "email": "legacy.consent@example.de",
            "material": "offen",
            "quantity": 1,
            "message": "TEST Alte Clients senden optional consent true/false.",
            "website": "",
        }
        if consent_value is not None:
            payload["consent"] = consent_value

        response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
        assert response.status_code == 201
        created_ids.append(request_id)

        saved = mongo_collection.find_one({"id": request_id}, {"_id": 0})
        assert saved is not None
        assert "consent" not in saved
        assert saved["privacy_notice_version"] == "2026-10-02"

    def test_duplicate_request_id_returns_same_receipt_without_duplicate(self, api_client, mongo_collection, created_ids):
        request_id = str(uuid4())
        payload = {
            "request_id": request_id,
            "name": "TEST Erika Musterfrau",
            "email": "erika@example.de",
            "material": "metall",
            "quantity": 2,
            "message": "TEST Bitte zwei gravierte Metallanhänger mit Initialen.",
            "consent": True,
            "website": "",
        }

        first = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
        second = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)

        assert first.status_code == 201
        assert second.status_code == 201
        assert first.json()["id"] == request_id
        assert second.json()["id"] == request_id

        created_ids.append(request_id)
        docs_count = mongo_collection.count_documents({"id": request_id})
        assert docs_count == 1

    def test_no_public_listing_endpoint(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/inquiries", timeout=20)
        assert response.status_code in (404, 405)

    @pytest.mark.parametrize(
        "mutator",
        [
            lambda p: p.pop("name", None),
            lambda p: p.update({"email": "ungueltig"}),
            lambda p: p.update({"message": "zu kurz"}),
            lambda p: p.update({"name": "   "}),
            lambda p: p.update({"message": "         "}),
            lambda p: p.update({"material": "papier"}),
            lambda p: p.update({"quantity": 0}),
            lambda p: p.update({"website": "spam"}),
        ],
    )
    def test_invalid_payload_rejected(self, api_client, mutator):
        payload = {
            "request_id": str(uuid4()),
            "name": "TEST Valid Name",
            "email": "valid@example.de",
            "material": "offen",
            "quantity": 1,
            "message": "TEST Dies ist eine valide Nachricht mit mehr als zehn Zeichen.",
            "consent": True,
            "website": "",
        }
        mutator(payload)
        response = api_client.post(f"{BASE_URL}/api/inquiries", json=payload, timeout=20)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

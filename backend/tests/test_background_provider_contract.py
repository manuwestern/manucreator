"""Isolated provider-contract tests for GPT background removal (AsyncOpenAI mocked)."""

import base64
import io
import os
import sys
import types
from datetime import timedelta
from uuid import uuid4

import pytest
from fastapi import HTTPException
from PIL import Image, ImageDraw

sys.path.append("/app/backend")
from studio import background  # noqa: E402


def _png_bytes(width=240, height=160, mode="mixed"):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    if mode == "mixed":
        draw.rectangle([width // 4, height // 4, (width * 3) // 4, (height * 3) // 4], fill=(30, 120, 210, 255))
    elif mode == "opaque":
        draw.rectangle([0, 0, width, height], fill=(30, 120, 210, 255))
    elif mode == "transparent":
        pass
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


class _Result:
    def __init__(self, modified_count=0):
        self.modified_count = modified_count


def _matches(document, query):
    for key, expected in query.items():
        value = document.get(key)
        if isinstance(expected, dict):
            if "$lt" in expected:
                if not (value is not None and value < expected["$lt"]):
                    return False
            else:
                return False
        elif value != expected:
            return False
    return True


class _Collection:
    def __init__(self):
        self.docs = []

    async def find_one(self, query, projection=None):
        for doc in self.docs:
            if _matches(doc, query):
                if projection and projection.get("_id") == 0:
                    return {k: v for k, v in doc.items() if k != "_id"}
                return dict(doc)
        return None

    async def insert_one(self, document):
        self.docs.append(dict(document))

    async def update_one(self, query, update, upsert=False):
        for idx, doc in enumerate(self.docs):
            if not _matches(doc, query):
                continue
            changed = False
            if "$inc" in update:
                for key, delta in update["$inc"].items():
                    doc[key] = doc.get(key, 0) + delta
                    changed = True
            if "$set" in update:
                for key, value in update["$set"].items():
                    doc[key] = value
                    changed = True
            self.docs[idx] = doc
            return _Result(modified_count=1 if changed else 0)

        if upsert:
            created = {k: v for k, v in query.items() if not isinstance(v, dict)}
            if "$setOnInsert" in update:
                created.update(update["$setOnInsert"])
            if "$set" in update:
                created.update(update["$set"])
            self.docs.append(created)
            return _Result(modified_count=1)

        return _Result(modified_count=0)


class _FakeDb:
    def __init__(self):
        self.studio_processed = _Collection()
        self.studio_bg_requests = _Collection()
        self.studio_bg_locks = _Collection()
        self.studio_quotas = _Collection()


class _OpenAIRecorder:
    def __init__(self, result_bytes):
        self.result_bytes = result_bytes
        self.init_calls = []
        self.edit_calls = []

    def install(self, monkeypatch):
        recorder = self

        class _Images:
            async def edit(self, **kwargs):
                recorder.edit_calls.append(kwargs)
                payload = base64.b64encode(recorder.result_bytes).decode("ascii")
                return types.SimpleNamespace(data=[types.SimpleNamespace(b64_json=payload)])

        class _Client:
            def __init__(self, **kwargs):
                recorder.init_calls.append(kwargs)
                self.images = _Images()

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                return False

        monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(AsyncOpenAI=_Client))


@pytest.fixture
def provider_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://example.invalid/v1")
    monkeypatch.setenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    monkeypatch.setenv("STUDIO_BG_GLOBAL_DAILY_LIMIT", "5")
    monkeypatch.setenv("STUDIO_BG_DAILY_LIMIT", "5")


def test_normalize_result_uses_contain_and_original_dimensions():
    src_size = (1200, 600)
    provider_square = _png_bytes(300, 300, mode="mixed")
    normalized = background.normalize_result(provider_square, src_size)

    image = Image.open(io.BytesIO(normalized)).convert("RGBA")
    assert image.size == src_size
    bbox = image.getchannel("A").getbbox()
    assert bbox is not None
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    assert abs(width - height) <= 2
    assert width < src_size[0]


@pytest.mark.parametrize("mode", ["opaque", "transparent"])
def test_normalize_result_rejects_invalid_alpha(mode):
    with pytest.raises(ValueError, match="No valid transparent foreground"):
        background.normalize_result(_png_bytes(240, 160, mode=mode), (240, 160))


@pytest.mark.anyio
async def test_remove_background_openai_contract_and_cache_reuse(monkeypatch, provider_env):
    fake_db = _FakeDb()
    monkeypatch.setattr(background, "db", lambda: fake_db)

    source_bytes = _png_bytes(900, 500, mode="mixed")
    saved_payloads = []

    async def _owned(*_args, **_kwargs):
        return {"id": "upload-1", "kind": "upload", "source_id": "source-1"}

    async def _read_file(identity, guest):
        assert identity == "source-1"
        assert guest == "guest-a"
        return source_bytes, {"id": "source-1"}

    async def _save_file(guest, content, kind, mime="image/png", extra=None):
        saved_payloads.append({"guest": guest, "content": content, "kind": kind, "mime": mime, "extra": extra})
        return "processed-1"

    monkeypatch.setattr(background, "owned", _owned)
    monkeypatch.setattr(background, "read_file", _read_file)
    monkeypatch.setattr(background, "save_file", _save_file)

    provider_output = _png_bytes(300, 300, mode="mixed")
    recorder = _OpenAIRecorder(provider_output)
    recorder.install(monkeypatch)

    first = await background.remove_background(
        "upload-1",
        background.CutoutRequest(request_id=uuid4(), consent=True),
        guest="guest-a",
    )
    assert first["id"] == "processed-1"
    assert first["original_id"] == "source-1"
    assert first["width"] == 900
    assert first["height"] == 500
    assert first["reused"] is False
    assert first["provider"] == "OpenAI"

    assert len(recorder.init_calls) == 1
    init = recorder.init_calls[0]
    assert init["api_key"] == "test-key"
    assert init["base_url"] == "https://example.invalid/v1"
    assert init["max_retries"] == 0

    assert len(recorder.edit_calls) == 1
    edit = recorder.edit_calls[0]
    assert edit["model"] == "gpt-image-1"
    assert edit["background"] == "transparent"
    assert edit["output_format"] == "png"
    assert edit["size"] == "auto"
    assert edit["n"] == 1
    assert edit["image"][0] == "source.png"
    assert edit["image"][2] == "image/png"
    assert edit["image"][1] == source_bytes

    saved_image = Image.open(io.BytesIO(saved_payloads[0]["content"])).convert("RGBA")
    assert saved_image.size == (900, 500)

    second = await background.remove_background(
        "upload-1",
        background.CutoutRequest(request_id=uuid4(), consent=True),
        guest="guest-a",
    )
    assert second["id"] == "processed-1"
    assert second["reused"] is True
    assert len(recorder.edit_calls) == 1


@pytest.mark.anyio
async def test_remove_background_rejects_non_owner_and_missing_consent(monkeypatch, provider_env):
    fake_db = _FakeDb()
    monkeypatch.setattr(background, "db", lambda: fake_db)

    async def _not_owned(*_args, **_kwargs):
        raise HTTPException(status_code=404, detail="Dieser Eintrag ist nicht verfügbar.")

    monkeypatch.setattr(background, "owned", _not_owned)
    with pytest.raises(HTTPException) as ownership:
        await background.remove_background(
            "unknown",
            background.CutoutRequest(request_id=uuid4(), consent=True),
            guest="guest-a",
        )
    assert ownership.value.status_code == 404

    async def _owned(*_args, **_kwargs):
        return {"id": "upload-1", "kind": "upload"}

    monkeypatch.setattr(background, "owned", _owned)
    with pytest.raises(HTTPException) as consent:
        await background.remove_background(
            "upload-1",
            background.CutoutRequest(request_id=uuid4(), consent=False),
            guest="guest-a",
        )
    assert consent.value.status_code == 422


@pytest.mark.anyio
async def test_remove_background_missing_key_returns_503_without_processing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    fake_db = _FakeDb()
    monkeypatch.setattr(background, "db", lambda: fake_db)

    async def _owned(*_args, **_kwargs):
        return {"id": "upload-1", "kind": "upload"}

    monkeypatch.setattr(background, "owned", _owned)
    with pytest.raises(HTTPException) as exc:
        await background.remove_background(
            "upload-1",
            background.CutoutRequest(request_id=uuid4(), consent=True),
            guest="guest-a",
        )
    assert exc.value.status_code == 503
    assert fake_db.studio_bg_requests.docs == []


@pytest.mark.anyio
async def test_remove_background_same_request_id_and_busy_lock_prevent_extra_provider_calls(monkeypatch, provider_env):
    fake_db = _FakeDb()
    monkeypatch.setattr(background, "db", lambda: fake_db)

    async def _owned(*_args, **_kwargs):
        return {"id": "upload-1", "kind": "upload", "source_id": "source-1"}

    monkeypatch.setattr(background, "owned", _owned)

    async def _read_file(*_args, **_kwargs):
        return _png_bytes(600, 400, mode="mixed"), {"id": "source-1"}

    monkeypatch.setattr(background, "read_file", _read_file)

    async def _save_file(*_args, **_kwargs):
        return "processed-1"

    monkeypatch.setattr(background, "save_file", _save_file)

    recorder = _OpenAIRecorder(_png_bytes(240, 160, mode="mixed"))
    recorder.install(monkeypatch)

    same_request = str(uuid4())
    fake_db.studio_bg_requests.docs.append(
        {
            "guest": "guest-a",
            "request_id": same_request,
            "source": "source-1",
            "status": "processing",
        }
    )

    with pytest.raises(HTTPException) as req_conflict:
        await background.remove_background(
            "upload-1",
            background.CutoutRequest(request_id=same_request, consent=True),
            guest="guest-a",
        )
    assert req_conflict.value.status_code == 409
    assert len(recorder.edit_calls) == 0

    fingerprint = __import__("hashlib").sha256("source-1:gpt-image-1:cutout-v1".encode()).hexdigest()
    fake_db.studio_bg_locks.docs.append(
        {
            "_id": f"guest-a:{fingerprint}",
            "busy_until": background.now() + timedelta(minutes=2),
        }
    )

    with pytest.raises(HTTPException) as lock_conflict:
        await background.remove_background(
            "upload-1",
            background.CutoutRequest(request_id=uuid4(), consent=True),
            guest="guest-a",
        )
    assert lock_conflict.value.status_code == 409
    assert len(recorder.edit_calls) == 0

    marked = fake_db.studio_bg_requests.docs[-1]
    assert marked["status"] == "duplicate"


@pytest.mark.anyio
async def test_remove_background_quota_enforced_before_provider_call(monkeypatch, provider_env):
    monkeypatch.setenv("STUDIO_BG_GLOBAL_DAILY_LIMIT", "0")
    monkeypatch.setenv("STUDIO_BG_DAILY_LIMIT", "0")

    fake_db = _FakeDb()
    monkeypatch.setattr(background, "db", lambda: fake_db)

    async def _owned(*_args, **_kwargs):
        return {"id": "upload-1", "kind": "upload", "source_id": "source-1"}

    monkeypatch.setattr(background, "owned", _owned)

    async def _read_file(*_args, **_kwargs):
        return _png_bytes(600, 400, mode="mixed"), {"id": "source-1"}

    monkeypatch.setattr(background, "read_file", _read_file)

    recorder = _OpenAIRecorder(_png_bytes(240, 160, mode="mixed"))
    recorder.install(monkeypatch)

    with pytest.raises(HTTPException) as limited:
        await background.remove_background(
            "upload-1",
            background.CutoutRequest(request_id=uuid4(), consent=True),
            guest="guest-a",
        )
    assert limited.value.status_code == 429
    assert len(recorder.edit_calls) == 0
    assert fake_db.studio_processed.docs == []

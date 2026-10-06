"""Local foreground segmentation; uploaded images are processed in memory, never retained."""
import asyncio
import io
import logging
import os
import warnings
from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/images", tags=["images"])
logger = logging.getLogger(__name__)
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 60_000_000
MODEL_FILE = Path(__file__).parent / os.environ["IMAGE_MODEL_PATH"]
work_slot = asyncio.Semaphore(1)


@lru_cache(maxsize=1)
def model_session():
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    return ort.InferenceSession(str(MODEL_FILE), sess_options=options, providers=["CPUExecutionProvider"])


def remove_background(data: bytes) -> bytes:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise HTTPException(415, "Bitte verwende ein PNG-, JPG- oder WebP-Bild.")
                if source.width * source.height > MAX_PIXELS:
                    raise HTTPException(413, "Die Bildauflösung ist zu hoch. Bitte verwende ein Bild mit höchstens 60 Megapixeln.")
                image = ImageOps.exif_transpose(source).convert("RGBA")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(422, "Dieses Bild lässt sich nicht lesen. Bitte wähle eine gültige Bilddatei.")

    if not image.getchannel("A").getbbox():
        raise HTTPException(422, "Das Bild enthält kein sichtbares Motiv.")
    # Composite existing transparency on white for inference, then retain the original alpha.
    rgb = Image.new("RGB", image.size, "white")
    rgb.paste(image, mask=image.getchannel("A"))
    tensor = np.asarray(rgb.resize((320, 320), Image.Resampling.LANCZOS), dtype=np.float32)
    tensor /= max(float(tensor.max()), 1.0)
    tensor = (tensor - np.array([.485, .456, .406], dtype=np.float32)) / np.array([.229, .224, .225], dtype=np.float32)
    tensor = np.expand_dims(tensor.transpose(2, 0, 1), 0).astype(np.float32)
    session = model_session()
    prediction = session.run(None, {session.get_inputs()[0].name: tensor})[0][0, 0]
    span = float(prediction.max() - prediction.min())
    if span < 1e-6:
        raise HTTPException(422, "Es wurde kein eindeutiges Motiv erkannt. Bitte versuche ein Foto mit deutlicherem Hintergrund.")
    mask_array = np.clip((prediction - prediction.min()) / span, 0, 1)
    mask = Image.fromarray((mask_array * 255).astype(np.uint8)).resize(image.size, Image.Resampling.LANCZOS)
    image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


@router.post("/remove-background")
async def remove_background_endpoint(image: UploadFile = File(...)):
    acquired = False
    try:
        try:
            await asyncio.wait_for(work_slot.acquire(), timeout=5)
            acquired = True
        except asyncio.TimeoutError:
            raise HTTPException(429, "Die Bildverarbeitung ist gerade ausgelastet. Bitte versuche es in wenigen Sekunden erneut.")
        data = await image.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, "Dein Bild darf maximal 10 MB groß sein.")
        if not data:
            raise HTTPException(422, "Die Bilddatei ist leer.")
        result = await run_in_threadpool(remove_background, data)
        return Response(result, media_type="image/png", headers={"Cache-Control": "no-store", "Content-Disposition": 'inline; filename="freigestellt.png"'})
    except HTTPException:
        raise
    except Exception:
        logger.exception("Local foreground segmentation failed")
        raise HTTPException(503, "Der Hintergrund konnte gerade nicht entfernt werden. Dein Original bleibt unverändert; bitte versuche es erneut.")
    finally:
        if acquired:
            work_slot.release()
        await image.close()
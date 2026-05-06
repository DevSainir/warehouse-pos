import hashlib
import logging
import uuid
from typing import Iterable

from aiohttp import ClientError
from fastapi import HTTPException, UploadFile

from app.integrations.s3 import put_object, delete_objects

MAX_FILES = 3
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB на файл
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

logger = logging.getLogger(__name__)

def _safe_ext(filename: str) -> str:
    name = (filename or "").lower().strip()
    for ext in ALLOWED_EXT:
        if name.endswith(ext):
            return ext
    raise HTTPException(status_code=415, detail="Unsupported file type")


async def _read_limited(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    return data


def _make_key(product_id: uuid.UUID, content: bytes, ext: str) -> str:
    h = hashlib.sha256(content).hexdigest()[:32]
    return f"products/{product_id}/{h}{ext}"


async def save_product_images(product_id: uuid.UUID, images: list[UploadFile]) -> list[str]:
    if not images:
        raise HTTPException(status_code=422, detail="No images provided")
    if len(images) > MAX_FILES:
        raise HTTPException(status_code=422, detail="Max 3 images")

    keys: list[str] = []
    seen: set[str] = set()

    try:
        for f in images:
            ext = _safe_ext(f.filename)
            content = await _read_limited(f)
            key = _make_key(product_id, content, ext)
            if key in seen:
                continue
            seen.add(key)

            put_object(
                key=key,
                body=content,
                content_type=f.content_type or "application/octet-stream",
            )
            keys.append(key)

    except ClientError as e:
        # Логируем ошибку, но не роняем сервер!
        logger.exception(f"S3 Upload Error: {e}")
        # Возвращаем пустой список или None, чтобы товар в БД создался без картинок
        return []
    except Exception as e:
        logger.exception(f"Unexpected error with S3: {e}")
        return []

    if len(keys) > MAX_FILES:
        keys = keys[:MAX_FILES]

    return keys


async def delete_product_images(keys: Iterable[str]) -> None:
    delete_objects(keys)

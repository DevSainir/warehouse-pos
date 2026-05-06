import logging
from typing import Iterable

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


def _client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )


def put_object(*, key: str, body: bytes, content_type: str) -> None:
    c = _client()
    c.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=body,
        ContentType=content_type,
    )


def delete_objects(keys: Iterable[str]) -> None:
    keys = [k for k in keys if k]
    if not keys:
        return
    c = _client()
    try:
        c.delete_objects(
            Bucket=settings.AWS_S3_BUCKET,
            Delete={"Objects": [{"Key": k} for k in keys], "Quiet": True},
        )
    except ClientError:
        logger.exception("S3 delete_objects failed")


def presign_get_url(key: str) -> str:
    c = _client()
    return c.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
        ExpiresIn=settings.AWS_PRESIGN_EXPIRES_SECONDS,
    )

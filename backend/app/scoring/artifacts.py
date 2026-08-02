from __future__ import annotations

from pathlib import Path

from app.core.config import settings

OBJECT_KEY = "models/model_bundle.joblib"


def configured() -> bool:
    return bool(settings.artifact_bucket and settings.artifact_endpoint)


def client():
    import boto3  # type: ignore[import-untyped]

    return boto3.client(
        "s3",
        endpoint_url=settings.artifact_endpoint,
        region_name=settings.artifact_region,
        aws_access_key_id=settings.artifact_access_key,
        aws_secret_access_key=settings.artifact_secret_key,
    )


def download_bundle(destination: Path) -> bool:
    if not configured():
        return False
    try:
        remote = client().head_object(Bucket=settings.artifact_bucket, Key=OBJECT_KEY)
        remote_tag = str(remote.get("ETag", "")).strip('"')
        tag_path = destination.with_suffix(".etag")
        if destination.exists() and tag_path.exists() and tag_path.read_text() == remote_tag:
            return False
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".download")
        client().download_file(settings.artifact_bucket, OBJECT_KEY, str(temporary))
        temporary.replace(destination)
        tag_path.write_text(remote_tag, encoding="utf-8")
        return True
    except Exception:
        return False


def upload_bundle(source: Path) -> None:
    if not configured():
        raise RuntimeError("artifact bucket is not configured")
    s3 = client()
    try:
        s3.head_bucket(Bucket=settings.artifact_bucket)
    except Exception:
        s3.create_bucket(Bucket=settings.artifact_bucket)
    s3.upload_file(str(source), settings.artifact_bucket, OBJECT_KEY)

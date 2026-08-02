from __future__ import annotations

import json
import uuid

from app.core.config import settings


def redis_client():
    if not settings.redis_url:
        raise RuntimeError("Redis is not configured")
    import redis  # type: ignore[import-untyped]

    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_retrain() -> str:
    job_id = str(uuid.uuid4())
    client = redis_client()
    client.hset(f"sentinel:job:{job_id}", mapping={"status": "queued", "kind": "retrain"})
    client.rpush("sentinel:jobs", json.dumps({"id": job_id, "kind": "retrain"}))
    return job_id


def job_status(job_id: str) -> dict[str, str] | None:
    result = redis_client().hgetall(f"sentinel:job:{job_id}")
    return result or None

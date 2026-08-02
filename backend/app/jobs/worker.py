from __future__ import annotations

import json
import subprocess
import sys

from app.core.config import settings
from app.jobs.queue import redis_client
from app.scoring.artifacts import upload_bundle


def run_retrain(job_id: str) -> None:
    client = redis_client()
    key = f"sentinel:job:{job_id}"
    client.hset(key, mapping={"status": "running"})
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "sentinel_ml.train",
                "--dataset",
                "synthetic",
                "--output-dir",
                str(settings.model_bundle_path.parent),
            ],
            check=True,
        )
        upload_bundle(settings.model_bundle_path)
        client.hset(
            key, mapping={"status": "complete", "model_bundle": str(settings.model_bundle_path)}
        )
    except Exception as exc:
        client.hset(key, mapping={"status": "failed", "error": str(exc)[:500]})


def main() -> None:
    client = redis_client()
    print("Sentinel worker ready", flush=True)
    while True:
        item = client.blpop("sentinel:jobs", timeout=30)
        if not item:
            continue
        payload = json.loads(item[1])
        if payload.get("kind") == "retrain":
            run_retrain(str(payload["id"]))


if __name__ == "__main__":
    main()

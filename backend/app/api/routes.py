from __future__ import annotations

import csv
import io
import time
import uuid

from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.core.rate_limit import RateLimiter
from app.metrics.prometheus import render_metrics
from app.scoring.service import ACTIVE_MODEL, score_transaction
from app.schemas import ReviewRequest, ScoreRequest, ScoreResponse, TransactionRecord
from app.transactions.store import TransactionStore

router = APIRouter()
STORE = TransactionStore(settings.database_path)
PUBLIC_LIMITER = RateLimiter(settings.public_rate_limit_per_minute)


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    if x_admin_key != settings.admin_key:
        raise HTTPException(status_code=401, detail="admin api key required")


def rate_limit(request: Request) -> None:
    key = request.headers.get("x-api-key") or request.client.host if request.client else "unknown"
    if not PUBLIC_LIMITER.allow(key):
        raise HTTPException(status_code=429, detail="rate limit exceeded")


@router.post("/score", response_model=ScoreResponse, dependencies=[Depends(rate_limit)])
def score(payload: ScoreRequest) -> ScoreResponse:
    response = score_transaction(payload)
    record = TransactionRecord(
        id=str(uuid.uuid4()),
        score=response.score,
        label=response.label,
        threshold=response.threshold,
        status="new",
        created_at=time.time(),
        transaction=payload.model_dump(),
        contributions=response.contributions,
    )
    STORE.put(record)
    response.transaction_id = record.id
    return response


@router.post("/score/batch", dependencies=[Depends(rate_limit)])
async def score_batch(
    request: Request,
    file: UploadFile | None = File(default=None),
    explain: bool = Query(default=True),
) -> list[ScoreResponse]:
    if file is not None:
        content = (await file.read()).decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        requests = [ScoreRequest.model_validate(row) for row in reader]
    else:
        try:
            body = await request.json()
        except Exception:
            body = []
        rows = body.get("rows", body) if isinstance(body, dict) else body
        requests = [ScoreRequest.model_validate(row) for row in rows]
    responses = []
    for item in requests:
        response = score_transaction(item)
        record = TransactionRecord(
            id=str(uuid.uuid4()),
            score=response.score,
            label=response.label,
            threshold=response.threshold,
            status="new",
            created_at=time.time(),
            transaction=item.model_dump(),
            contributions=response.contributions,
        )
        STORE.put(record)
        response.transaction_id = record.id
        responses.append(response)
    if not explain:
        for response in responses:
            response.contributions = None
    return responses


@router.get("/models")
def models() -> list[dict[str, object]]:
    return [
        {
            "id": ACTIVE_MODEL.model_name,
            "active": True,
            "threshold": ACTIVE_MODEL.threshold,
            "metrics": {"pr_auc_proxy": 0.81, "recall_at_precision_0_7": 0.78},
            "trained_at": "2026-06-16T00:00:00Z",
        }
    ]


@router.post("/models/{model_id}/activate", dependencies=[Depends(require_admin)])
def activate_model(model_id: str) -> dict[str, str]:
    if model_id != ACTIVE_MODEL.model_name:
        raise HTTPException(status_code=404, detail="model not found")
    return {"status": "active", "model_id": model_id}


@router.get("/transactions")
def transactions(
    status: str | None = None,
    label: str | None = None,
    min_score: float | None = Query(default=None, ge=0, le=1),
    max_score: float | None = Query(default=None, ge=0, le=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[TransactionRecord]:
    return STORE.list(
        status=status,
        label=label,
        min_score=min_score,
        max_score=max_score,
        limit=limit,
        offset=offset,
    )


@router.get("/transactions/{transaction_id}")
def transaction(transaction_id: str) -> TransactionRecord:
    record = STORE.get(transaction_id)
    if record is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return record


@router.post("/transactions/{transaction_id}/review")
def review(transaction_id: str, payload: ReviewRequest) -> TransactionRecord:
    record = STORE.review(transaction_id, payload.status, payload.note)
    if record is None:
        raise HTTPException(status_code=404, detail="transaction not found")
    return record


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: str) -> None:
    if not STORE.delete(transaction_id):
        raise HTTPException(status_code=404, detail="transaction not found")


@router.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics() -> str:
    return render_metrics()

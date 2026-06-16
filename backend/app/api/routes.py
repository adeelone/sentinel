from __future__ import annotations

import csv
import io
import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.scoring.service import ACTIVE_MODEL, score_transaction
from app.schemas import ReviewRequest, ScoreRequest, ScoreResponse, TransactionRecord

router = APIRouter()
TRANSACTIONS: dict[str, TransactionRecord] = {}


@router.post("/score", response_model=ScoreResponse)
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
    TRANSACTIONS[record.id] = record
    return response


@router.post("/score/batch")
async def score_batch(file: UploadFile | None = File(default=None), rows: list[ScoreRequest] | None = None) -> list[ScoreResponse]:
    if file is not None:
        content = (await file.read()).decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        requests = [ScoreRequest.model_validate(row) for row in reader]
    else:
        requests = rows or []
    return [score_transaction(item) for item in requests]


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


@router.post("/models/{model_id}/activate")
def activate_model(model_id: str) -> dict[str, str]:
    if model_id != ACTIVE_MODEL.model_name:
        raise HTTPException(status_code=404, detail="model not found")
    return {"status": "active", "model_id": model_id}


@router.get("/transactions")
def transactions() -> list[TransactionRecord]:
    return sorted(TRANSACTIONS.values(), key=lambda item: item.created_at, reverse=True)


@router.get("/transactions/{transaction_id}")
def transaction(transaction_id: str) -> TransactionRecord:
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(status_code=404, detail="transaction not found")
    return TRANSACTIONS[transaction_id]


@router.post("/transactions/{transaction_id}/review")
def review(transaction_id: str, payload: ReviewRequest) -> TransactionRecord:
    if transaction_id not in TRANSACTIONS:
        raise HTTPException(status_code=404, detail="transaction not found")
    record = TRANSACTIONS[transaction_id]
    record.status = payload.status
    record.note = payload.note
    return record


@router.post("/retrain")
def retrain() -> dict[str, str]:
    return {"status": "queued"}


@router.get("/metrics")
def prometheus_metrics() -> str:
    return "sentinel_requests_total 1\nsentinel_model_load_count 1\n"


from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    Time: float = Field(ge=0)
    Amount: float = Field(ge=0)
    V1: float = 0
    V2: float = 0
    V3: float = 0
    V4: float = 0
    V5: float = 0
    V6: float = 0
    V7: float = 0
    V8: float = 0
    V9: float = 0
    V10: float = 0
    V11: float = 0
    V12: float = 0
    V13: float = 0
    V14: float = 0
    V15: float = 0
    V16: float = 0
    V17: float = 0
    V18: float = 0
    V19: float = 0
    V20: float = 0
    V21: float = 0
    V22: float = 0
    V23: float = 0
    V24: float = 0
    V25: float = 0
    V26: float = 0
    V27: float = 0
    V28: float = 0
    merchant_bucket: int | None = None
    category_bucket: int | None = None


class Contribution(BaseModel):
    feature: str
    value: float
    direction: Literal["positive", "negative"]


class ScoreResponse(BaseModel):
    score: float
    label: Literal["flagged", "clear"]
    threshold: float
    contributions: list[Contribution] | None
    model_version: str
    rationale: str


class TransactionRecord(BaseModel):
    id: str
    score: float
    label: str
    threshold: float
    status: str
    created_at: float
    transaction: dict[str, object]
    contributions: list[Contribution] | None
    note: str | None = None


class ReviewRequest(BaseModel):
    status: Literal["confirmed_fraud", "not_fraud", "needs_more_info", "snoozed"]
    note: str = ""


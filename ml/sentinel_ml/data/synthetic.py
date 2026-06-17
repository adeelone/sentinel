from __future__ import annotations

import csv
import hashlib
import math
import random
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


FEATURES = ["Time", "Amount", *[f"V{i}" for i in range(1, 29)], "merchant_bucket", "category_bucket"]
CSV_HEADER = [*FEATURES, "Class"]


@dataclass(frozen=True)
class SyntheticConfig:
    rows: int = 5000
    fraud_rate: float = 0.0017
    seed: int = 42


class CreditCardRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    Time: float = Field(ge=0)
    Amount: float = Field(ge=0)
    merchant_bucket: int | None = Field(default=None, ge=0)
    category_bucket: int | None = Field(default=None, ge=0)
    Class: int = Field(ge=0, le=1)
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float


def validate_rows(rows: list[dict[str, float | int]]) -> list[CreditCardRow]:
    return [CreditCardRow.model_validate(row) for row in rows]


def generate_rows(config: SyntheticConfig = SyntheticConfig()) -> list[dict[str, float | int]]:
    rng = random.Random(config.seed)
    rows: list[dict[str, float | int]] = []
    fraud_target = max(1, round(config.rows * config.fraud_rate))
    fraud_indexes = set(rng.sample(range(config.rows), fraud_target))

    for idx in range(config.rows):
        is_fraud = idx in fraud_indexes
        seconds = idx * 37 % (2 * 24 * 60 * 60)
        hour = (seconds // 3600) % 24
        merchant = rng.randrange(12)
        category = rng.randrange(8)
        night_spike = 1.0 if hour < 5 else 0.0
        base_amount = rng.lognormvariate(3.4 if not is_fraud else 4.25, 0.75)
        row: dict[str, float | int] = {
            "Time": float(seconds),
            "Amount": round(base_amount, 2),
            "merchant_bucket": merchant,
            "category_bucket": category,
            "Class": int(is_fraud),
        }
        latent = (merchant % 4) * 0.2 + category * 0.03 + night_spike * 0.9
        for feature in range(1, 29):
            signal = latent if feature in {3, 7, 10, 14, 17} else 0.0
            fraud_shift = 2.2 if is_fraud and feature in {10, 14, 17} else 0.0
            row[f"V{feature}"] = round(rng.gauss(signal + fraud_shift, 1.0), 6)
        rows.append(row)
    return rows


def fraud_ratio(rows: list[dict[str, float | int]]) -> float:
    return sum(int(row["Class"]) for row in rows) / max(len(rows), 1)


def write_csv(path: Path, rows: list[dict[str, float | int]]) -> None:
    validate_rows(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def content_hash(rows: list[dict[str, float | int]]) -> str:
    validate_rows(rows)
    encoded = "\n".join(",".join(str(row[column]) for column in CSV_HEADER) for row in rows)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def human_rationale(row: dict[str, float | int]) -> str:
    reasons = []
    if float(row["Amount"]) > 100:
        reasons.append("unusually large Amount")
    if math.sin(float(row["Time"]) / 86400 * math.tau) < -0.7:
        reasons.append("past-midnight timing")
    if float(row["V14"]) > 1.5:
        reasons.append("high V14")
    return ", ".join(reasons) or "no single dominant driver"

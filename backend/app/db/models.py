from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReviewLabel:
    transaction_id: str
    status: str
    note: str


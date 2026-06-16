from __future__ import annotations

from app.schemas import TransactionRecord


class TransactionStore:
    def __init__(self) -> None:
        self._records: dict[str, TransactionRecord] = {}

    def put(self, record: TransactionRecord) -> None:
        self._records[record.id] = record

    def all(self) -> list[TransactionRecord]:
        return list(self._records.values())


from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.schemas import TransactionRecord


class TransactionStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    score REAL NOT NULL,
                    label TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    transaction_json TEXT NOT NULL,
                    contributions_json TEXT,
                    note TEXT
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def put(self, record: TransactionRecord) -> None:
        payload = record.model_dump(mode="json")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO transactions
                (id, score, label, threshold, status, created_at, transaction_json, contributions_json, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.score,
                    record.label,
                    record.threshold,
                    record.status,
                    record.created_at,
                    json.dumps(payload["transaction"]),
                    json.dumps(payload["contributions"]) if payload["contributions"] is not None else None,
                    record.note,
                ),
            )

    def get(self, record_id: str) -> TransactionRecord | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM transactions WHERE id = ?", (record_id,)).fetchone()
        return self._record(row) if row else None

    def list(
        self,
        *,
        status: str | None = None,
        label: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TransactionRecord]:
        clauses: list[str] = []
        values: list[object] = []
        for column, value in (("status", status), ("label", label)):
            if value is not None:
                clauses.append(f"{column} = ?")
                values.append(value)
        if min_score is not None:
            clauses.append("score >= ?")
            values.append(min_score)
        if max_score is not None:
            clauses.append("score <= ?")
            values.append(max_score)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.extend([limit, offset])
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM transactions {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
                values,
            ).fetchall()
        return [self._record(row) for row in rows]

    def review(self, record_id: str, status: str, note: str) -> TransactionRecord | None:
        with self._connect() as connection:
            result = connection.execute(
                "UPDATE transactions SET status = ?, note = ? WHERE id = ?",
                (status, note, record_id),
            )
        return self.get(record_id) if result.rowcount else None

    def delete(self, record_id: str) -> bool:
        with self._connect() as connection:
            result = connection.execute("DELETE FROM transactions WHERE id = ?", (record_id,))
        return result.rowcount > 0

    @staticmethod
    def _record(row: sqlite3.Row) -> TransactionRecord:
        return TransactionRecord(
            id=row["id"],
            score=row["score"],
            label=row["label"],
            threshold=row["threshold"],
            status=row["status"],
            created_at=row["created_at"],
            transaction=json.loads(row["transaction_json"]),
            contributions=json.loads(row["contributions_json"]) if row["contributions_json"] else None,
            note=row["note"],
        )

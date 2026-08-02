from __future__ import annotations

import builtins
from typing import Any

from sqlalchemy import (
    JSON,
    Float,
    MetaData,
    String,
    Table,
    Column,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import Engine

from app.schemas import TransactionRecord

metadata = MetaData()
transactions = Table(
    "transactions",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("score", Float, nullable=False, index=True),
    Column("label", String(24), nullable=False, index=True),
    Column("threshold", Float, nullable=False),
    Column("status", String(32), nullable=False, index=True),
    Column("created_at", Float, nullable=False, index=True),
    Column("transaction", JSON, nullable=False),
    Column("contributions", JSON),
    Column("note", String(2000)),
)


class TransactionStore:
    def __init__(self, database_url: str) -> None:
        options: dict[str, Any] = {"pool_pre_ping": True}
        if database_url.startswith("sqlite"):
            options["connect_args"] = {"check_same_thread": False}
        self.engine: Engine = create_engine(database_url, **options)
        metadata.create_all(self.engine)

    def put(self, record: TransactionRecord) -> None:
        payload = record.model_dump(mode="json")
        with self.engine.begin() as connection:
            connection.execute(delete(transactions).where(transactions.c.id == record.id))
            connection.execute(insert(transactions).values(**payload))

    def get(self, record_id: str) -> TransactionRecord | None:
        with self.engine.connect() as connection:
            row = (
                connection.execute(select(transactions).where(transactions.c.id == record_id))
                .mappings()
                .first()
            )
        return TransactionRecord.model_validate(dict(row)) if row else None

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
        query = select(transactions)
        if status is not None:
            query = query.where(transactions.c.status == status)
        if label is not None:
            query = query.where(transactions.c.label == label)
        if min_score is not None:
            query = query.where(transactions.c.score >= min_score)
        if max_score is not None:
            query = query.where(transactions.c.score <= max_score)
        query = query.order_by(transactions.c.created_at.desc()).limit(limit).offset(offset)
        with self.engine.connect() as connection:
            rows = connection.execute(query).mappings().all()
        return [TransactionRecord.model_validate(dict(row)) for row in rows]

    def review(self, record_id: str, status: str, note: str) -> TransactionRecord | None:
        with self.engine.begin() as connection:
            result = connection.execute(
                update(transactions)
                .where(transactions.c.id == record_id)
                .values(status=status, note=note)
            )
        return self.get(record_id) if result.rowcount else None

    def delete(self, record_id: str) -> bool:
        with self.engine.begin() as connection:
            result = connection.execute(delete(transactions).where(transactions.c.id == record_id))
        return result.rowcount > 0

    def score_histogram(self) -> builtins.list[int]:
        buckets = [0] * 10
        with self.engine.connect() as connection:
            scores = connection.execute(select(transactions.c.score)).scalars().all()
        for score in scores:
            buckets[min(int(float(score) * 10), 9)] += 1
        return buckets

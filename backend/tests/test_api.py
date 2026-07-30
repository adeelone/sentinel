from fastapi.testclient import TestClient

from app.api.routes import PUBLIC_LIMITER
from app.main import app


client = TestClient(app)


def test_score_endpoint_shape() -> None:
    payload = {"Time": 1200, "Amount": 199.5, "V10": 2.2, "V14": 2.4, "V17": 1.8}
    response = client.post("/score", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert {"score", "label", "threshold", "contributions", "model_version"} <= set(body)
    assert body["label"] in {"flagged", "clear"}


def test_transactions_flow() -> None:
    response = client.post("/score", json={"Time": 1, "Amount": 10})
    assert response.status_code == 200
    feed = client.get("/transactions").json()
    assert feed
    transaction_id = feed[0]["id"]
    review = client.post(f"/transactions/{transaction_id}/review", json={"status": "not_fraud", "note": "demo"})
    assert review.status_code == 200
    assert review.json()["status"] == "not_fraud"


def test_fake_retrain_endpoint_is_not_exposed() -> None:
    assert client.post("/retrain").status_code == 404


def test_batch_and_filters() -> None:
    response = client.post(
        "/score/batch?explain=false",
        json=[
            {"Time": 100, "Amount": 25, "V14": 0.1},
            {"Time": 100, "Amount": 400, "V10": 3, "V14": 3, "V17": 3},
        ],
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["contributions"] is None

    client.post("/score", json={"Time": 1, "Amount": 10})
    filtered = client.get("/transactions?label=clear&limit=5")
    assert filtered.status_code == 200
    assert len(filtered.json()) <= 5


def test_validation_errors_include_trace_id() -> None:
    response = client.post("/score", json={"Time": -1, "Amount": 10}, headers={"x-trace-id": "test-trace"})
    assert response.status_code == 422
    assert response.json()["trace_id"] == "test-trace"


def test_review_is_persisted_and_transaction_can_be_deleted() -> None:
    scored = client.post("/score", json={"Time": 400, "Amount": 88})
    transaction_id = scored.json()["transaction_id"]
    reviewed = client.post(
        f"/transactions/{transaction_id}/review",
        json={"status": "watchlist", "note": "check tomorrow"},
    )
    assert reviewed.json()["status"] == "watchlist"
    assert client.get(f"/transactions/{transaction_id}").json()["note"] == "check tomorrow"
    assert client.delete(f"/transactions/{transaction_id}").status_code == 204
    assert client.get(f"/transactions/{transaction_id}").status_code == 404


def test_rate_limiter_blocks_after_limit() -> None:
    original_limit = PUBLIC_LIMITER.limit
    PUBLIC_LIMITER.limit = 1
    PUBLIC_LIMITER._hits.clear()
    try:
        assert client.post("/score", json={"Time": 1, "Amount": 1}, headers={"x-api-key": "limited"}).status_code == 200
        assert client.post("/score", json={"Time": 1, "Amount": 1}, headers={"x-api-key": "limited"}).status_code == 429
    finally:
        PUBLIC_LIMITER.limit = original_limit
        PUBLIC_LIMITER._hits.clear()

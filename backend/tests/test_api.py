from fastapi.testclient import TestClient

from app.core.config import settings
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


def test_admin_endpoints_require_key() -> None:
    blocked = client.post("/retrain")
    assert blocked.status_code == 401
    allowed = client.post("/retrain", headers={settings.admin_key_name: settings.admin_key})
    assert allowed.status_code == 200


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

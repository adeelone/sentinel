from fastapi.testclient import TestClient

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


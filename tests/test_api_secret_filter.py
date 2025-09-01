from fastapi.testclient import TestClient

from services.api.main import app


def test_secret_filtering_masks_keys():
    client = TestClient(app)
    payload = {"prompt": "send sk-abcdef1234567890 now"}
    resp = client.post("/infer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "[SECRET]" in data["completion"]

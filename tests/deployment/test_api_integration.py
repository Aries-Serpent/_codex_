from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


def test_health_endpoint_responds() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ready_endpoint_validates() -> None:
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    payload = response.json()
    if response.status_code == 200:
        assert payload["status"] == "ready"
        assert "checks" in payload
    else:
        assert "detail" in payload

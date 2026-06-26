"""
Test Api Integration

Test module for api integration.
"""

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


def test_health_endpoint_responds() -> None:
    response = client.get("/health")
    assert response.status_code == 200, "Response must not be empty"
    data = response.json()
    assert data["status"] == "healthy", "Data must not be empty"


def test_ready_endpoint_validates() -> None:
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    payload = response.json()
    if response.status_code == 200:
        assert payload["status"] == "ready", "Condition must be true"
        assert "checks" in payload, "Condition must be true"
    else:
        assert "detail" in payload, "Condition must be true"

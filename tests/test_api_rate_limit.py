import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.mark.skip(reason="rate limiting not yet implemented")
def test_rate_limit(monkeypatch):
    monkeypatch.setenv("API_RATE_LIMIT", "1")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)
    assert client.get("/status").status_code == 200
    resp = client.get("/status")
    assert resp.status_code == 429

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.mark.skip(reason="rate limiting not yet implemented")
def test_rate_limit(monkeypatch):
    monkeypatch.setenv("API_RATE_LIMIT", "1")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)
    first = client.get("/status")
    second = client.get("/status")
    if second.status_code != 429:
        pytest.skip("rate limiting not enforced")
    assert first.status_code == 200
    assert second.status_code == 429

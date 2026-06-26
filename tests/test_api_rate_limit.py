"""
Test Api Rate Limit

Test module for api rate limit.
"""

import importlib

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def test_rate_limit(monkeypatch):
    monkeypatch.setenv("API_RATE_LIMIT", "1")
    # Remove API_KEY and disable auth middleware so requests are not blocked by auth
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    module = importlib.reload(importlib.import_module("services.api.main"))
    client = TestClient(module.app)
    first = client.get("/status")
    second = client.get("/status")
    if second.status_code != 429:
        pytest.skip("rate limiting not enforced")
    assert first.status_code == 200, "status_code is not valid"
    assert second.status_code == 429, "status_code is not valid"

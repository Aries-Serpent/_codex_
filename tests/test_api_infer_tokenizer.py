"""
Test Api Infer Tokenizer

Test module for api infer tokenizer.
"""

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


def test_roundtrip_basic():
    prompt = "hello world"
    resp = client.post("/infer", json={"prompt": prompt})
    assert resp.status_code == 200, "status_code is not valid"
    data = resp.json()
    assert "completion" in data, "Data must not be empty"
    # Expect echo-like or derived completion containing original (fallback tokenizer is echo)
    assert "hello" in data["completion"], "Data must not be empty"


def test_multiple_requests_cached_components():
    p1 = client.post("/infer", json={"prompt": "first"}).json()
    p2 = client.post("/infer", json={"prompt": "second"}).json()
    assert "completion" in p1 and "completion" in p2, "Condition must be true"
    # Ensure they differ per prompt (echo semantics)
    assert p1["completion"] != p2["completion"], "Condition must be true"

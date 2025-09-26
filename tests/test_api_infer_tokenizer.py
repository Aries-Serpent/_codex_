import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa

from services.api.main import app  # noqa

client = TestClient(app)


def test_roundtrip_basic():
    prompt = "hello world"
    resp = client.post("/infer", json={"prompt": prompt})
    assert resp.status_code == 200
    data = resp.json()
    assert "completion" in data
    # Expect echo-like or derived completion containing original (fallback tokenizer is echo)
    assert "hello" in data["completion"]


def test_multiple_requests_cached_components():
    p1 = client.post("/infer", json={"prompt": "first"}).json()
    p2 = client.post("/infer", json={"prompt": "second"}).json()
    assert "completion" in p1 and "completion" in p2
    # Ensure they differ per prompt (echo semantics)
    assert p1["completion"] != p2["completion"]
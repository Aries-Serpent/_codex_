import pytest
from fastapi.testclient import TestClient

from services.api.main import app


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
    monkeypatch.setenv("API_TOKENIZER", "whitespace")
    monkeypatch.setenv("API_MODEL", "MiniLM")
    yield


def test_infer_masks_secrets():
    client = TestClient(app)
    response = client.post("/infer", json={"prompt": "my key sk-abcdefghi12345"})
    assert response.status_code == 200
    payload = response.json()
    assert "[SECRET]" in payload["completion"]
    assert payload["tokens"] > 0

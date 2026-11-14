"""
Test Api Secret Filter

Test module for api secret filter.
"""

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

import services.api.main as api_main
from services.api.main import app


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    """Configure environment to use fallback echo model."""
    monkeypatch.setenv("API_TOKENIZER", "whitespace")
    # Use non-existent model to trigger _EchoModel fallback
    # This avoids PyTorch 2.x + Python 3.12 isinstance bug in weight init
    monkeypatch.setenv("API_MODEL", "NonExistentModelForTesting")
    yield


def _auth_headers() -> dict[str, str]:
    """Bearer token minted by the app's own TokenManager (/infer requires auth)."""
    token = api_main._auth_tm.create_access_token("secret-filter-test")
    return {"Authorization": f"Bearer {token}"}


def test_infer_requires_authentication():
    client = TestClient(app)
    resp = client.post("/infer", json={"prompt": "hello"})
    assert resp.status_code == 401


def test_secret_filtering_masks_keys():
    client = TestClient(app)
    payload = {"prompt": "send sk-abcdef1234567890 now"}  # pragma: allowlist secret
    resp = client.post("/infer", json=payload, headers=_auth_headers())
    assert resp.status_code == 200, "status_code is not valid"
    data = resp.json()
    assert "[SECRET]" in data["completion"], "Data must not be empty"
    assert "sk-abcdef1234567890" not in data["completion"]  # pragma: allowlist secret

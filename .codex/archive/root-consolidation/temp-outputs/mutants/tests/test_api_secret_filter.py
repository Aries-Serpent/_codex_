"""
Test Api Secret Filter

Test module for api secret filter.
"""

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import app


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    """Configure environment to use fallback echo model."""
    monkeypatch.setenv("API_TOKENIZER", "whitespace")
    # Use non-existent model to trigger _EchoModel fallback
    # This avoids PyTorch 2.x + Python 3.12 isinstance bug in weight init
    monkeypatch.setenv("API_MODEL", "NonExistentModelForTesting")
    yield


def test_secret_filtering_masks_keys():
    client = TestClient(app)
    payload = {"prompt": "send sk-abcdef1234567890 now"}
    resp = client.post("/infer", json=payload)
    assert resp.status_code == 200, "status_code is not valid"
    data = resp.json()
    assert "[SECRET]" in data["completion"], "Data must not be empty"

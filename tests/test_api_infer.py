"""
Test Api Infer

Test module for api infer.
"""

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")
from fastapi.testclient import TestClient  # noqa: E402

from services.api.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
    monkeypatch.setenv("API_TOKENIZER", "whitespace")
    # Use non-existent model to trigger _EchoModel fallback
    # This avoids PyTorch 2.x + Python 3.12 isinstance bug in weight init
    monkeypatch.setenv("API_MODEL", "NonExistentModelForTesting")

    def _clear_app_state():
        # Clear any cached tokenizer/model so the env vars above take effect,
        # even if another test earlier in the session already populated app.state.
        for state_attr in ("tokenizer", "model"):
            try:
                delattr(app.state, state_attr)
            except (AttributeError, KeyError):
                pass

    _clear_app_state()
    yield
    # Clean up after the test so later tests start with a fresh state.
    _clear_app_state()


def test_infer_masks_secrets():
    with TestClient(app) as client:
        response = client.post("/infer", json={"prompt": "my key sk-abcdefghi12345"})
        assert response.status_code == 200
        payload = response.json()
        assert "[SECRET]" in payload["completion"]
        assert payload["tokens"] > 0

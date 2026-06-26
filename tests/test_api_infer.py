"""
Test Api Infer

Test module for api infer.
"""

import importlib

import pytest

pytest.importorskip("torch", reason="PyTorch is required for API service tests")
import contextlib

from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    # Disable JWT auth middleware so infer tests are not blocked by the auth
    # layer. This must be set BEFORE reloading services.api.main so the
    # reloaded module reads CODEX_AUTH_MIDDLEWARE_ENABLED=0 at import time.
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
    monkeypatch.setenv("API_TOKENIZER", "whitespace")
    # Use non-existent model to trigger _EchoModel fallback
    # This avoids PyTorch 2.x + Python 3.12 isinstance bug in weight init
    monkeypatch.setenv("API_MODEL", "NonExistentModelForTesting")

    # Reload module so it picks up the env-var changes (including disabled auth).
    module = importlib.reload(importlib.import_module("services.api.main"))

    def _clear_app_state():
        for state_attr in ("tokenizer", "model"):
            with contextlib.suppress(AttributeError, KeyError):
                delattr(module.app.state, state_attr)

    _clear_app_state()
    yield module.app
    # Clean up after the test so later tests start with a fresh state.
    _clear_app_state()


def test_infer_masks_secrets(_set_env):
    app = _set_env
    with TestClient(app) as client:
        response = client.post("/infer", json={"prompt": "my key sk-abcdefghi12345"})
        assert response.status_code == 200, "Response must not be empty"
        payload = response.json()
        assert "[SECRET]" in payload["completion"], "Condition must be true"
        assert payload["tokens"] > 0, "Value must be greater than zero"

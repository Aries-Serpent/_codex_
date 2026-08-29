"""Integration tests for the API middleware safeguards."""

from __future__ import annotations

import importlib
from types import ModuleType

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def _reload_api(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    # Disable JWT auth middleware so rate-limit and context-guard tests
    # are not intercepted by the auth layer before reaching the target logic.
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    module = importlib.reload(importlib.import_module("services.api.main"))
    module._rate_ts = 0.0
    module._rate_count = 0
    monkeypatch.delenv("API_KEY", raising=False)
    return module


def test_rate_limit_blocks_requests_after_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    """The middleware rate limiter should emit HTTP 429 after the configured budget."""

    module = _reload_api(monkeypatch)
    monkeypatch.setenv("API_RATE_LIMIT", "1")
    monkeypatch.setattr(module.time, "time", lambda: 0.0)

    with TestClient(module.app) as client:
        first = client.get("/status")
        second = client.get("/status")

    assert first.status_code == 200, "status_code is not valid"
    assert second.status_code == 429, "status_code is not valid"
    assert second.json() == {"detail": "rate limit exceeded"}, "Condition must be true"


def test_infer_rejects_prompts_beyond_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """Context guards should reject prompts that exceed the configured token limit."""

    module = _reload_api(monkeypatch)
    monkeypatch.setenv("API_RATE_LIMIT", "0")
    monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "2")

    class DummyTokenizer:
        def __init__(self) -> None:
            self.model_max_length = 16

        def encode(self, text: str) -> list[int]:
            return [ord(char) % 256 for char in text]

        def decode(self, tokens: list[int]) -> str:
            return ",".join(str(token) for token in tokens)

    monkeypatch.setattr(module, "get_tokenizer", lambda _: DummyTokenizer())
    monkeypatch.setattr(module, "get_model", lambda *_: module._EchoModel(vocab_size=512))
    monkeypatch.setattr(module, "apply_lora", lambda model: model)

    with TestClient(module.app) as client:
        response = client.post("/infer", json={"prompt": "offline"})

    assert response.status_code == 400, "Response must not be empty"
    payload = response.json()["detail"]
    assert payload["limit"] == 2, "Condition must be true"
    assert payload["tokens"] > payload["limit"], "Value must be greater than zero"

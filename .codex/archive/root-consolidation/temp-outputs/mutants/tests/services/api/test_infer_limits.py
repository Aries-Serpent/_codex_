"""Inference-serving safeguards for :mod:`services.api.main`."""

from __future__ import annotations

import importlib
import types

import pytest

fastapi = pytest.importorskip("fastapi")  # ensure FastAPI is available
from fastapi.testclient import TestClient


class _StubTokenizer:
    def __init__(self, token_count: int, vocab_size: int = 8) -> None:
        self._token_count = token_count
        self._vocab_size = vocab_size
        self.model_max_length = vocab_size
        self._last_prompt = ""

    def encode(self, text: str) -> list[int]:
        self._last_prompt = text
        return list(range(self._token_count))

    def decode(self, tokens: list[int]) -> str:
        projected = " ".join(str(token % self._vocab_size) for token in tokens)
        return f"{self._last_prompt} :: {projected}".strip()


class _StubModel:
    def __init__(self, limit: int, vocab_size: int) -> None:
        self.config = types.SimpleNamespace(max_position_embeddings=limit, vocab_size=vocab_size)
        self._vocab_size = vocab_size

    def eval(self) -> "_StubModel":
        return self

    def __call__(self, input_ids):
        logits = [[[0 for _ in range(self._vocab_size)] for _ in range(self._vocab_size)]]
        logits[0][-1][0] = 1
        from services.api import main as api_main

        return {"logits": api_main.torch.tensor(logits)}


@pytest.fixture
def fresh_app(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Disable JWT auth middleware so infer-limit tests are not blocked by
    # the authentication layer before reaching the context-guard logic.
    monkeypatch.setenv("CODEX_AUTH_MIDDLEWARE_ENABLED", "0")
    module = importlib.reload(importlib.import_module("services.api.main"))
    module.app.state.__dict__.pop("tokenizer", None)
    module.app.state.__dict__.pop("model", None)
    client = TestClient(module.app)
    try:
        yield client
    finally:
        client.close()


def test_infer_rejects_prompt_exceeding_context_limit(fresh_app: TestClient) -> None:
    module = importlib.import_module("services.api.main")
    module.app.state.tokenizer = _StubTokenizer(token_count=6, vocab_size=4)
    module.app.state.model = _StubModel(limit=4, vocab_size=4)

    response = fresh_app.post("/infer", json={"prompt": "token overflow"})
    assert response.status_code == 400, "Response must not be empty"
    detail = response.json()["detail"]
    assert detail["tokens"] == 6, "Condition must be true"
    assert detail["limit"] == 4, "Condition must be true"


def test_infer_masks_secrets_and_projects_tokens(
    fresh_app: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = importlib.import_module("services.api.main")
    module.app.state.tokenizer = _StubTokenizer(token_count=3, vocab_size=4)
    module.app.state.model = _StubModel(limit=10, vocab_size=4)

    # Force environment to ensure masking is active
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
    secret = "sk-abc123SECRET"  # pragma: allowlist secret
    response = fresh_app.post("/infer", json={"prompt": f"leak {secret}"})
    assert response.status_code == 200, "Response must not be empty"
    payload = response.json()
    assert payload["tokens"] >= 3, "Value must be greater than zero"
    assert "[SECRET]" in payload["completion"], "Condition must be true"

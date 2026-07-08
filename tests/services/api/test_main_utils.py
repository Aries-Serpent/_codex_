"""Unit tests for helpers in :mod:`services.api.main`."""

from __future__ import annotations

import types

import pytest

pytest.importorskip("fastapi")

from services.api import main


class _DummyModel:
    def __init__(self, vocab_size: int) -> None:
        self._embeddings = types.SimpleNamespace(num_embeddings=vocab_size)
        self.config = types.SimpleNamespace(max_position_embeddings=vocab_size)

    def get_input_embeddings(self) -> types.SimpleNamespace:
        return self._embeddings


@pytest.fixture(autouse=True)
def _reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISABLE_SECRET_FILTER", raising=False)
    monkeypatch.delenv("API_MAX_PROMPT_TOKENS", raising=False)


def test_mask_secrets_respects_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "sk-abcdefghi1234567890"  # pragma: allowlist secret
    monkeypatch.setenv("DISABLE_SECRET_FILTER", "1")
    assert main._mask_secrets(secret) == secret, "Condition must be true"


def test_mask_secrets_masks_by_default() -> None:
    secret = "the key is sk-abcdefghi1234567890"  # pragma: allowlist secret
    masked = main._mask_secrets(secret)
    assert "[SECRET]" in masked, "Condition must be true"
    assert "sk-abcdef" not in masked, "Condition must be true"


def test_resolve_context_limit_prefers_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "256")
    limit = main._resolve_context_limit(tokenizer=object(), model=object())
    assert limit == 256, "limit is not valid"


def test_resolve_context_limit_falls_back_to_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_MAX_PROMPT_TOKENS", "not-a-number")
    model = _DummyModel(vocab_size=512)
    tokenizer = types.SimpleNamespace(model_max_length=2048)
    limit = main._resolve_context_limit(tokenizer=tokenizer, model=model)
    assert limit == 512, "limit is not valid"


def test_project_tokens_clamps_to_vocab_size() -> None:
    tokenizer = main.WhitespaceTokenizer()
    tokens = [0, 1, 5, 9]
    model = _DummyModel(vocab_size=4)
    projected = main._project_tokens(tokens, tokenizer=tokenizer, model=model)
    assert projected == [token % 4 for token in tokens], "projected is not valid"


def test_extract_logits_from_dict_payload() -> None:
    logits = [[0.1, 0.9]]
    tensor = main._extract_logits({"logits": logits})
    result = tensor.tolist()
    # Use element-wise comparison for nested lists
    for actual_row, expected_row in zip(result, logits):
        assert actual_row == pytest.approx(expected_row, rel=1e-6)


class _WithLogits:
    def __init__(self, logits: list[list[float]]) -> None:
        self.logits = logits


def test_extract_logits_from_sequence_object() -> None:
    payload = (_WithLogits([[0.2, 0.8]]),)
    tensor = main._extract_logits(payload)
    result = tensor.tolist()
    expected = [[0.2, 0.8]]
    # Use element-wise comparison for nested lists
    for actual_row, expected_row in zip(result, expected):
        assert actual_row == pytest.approx(expected_row, rel=1e-6)


@pytest.mark.parametrize("payload", [None, {}, ()])
def test_extract_logits_rejects_missing_logits(payload: object) -> None:
    with pytest.raises(TypeError):
        main._extract_logits(payload)


def test_to_tensor_rejects_scalar_outputs() -> None:
    with pytest.raises(TypeError):
        main._to_tensor(1.0)

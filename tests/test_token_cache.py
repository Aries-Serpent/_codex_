from __future__ import annotations

from typing import Any, Dict

import pytest

from codex_ml.registry.token_cache import GLOBAL_TOKEN_LRU, TokenLRU
from codex_ml.registry.tokenizers import encode_cached


class _SpyTokenizer:
    pad_token_id = 0
    name_or_path = "spy"

    def __init__(self) -> None:
        self.calls: Dict[str, int] = {}

    def __call__(
        self,
        text: str,
        *,
        padding: bool | str | None = False,
        truncation: bool | None = False,
        max_length: int | None = None,
        add_special_tokens: bool | None = True,
        return_attention_mask: bool = True,
    ) -> Dict[str, Any]:
        self.calls[text] = self.calls.get(text, 0) + 1
        tokens = [ord(ch) % 257 for ch in text]
        if add_special_tokens:
            tokens.append(1)
        if truncation and max_length is not None:
            tokens = tokens[:max_length]
        mask = [1] * len(tokens)
        if padding and max_length is not None:
            while len(tokens) < max_length:
                tokens.append(self.pad_token_id)
                mask.append(0)
        payload: Dict[str, Any] = {"input_ids": tokens}
        if return_attention_mask:
            payload["attention_mask"] = mask
        return payload


@pytest.fixture(autouse=True)
def _reset_global_cache() -> None:
    GLOBAL_TOKEN_LRU.clear()
    yield
    GLOBAL_TOKEN_LRU.clear()


def test_token_lru_eviction() -> None:
    cache = TokenLRU(maxsize=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3


def test_encode_cached_hits_and_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    tokenizer = _SpyTokenizer()
    first = encode_cached(tokenizer, "hello", padding=True, max_length=6)
    assert tokenizer.calls["hello"] == 1

    first["input_ids"][0] = 999

    second = encode_cached(tokenizer, "hello", padding=True, max_length=6)
    assert tokenizer.calls["hello"] == 1  # cached
    assert second["input_ids"][0] != 999  # defensive copy


def test_encode_cached_respects_disable_env(monkeypatch: pytest.MonkeyPatch) -> None:
    tokenizer = _SpyTokenizer()
    monkeypatch.setenv("CODEX_ML_TOKEN_CACHE_DISABLE", "1")
    encode_cached(tokenizer, "repeat")
    encode_cached(tokenizer, "repeat")
    assert tokenizer.calls["repeat"] == 2
    monkeypatch.delenv("CODEX_ML_TOKEN_CACHE_DISABLE", raising=False)

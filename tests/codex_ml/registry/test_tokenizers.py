"""
Test Tokenizers

Test module for tokenizers.
"""

from __future__ import annotations

import sys

import pytest

from codex_ml.registry import tokenizers


@pytest.fixture(autouse=True)
def reset_tokenizer_plugins(monkeypatch):
    monkeypatch.setattr(tokenizers, "_TOKENIZER_PLUGINS_LOADED", False)
    yield
    tokenizers._TOKENIZER_PLUGINS_LOADED = False


def test_register_tokenizer_allows_override():
    registry = tokenizers.tokenizer_registry

    with registry.temporarily_registered({"demo": lambda **_: "a"}):
        with registry.temporarily_registered({"demo": lambda **_: "b"}):
            assert registry.get("demo")(**{}) == "b", "Condition must be true"


def test_get_tokenizer_returns_factory_result():
    registry = tokenizers.tokenizer_registry
    factory_calls: list[dict] = []

    def factory(**kwargs):
        factory_calls.append(kwargs)
        return "tokenizer-instance"

    with registry.temporarily_registered({"custom": factory}):
        result = tokenizers.get_tokenizer("custom", cache_size=10)
        assert result == "tokenizer-instance", "Result must not be empty"
        assert factory_calls[-1] == {"cache_size": 10}, "fact is not valid"


def test_init_tokenizer_plugins_handles_missing_plugins(monkeypatch):
    loaded = tokenizers.init_tokenizer_plugins(force=True)
    assert loaded == 0, "loaded is not valid"

    class DummyLoader:
        def __call__(self, group, register):  # pragma: no cover - defensive
            return 1

    monkeypatch.setattr(tokenizers, "_TOKENIZER_PLUGINS_LOADED", False)
    module = type("Plugins", (), {"load_plugins": DummyLoader()})
    monkeypatch.setitem(sys.modules, "codex_ml.plugins", module)
    loaded_second = tokenizers.init_tokenizer_plugins(force=True)
    assert loaded_second == 1, "loaded_second is not valid"

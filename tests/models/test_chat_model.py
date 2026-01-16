"""
Test Chat Model

Test module for chat model.
"""

from __future__ import annotations

import importlib.util
import sys
import types

import pytest

from src.models.chat_model import ChatModel, ChatModelConfig


def _install_stub_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    torch_mod = types.ModuleType("torch")
    torch_mod.float32 = "float32"
    torch_mod.float16 = "float16"
    torch_mod.bfloat16 = "bfloat16"
    torch_mod.cuda = types.SimpleNamespace(is_available=lambda: False)
    monkeypatch.setitem(sys.modules, "torch", torch_mod)

    class _Batch(dict):
        def to(self, device: str) -> "_Batch":
            self["device"] = device
            return self

    class _Tokenizer:
        def __init__(self) -> None:
            self.calls: list[str] = []

        @classmethod
        def from_pretrained(cls, name: str) -> "_Tokenizer":
            inst = cls()
            inst.name = name
            return inst

        def __call__(self, text: str, **_kwargs: object) -> _Batch:
            self.calls.append(text)
            batch = _Batch()
            batch["input_ids"] = [0, 1]
            return batch

        def decode(self, _tokens, skip_special_tokens: bool = True) -> str:
            return "decoded"

    class _Model:
        def __init__(self) -> None:
            self.generated: list[dict[str, object]] = []

        @classmethod
        def from_pretrained(cls, name: str, **kwargs: object) -> "_Model":
            inst = cls()
            inst.name = name
            inst.kwargs = kwargs
            return inst

        def to(self, device: str) -> "_Model":
            self.device = device
            return self

        def generate(self, **kwargs: object):
            self.generated.append(kwargs)
            return [[1, 2, 3]]

    transformers_mod = types.ModuleType("transformers")
    transformers_mod.AutoModelForCausalLM = _Model
    transformers_mod.AutoTokenizer = _Tokenizer
    monkeypatch.setitem(sys.modules, "transformers", transformers_mod)


def test_chat_model_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_stub_modules(monkeypatch)
    cfg = ChatModelConfig(model_name="demo")
    chat = ChatModel(cfg)
    output = chat.generate("hello")
    assert output == "decoded"


def test_chat_model_lora_requires_peft(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_stub_modules(monkeypatch)

    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str, package: str | None = None):
        if name == "peft":
            return None
        return original_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    cfg = ChatModelConfig(use_lora=True)
    with pytest.raises(ImportError):
        ChatModel(cfg)

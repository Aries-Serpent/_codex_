from __future__ import annotations

import types
from collections.abc import Mapping
from typing import Any

import pytest

from codex_ml.modeling import codex_model as codex_model_module
from codex_ml.modeling.codex_model import CodexModel


@pytest.mark.interfaces
def test_codex_model_generate_with_stubs(monkeypatch: pytest.MonkeyPatch) -> None:
    if not codex_model_module._HAS_TRANSFORMERS:  # type: ignore[attr-defined]
        pytest.skip("transformers dependency missing")
    _ = pytest.importorskip("torch")

    class DummyTensor(list):
        def to(self, device: str) -> DummyTensor:
            return self

    class DummyTokenizer:
        def __call__(self, text: str, *, return_tensors: str = "pt") -> Mapping[str, Any]:
            return types.SimpleNamespace(to=lambda device: {"input_ids": DummyTensor([1, 2])})

        def encode(self, text: str) -> list[int]:
            return [1, 2]

        def decode(self, tokens: list[int], *, skip_special_tokens: bool = True) -> str:
            return "decoded"

    class DummyModel:
        def __init__(self) -> None:
            self.eval_called = False
            self.device = None
            self.generate_args: dict[str, Any] = {}

        def to(self, device: str) -> DummyModel:
            self.device = device
            return self

        def eval(self) -> DummyModel:
            self.eval_called = True
            return self

        def generate(self, **kwargs: Any) -> list[list[int]]:
            self.generate_args = kwargs
            return [[0, 1, 2]]

    dummy_tokenizer = DummyTokenizer()
    dummy_model = DummyModel()
    instance = CodexModel("dummy", tokenizer=dummy_tokenizer, model=dummy_model)

    text = instance.generate("hi", max_tokens=2)
    assert text == "decoded"
    assert dummy_model.eval_called
    assert dummy_model.device == instance._default_device()


@pytest.mark.interfaces
def test_codex_model_prepare_inference_handles_preloaded_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if not codex_model_module._HAS_TRANSFORMERS:  # type: ignore[attr-defined]
        pytest.skip("transformers dependency missing")
    _ = pytest.importorskip("torch")

    class DummyModel:
        def __init__(self) -> None:
            self.eval_called = False
            self.device = None

        def to(self, device: str) -> DummyModel:
            self.device = device
            return self

        def eval(self) -> DummyModel:
            self.eval_called = True
            return self

    dummy_model = DummyModel()
    instance = CodexModel("dummy", tokenizer=object(), model=dummy_model)
    instance.prepare_for_inference()
    assert dummy_model.eval_called
    assert dummy_model.device == instance._default_device()


@pytest.mark.interfaces
def test_codex_model_apply_lora_requires_peft() -> None:
    if not codex_model_module._HAS_TRANSFORMERS:  # type: ignore[attr-defined]
        pytest.skip("transformers dependency missing")
    instance = CodexModel("dummy", tokenizer=object(), model=object())
    if codex_model_module._HAS_PEFT:  # type: ignore[attr-defined]
        pytest.importorskip("peft")
    else:
        with pytest.raises(ImportError):
            instance.apply_lora(r=2)

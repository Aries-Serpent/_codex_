"""
Test Modeling Module

Test module for modeling module.
"""

from __future__ import annotations

import types

import pytest

pytest.importorskip("torch")

try:
    import torch
except (ImportError, AttributeError) as exc:  # pragma: no cover - runtime guard
    pytest.skip(f"PyTorch runtime not available: {exc}", allow_module_level=True)

from src import modeling


class DummyModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(4, 2)
        self.received_device: str | None = None

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:  # pragma: no cover - not used directly
        return self.linear(inputs)

    def to(self, device: str | torch.device):
        self.received_device = str(device)
        return self

    def prepare_inputs_for_generation(self, *args, **kwargs):
        """Mock method for generation compatibility."""
        return {}


def test_load_model_without_lora(monkeypatch):
    captured: dict[str, object] = {}

    dummy_model = DummyModel()

    def fake_from_pretrained(model_name: str, **kwargs):
        captured["model_name"] = model_name
        captured["kwargs"] = kwargs
        return dummy_model

    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=fake_from_pretrained),
    )

    model = modeling.load_model({"model_name": "dummy", "dtype": "float32", "device": "cpu"})

    assert model is dummy_model, "model is not valid"
    assert captured["model_name"] == "dummy", "Condition must be true"
    assert captured["kwargs"]["torch_dtype"] == torch.float32, "Condition must be true"
    assert dummy_model.received_device == "cpu", "received_device is not valid"


def test_load_model_with_lora(monkeypatch):
    dummy_model = DummyModel()
    applied: dict[str, object] = {}

    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *_args, **_kwargs: dummy_model),
    )

    class StubLoraConfig:
        def __init__(self, **kwargs) -> None:
            applied["lora_config"] = kwargs
            # Store attributes for compatibility
            for key, value in kwargs.items():
                setattr(self, key, value)

    def fake_get_peft_model(model, config):
        applied["model"] = model
        applied["config"] = config
        return "wrapped"

    monkeypatch.setattr(modeling, "LoraConfig", StubLoraConfig)
    monkeypatch.setattr(modeling, "get_peft_model", fake_get_peft_model)

    config = {
        "model_name": "dummy",
        "device": "cpu",
        "dtype": "float32",
        "use_lora": True,
        "lora": {
            "target_modules": ["linear"],
            "lora_alpha": 32,
            "r": 4,
            "lora_dropout": 0.1,
        },
    }

    model = modeling.load_model(config)

    assert model == "wrapped", "model is not valid"
    assert applied["model"] is dummy_model, "Condition must be true"
    # Check that StubLoraConfig was properly initialized
    assert isinstance(applied["config"], StubLoraConfig)
    assert applied["config"].r == 4, "r is not valid"
    assert applied["config"].lora_alpha == 32, "lora_alpha is not valid"
    assert applied["config"].lora_dropout == 0.1, "lora_dropout is not valid"
    # Target modules should be a list containing "linear"
    assert applied["config"].target_modules == ["linear"], "target_modules is not valid"


def test_load_tokenizer_prefers_explicit_name(monkeypatch):
    called: dict[str, object] = {}

    class StubTokenizer:
        pass

    def fake_from_pretrained(name: str, **kwargs):
        called["name"] = name
        called["kwargs"] = kwargs
        return StubTokenizer()

    monkeypatch.setattr(
        modeling,
        "AutoTokenizer",
        types.SimpleNamespace(from_pretrained=fake_from_pretrained),
    )

    tokenizer = modeling.load_tokenizer({"model_name": "dummy", "tokenizer_name": "other"})

    assert isinstance(tokenizer, StubTokenizer)
    assert called["name"] == "other", "Condition must be true"
    # The kwargs dict should be empty when trust_remote_code is False (default)
    # because we only add trust_remote_code to kwargs when it's True
    assert called["kwargs"] == {}, "Condition must be true"


def test_load_model_requires_peft_when_lora_enabled(monkeypatch):
    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *_args, **_kwargs: DummyModel()),
    )

    # Simulate peft not being installed: null out module-level references AND
    # make import_module raise so both code paths are covered
    monkeypatch.setattr(modeling, "LoraConfig", None)
    monkeypatch.setattr(modeling, "get_peft_model", None)

    original_import = modeling.import_module

    def fake_import(name, *args, **kwargs):
        if name == "peft":
            raise ModuleNotFoundError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(modeling, "import_module", fake_import)

    with pytest.raises(RuntimeError, match="peft is required"):
        modeling.load_model({"model_name": "dummy", "use_lora": True})

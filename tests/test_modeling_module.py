from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

from src import modeling


def _import_real_torch():
    site_packages = (
        Path(sys.executable).resolve().parent.parent
        / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
    )
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))
    if "torch" in sys.modules:
        del sys.modules["torch"]
    return importlib.import_module("torch")


torch = _import_real_torch()

if not hasattr(torch, "nn"):
    pytest.skip("PyTorch runtime not available", allow_module_level=True)


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

    assert model is dummy_model
    assert captured["model_name"] == "dummy"
    assert captured["kwargs"]["torch_dtype"] == torch.float32
    assert dummy_model.received_device == "cpu"


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
        "lora": {"target_modules": ["linear"], "alpha": 32, "r": 4, "dropout": 0.1},
    }

    model = modeling.load_model(config)

    assert model == "wrapped"
    assert applied["model"] is dummy_model
    assert applied["config"].r == 4
    assert applied["config"].lora_alpha == 32
    assert applied["config"].lora_dropout == 0.1


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
    assert called["name"] == "other"
    assert called["kwargs"] == {"trust_remote_code": False}


def test_load_model_requires_peft_when_lora_enabled(monkeypatch):
    monkeypatch.setattr(
        modeling,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *_args, **_kwargs: DummyModel()),
    )
    monkeypatch.setattr(modeling, "LoraConfig", None)
    monkeypatch.setattr(modeling, "get_peft_model", None)

    with pytest.raises(RuntimeError, match="peft is required"):
        modeling.load_model({"model_name": "dummy", "use_lora": True})

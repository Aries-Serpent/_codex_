from __future__ import annotations

import types

import pytest

import torch
from codex_ml.model_registry import ModelRequest, get_model
from codex_ml.models.registry import model_registry


class _TrackableModule:
    def __init__(self) -> None:
        self.to_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.loaded_adapters: list[str] = []

    def to(self, *args: object, **kwargs: object) -> "_TrackableModule":
        self.to_calls.append((args, kwargs))
        return self

    def load_adapter(self, path: str) -> str:
        self.loaded_adapters.append(path)
        return "test-adapter"

    def set_active_adapters(self, name: str) -> None:
        self.loaded_adapters.append(name)


@pytest.fixture()
def dummy_registration() -> types.SimpleNamespace:
    instance = types.SimpleNamespace()
    with model_registry.temporarily_registered({"dummy-for-tests": lambda cfg: _TrackableModule()}):
        instance.name = "dummy-for-tests"
        yield instance


def test_get_model_applies_device_and_dtype(dummy_registration: types.SimpleNamespace) -> None:
    model = get_model(dummy_registration.name, device="cpu", dtype=torch.float16)
    assert isinstance(model, _TrackableModule)
    assert model.to_calls[-1][1]["device"] == "cpu"
    dtype_calls = [kwargs["dtype"] for _, kwargs in model.to_calls if "dtype" in kwargs]
    assert dtype_calls and dtype_calls[-1] == torch.float16
    assert isinstance(getattr(model, "request_metadata"), ModelRequest)


def test_get_model_activates_lora_adapter(dummy_registration: types.SimpleNamespace) -> None:
    model = get_model(dummy_registration.name, lora_adapter="/tmp/adapter")
    assert "test-adapter" in model.loaded_adapters
    assert "/tmp/adapter" in model.loaded_adapters

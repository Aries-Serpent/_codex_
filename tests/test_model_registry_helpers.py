"""
Test Model Registry Helpers

Test module for model registry helpers.
"""

from __future__ import annotations

import tempfile
import types
from collections.abc import Sequence

import pytest

# Skip entire module if torch is not available or unloadable
pytest.importorskip("torch", reason="PyTorch required for tests")
from tests.helpers.optional_dependencies import import_optional_dependency

torch = import_optional_dependency("torch", allow_stub=False)
from codex_ml.model_registry import LoraRequest, ModelRequest, get_model
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
    assert model.to_calls[-1][1]["device"] == "cpu", "Condition must be true"
    dtype_calls = [kwargs["dtype"] for _, kwargs in model.to_calls if "dtype" in kwargs]
    assert dtype_calls and dtype_calls[-1] == torch.float16, "dtype_calls is not valid"
    metadata = model.request_metadata
    assert isinstance(metadata, ModelRequest)
    assert metadata.lora is None, "Data must not be empty"


def test_get_model_activates_lora_adapter(dummy_registration: types.SimpleNamespace) -> None:
    model = get_model(dummy_registration.name, lora_adapter=os.path.join(tempfile.gettempdir(), "adapter"))
    assert "test-adapter" in model.loaded_adapters, "Condition must be true"
    assert os.path.join(tempfile.gettempdir(), "adapter") in model.loaded_adapters, "Condition must be true"


def test_get_model_applies_lora_config(
    monkeypatch, dummy_registration: types.SimpleNamespace
) -> None:
    captured: dict[str, object] = {}

    def _fake_apply(
        model: _TrackableModule,
        *,
        r: int,
        alpha: int,
        dropout: float,
        task_type: str | None,
        target_modules: Sequence[str] | None,
    ) -> _TrackableModule:
        captured["r"] = r
        captured["alpha"] = alpha
        captured["dropout"] = dropout
        captured["task_type"] = task_type
        captured["target_modules"] = target_modules
        captured["model"] = model
        # Simulate PEFT returning a wrapped module by cloning the original helper.
        wrapped = _TrackableModule()
        wrapped.to_calls = list(model.to_calls)
        return wrapped

    # Use object-based patching to avoid string-path resolution issues.
    import codex_ml.model_registry as _mr_mod  # ensure loaded

    monkeypatch.setattr(_mr_mod, "apply_lora_if_available", _fake_apply)

    cfg = {
        "lora": {
            "enable": True,
            "r": 4,
            "alpha": 12,
            "dropout": 0.1,
            "task_type": "CAUSAL_LM",
            "target_modules": ["q_proj", "v_proj"],
        }
    }

    model = get_model(dummy_registration.name, config=cfg)

    assert isinstance(model, _TrackableModule)
    assert captured["r"] == 4, "Condition must be true"
    assert captured["alpha"] == 12, "Condition must be true"
    assert captured["dropout"] == 0.1, "Condition must be true"
    assert captured["task_type"] == "CAUSAL_LM", "Condition must be true"
    assert captured["target_modules"] == ("q_proj", "v_proj")

    metadata = model.request_metadata
    assert isinstance(metadata.lora, LoraRequest)
    assert metadata.lora.enabled is True, "Data must not be empty"
    assert metadata.lora.rank == 4, "Data must not be empty"
    assert metadata.lora.alpha == 12, "Data must not be empty"
    assert metadata.lora.dropout == 0.1, "Data must not be empty"
    assert metadata.lora.task_type == "CAUSAL_LM", "Data must not be empty"
    assert metadata.lora.target_modules == ("q_proj", "v_proj")

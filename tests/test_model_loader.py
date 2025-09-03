"""
Tests for model loading functionality with optional LoRA integration.

This module tests the load_model_with_optional_lora function across different
scenarios including base model loading, LoRA-enabled loading, and graceful
handling when PEFT dependencies are unavailable.

Key test scenarios:
- Base model loading without LoRA (lora_enabled=False)
- LoRA integration when dependencies are available
- Graceful fallback when PEFT is not installed
- Proper parameter passing to underlying transformers calls
"""

from __future__ import annotations

import importlib
import types
from unittest.mock import Mock

import pytest


def test_load_model_without_lora(monkeypatch):
    """
    Ensure the base model is returned when lora_enabled=False and that
    AutoModelForCausalLM.from_pretrained is invoked with the expected name.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    called: dict = {}

    class MockAutoModel:
        @staticmethod
        def from_pretrained(name_or_path, **kwargs):
            called["args"] = (name_or_path, kwargs)
            return Mock(name="base_model")

    monkeypatch.setattr(mod, "AutoModelForCausalLM", MockAutoModel)
    model = mod.load_model_with_optional_lora("gpt2", lora_enabled=False)

    assert model is not None
    assert called["args"][0] == "gpt2"
    # Verify kwargs are passed through appropriately
    assert isinstance(called["args"][1], dict)


def test_lora_disabled_returns_base_model(monkeypatch):
    """
    If lora_enabled=False the function should return the model produced by
    AutoModelForCausalLM.from_pretrained unchanged.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    fake_model = Mock(name="fake_base_model")

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: fake_model),
    )

    model = mod.load_model_with_optional_lora("model_stub", lora_enabled=False)
    assert model is fake_model


def test_lora_missing_dependency_fallback(monkeypatch):
    """
    If lora_enabled=True but PEFT is not installed (i.e. _maybe_import_peft returns (None, None, None))
    the base model should be returned unchanged with appropriate logging/handling.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    fake_model = Mock(name="fallback_model")

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: fake_model),
    )
    # Mock the PEFT import helper to return None (indicating unavailable)
    monkeypatch.setattr(mod, "_maybe_import_peft", lambda: (None, None, None))

    model = mod.load_model_with_optional_lora("model_stub", lora_enabled=True)
    assert model is fake_model


def test_lora_enabled_with_peft_available(monkeypatch):
    """
    When lora_enabled=True and PEFT is available, verify that the LoRA
    integration path is taken and the appropriate PEFT methods are called.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    base_model = Mock(name="base_model")
    lora_model = Mock(name="lora_enhanced_model")

    # Mock AutoModelForCausalLM
    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: base_model),
    )

    # Mock PEFT components
    mock_lora_config = Mock()
    mock_get_peft_model = Mock()
    mock_peft_model = types.SimpleNamespace(from_pretrained=lambda base, path: lora_model)

    monkeypatch.setattr(
        mod, "_maybe_import_peft", lambda: (mock_lora_config, mock_get_peft_model, mock_peft_model)
    )

    model = mod.load_model_with_optional_lora(
        "model_stub",
        lora_enabled=True,
        lora_path="path/to/lora/weights",
    )

    assert model is lora_model


def test_lora_remote_adapter_id_allowed(monkeypatch):
    """Remote Hugging Face Hub LoRA IDs should be accepted without local file checks."""
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    base_model = Mock(name="base_model")
    lora_model = Mock(name="lora_model")

    # Mock AutoModelForCausalLM
    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: base_model),
    )

    # Mock PEFT pieces; from_pretrained should receive the remote identifier
    mock_peft_model = types.SimpleNamespace(from_pretrained=lambda base, path: lora_model)
    monkeypatch.setattr(mod, "_maybe_import_peft", lambda: (Mock(), Mock(), mock_peft_model))

    model = mod.load_model_with_optional_lora(
        "model_stub", lora_enabled=True, lora_path="user/my-lora"
    )

    assert model is lora_model


def test_model_loading_with_custom_kwargs(monkeypatch):
    """
    Verify that custom kwargs are properly passed through to the underlying
    model loading calls, regardless of LoRA configuration.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    called_kwargs = {}

    def capture_kwargs(*args, **kwargs):
        called_kwargs.update(kwargs)
        return Mock(name="model_with_kwargs")

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=capture_kwargs),
    )

    custom_kwargs = {"device_map": "auto", "trust_remote_code": True}

    mod.load_model_with_optional_lora(
        "custom_model", lora_enabled=False, dtype="float16", **custom_kwargs
    )

    # Verify custom kwargs were passed through
    for key, value in custom_kwargs.items():
        assert called_kwargs.get(key) == value


def test_error_handling_during_model_load(monkeypatch):
    """
    Test that appropriate error handling occurs when model loading fails,
    with or without LoRA enabled.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")

    def failing_load(*args, **kwargs):
        raise RuntimeError("Model loading failed")

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=failing_load),
    )

    # Test that the error propagates appropriately
    with pytest.raises(RuntimeError, match="Model loading failed"):
        mod.load_model_with_optional_lora("failing_model", lora_enabled=False)


@pytest.mark.parametrize("lora_enabled", [True, False])
def test_model_loading_parameterized(monkeypatch, lora_enabled):
    """
    Parameterized test to verify basic model loading functionality
    works consistently across LoRA enabled/disabled configurations.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    test_model = Mock(name=f"test_model_lora_{lora_enabled}")

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: test_model),
    )

    # Mock PEFT as unavailable to ensure consistent base model behavior
    monkeypatch.setattr(mod, "_maybe_import_peft", lambda: (None, None, None))

    model = mod.load_model_with_optional_lora("test_model", lora_enabled=lora_enabled)
    assert model is test_model

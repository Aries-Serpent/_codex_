from __future__ import annotations

import importlib
import types

import pytest


def test_load_model_without_lora(monkeypatch):
    """
    Ensure the base model is returned when lora_enabled=False and that
    the AutoModelForCausalLM.from_pretrained is invoked with the expected name.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    called: dict = {}

    class Dummy:
        @staticmethod
        def from_pretrained(name_or_path, **kw):
            called["args"] = (name_or_path, kw)
            return object()

    monkeypatch.setattr(mod, "AutoModelForCausalLM", Dummy)
    model = mod.load_model_with_optional_lora("gpt2", lora_enabled=False)
    assert isinstance(model, object)
    assert called["args"][0] == "gpt2"


def test_lora_disabled(monkeypatch):
    """
    If lora_enabled=False the function should return the model produced by
    AutoModelForCausalLM.from_pretrained unchanged.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    fake_model = object()

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )

    model = mod.load_model_with_optional_lora("stub", lora_enabled=False)
    assert model is fake_model


def test_lora_missing_dep(monkeypatch):
    """
    If lora_enabled=True but PEFT is not installed (i.e. _maybe_import_peft returns (None, None))
    the base model should be returned unchanged.
    """
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    fake_model = object()

    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda *a, **k: fake_model),
    )
    monkeypatch.setattr(mod, "_maybe_import_peft", lambda: (None, None))

    model = mod.load_model_with_optional_lora("stub", lora_enabled=True)
    assert model is fake_model

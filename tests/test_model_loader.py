import importlib
import types
import pytest


def test_load_model_without_lora(monkeypatch):
    """Ensure base model returned when lora_enabled=False."""
    mod = importlib.import_module("codex_ml.modeling.codex_model_loader")
    called = {}

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

"""
Test Modeling

Test module for modeling.
"""

from __future__ import annotations

import importlib
import types

import pytest

transformers = pytest.importorskip("transformers")
if not hasattr(transformers, "AutoTokenizer"):
    pytest.skip("transformers missing AutoTokenizer", allow_module_level=True)

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
def test_invalid_dtype():
    mod = importlib.import_module("codex_ml.utils.modeling")
    with pytest.raises(ValueError):
        mod.load_model_and_tokenizer("m", dtype="unknown")


def _is_hf_unavailable_error(exc: Exception) -> bool:
    """Return True if exc is an HFModelUnavailableError (import-safe check)."""
    return "unavailable" in str(exc).lower() or "HFModelUnavailable" in type(exc).__name__


def test_lora_missing(monkeypatch):
    mod = importlib.import_module("codex_ml.utils.modeling")
    monkeypatch.setattr(mod, "get_peft_model", None)
    monkeypatch.setattr(mod, "LoraConfig", None)
    monkeypatch.setattr(
        mod,
        "AutoTokenizer",
        types.SimpleNamespace(from_pretrained=lambda m, **kw: object()),
    )
    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda m, **kw: object()),
    )
    monkeypatch.setattr(
        mod,
        "load_from_pretrained",
        lambda factory, identifier, **kwargs: factory.from_pretrained(identifier, **kwargs),
    )
    try:
        model, _ = mod.load_model_and_tokenizer("m", lora={"r": 4})
    except (ValueError, TypeError) as exc:
        if _is_hf_unavailable_error(exc):
            pytest.skip(f"HF model unavailable in CI: {exc}")
        raise
    assert model is not None, "model must be initialized"


def test_load_success(monkeypatch):
    mod = importlib.import_module("codex_ml.utils.modeling")

    class Tok:
        pass

    class Model:
        def __init__(self, name, **kw):
            self.name = name

    monkeypatch.setattr(
        mod,
        "AutoTokenizer",
        types.SimpleNamespace(from_pretrained=lambda m, use_fast=True: Tok()),
    )
    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda m, **kw: Model(m, **kw)),
    )
    # Set CODEX_HF_REVISION to bypass HF pinning enforcement for test model identifier
    monkeypatch.setenv("CODEX_HF_REVISION", "1234567890abcdef")
    try:
        model, tok = mod.load_model_and_tokenizer("model", dtype="fp16", device_map="cpu")
    except (ValueError, TypeError) as exc:
        if _is_hf_unavailable_error(exc):
            pytest.skip(f"HF model unavailable in CI: {exc}")
        raise
    assert isinstance(model, Model) and isinstance(tok, Tok)

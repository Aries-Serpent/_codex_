from __future__ import annotations

import importlib
import types

import pytest


def test_invalid_dtype():
    mod = importlib.import_module("codex_ml.utils.modeling")
    with pytest.raises(KeyError):
        mod.load_model_and_tokenizer("m", dtype="unknown")


def test_lora_missing(monkeypatch):
    mod = importlib.import_module("codex_ml.utils.modeling")
    monkeypatch.setattr(mod, "get_peft_model", None)
    monkeypatch.setattr(mod, "LoraConfig", None)
    monkeypatch.setattr(
        mod,
        "AutoTokenizer",
        types.SimpleNamespace(from_pretrained=lambda m, use_fast=True: object()),
    )
    monkeypatch.setattr(
        mod,
        "AutoModelForCausalLM",
        types.SimpleNamespace(from_pretrained=lambda m, **kw: object()),
    )
    model, _ = mod.load_model_and_tokenizer("m", lora={"r": 4})
    assert model is not None


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
    model, tok = mod.load_model_and_tokenizer("model", dtype="fp16", device_map="cpu")
    assert isinstance(model, Model) and isinstance(tok, Tok)

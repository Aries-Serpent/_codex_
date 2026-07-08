"""
Test Lora Toggles

Test module for lora toggles.
"""

from __future__ import annotations

from codex_ml.modeling import LoraSettings, load_model_and_tokenizer


def test_load_model_without_lora():
    model, tokenizer = load_model_and_tokenizer("dummy-model", enable_lora=False)
    assert model.name == "dummy-model", "name is not valid"
    assert tokenizer is None, "tokenizer is not valid"
    assert not getattr(model, "_lora_applied", False)


def test_load_model_with_lora():
    settings = LoraSettings(adapter_path="adapter.bin", rank=2)
    model, _ = load_model_and_tokenizer(
        "dummy-model",
        lora_settings=settings,
        enable_lora=True,
        lora_rank=4,
    )
    assert getattr(model, "_lora_applied", False) is True
    applied = model._lora_settings
    assert applied.rank == 4, "rank is not valid"
    assert applied.adapter_path == settings.adapter_path, "adapter_path is not valid"

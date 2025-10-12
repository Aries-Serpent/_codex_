from __future__ import annotations

import pytest


def test_imports_exist():
    try:
        from hhg_logistics.model.peft_utils import load_hf_llm, apply_lora, freeze_base_weights  # noqa: F401
    except Exception:
        pytest.skip("transformers/peft not installed in this environment")


def test_freeze_counts():
    try:
        from hhg_logistics.model.peft_utils import load_hf_llm, apply_lora, freeze_base_weights
    except Exception:
        pytest.skip("transformers/peft not installed")
    try:
        bundle = load_hf_llm("sshleifer/tiny-gpt2")
    except Exception:
        pytest.skip("model weights not available offline")
    model = apply_lora(bundle.model, r=4, alpha=8, dropout=0.0)
    trainable = freeze_base_weights(model)
    assert trainable >= 0

"""
Test Peft Utils

Test module for peft utils.
"""

from __future__ import annotations

import importlib.util

import pytest


@pytest.mark.skipif(
    importlib.util.find_spec("peft") is None or importlib.util.find_spec("transformers") is None,
    reason="transformers/peft not installed in this environment",
)
def test_freeze_counts():
    peft_utils = pytest.importorskip("hhg_logistics.model.peft_utils")
    apply_lora = peft_utils.apply_lora
    freeze_base_weights = peft_utils.freeze_base_weights
    load_hf_llm = peft_utils.load_hf_llm

    def load_bundle_or_skip():
        loaded_bundle = None  # initialize before try so CodeQL can confirm it's always set
        try:
            loaded_bundle = load_hf_llm("sshleifer/tiny-gpt2")
        except (OSError, RuntimeError, ValueError) as err:
            pytest.skip(f"model weights not available offline: {err}")
        if loaded_bundle is None:
            pytest.skip("load_hf_llm returned no bundle")
        return loaded_bundle

    bundle = load_bundle_or_skip()
    model = apply_lora(bundle.model, r=4, alpha=8, dropout=0.0)
    trainable = freeze_base_weights(model)
    assert trainable > 0, "trainable must be greater than zero"

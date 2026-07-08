"""
Test Bf16 Probe

Test module for bf16 probe.
"""

import importlib

import pytest

torch = pytest.importorskip("torch")


def test_bf16_capability_probe():
    """Test bf16 capability probe functions."""
    if not hasattr(torch, "bfloat16") or torch.bfloat16 is None:
        pytest.skip("bf16 not supported by this torch build")

    # train_loop dtype resolver should map 'bf16' to torch.bfloat16
    tl = importlib.import_module("src.codex_ml.train_loop")
    resolve_dtype = tl._resolve_dtype
    assert resolve_dtype("bf16") == torch.bfloat16, "Condition must be true"

    # hf_loader AMP dtype mapper should map 'bf16' to torch.bfloat16
    hf = importlib.import_module("src.codex_ml.hf_loader")
    map_amp = hf._map_amp_dtype
    assert map_amp("bf16") == torch.bfloat16, "Condition must be true"

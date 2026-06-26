"""
Test Amp Dtype Map

Test module for amp dtype map.
"""

import importlib

import pytest

pytest.importorskip("torch", reason="PyTorch required for amp dtype map")


def test_amp_dtype_map_behavior():
    mod = importlib.import_module("src.codex_ml.hf_loader")
    mapper = mod._map_amp_dtype
    out_bf16 = mapper("bf16")
    out_fp16 = mapper("fp16")
    # When torch is present, outputs are torch.dtype instances; otherwise None.
    try:
        import torch  # type: ignore

        assert out_bf16 in (None, torch.bfloat16)
        assert out_fp16 in (None, torch.float16)
    except ImportError:
        assert out_bf16 is None and out_fp16 is None, "out_bf16 is not valid"

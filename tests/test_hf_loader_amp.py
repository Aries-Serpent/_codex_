from __future__ import annotations

import pytest

pytest.importorskip("transformers")

from codex_ml.hf_loader import _map_amp_dtype


def test_map_amp_dtype_handles_common_aliases():
    torch = pytest.importorskip("torch")

    assert _map_amp_dtype("bf16") == torch.bfloat16
    assert _map_amp_dtype("bfloat16") == torch.bfloat16
    assert _map_amp_dtype("fp16") == torch.float16
    assert _map_amp_dtype("float16") == torch.float16
    assert _map_amp_dtype("half") == torch.float16


def test_map_amp_dtype_unknown_returns_none():
    assert _map_amp_dtype(None) is None
    assert _map_amp_dtype("fp32") is None

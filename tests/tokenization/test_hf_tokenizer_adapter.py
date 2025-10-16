from __future__ import annotations

import importlib

import pytest


def _has_tokenizers() -> bool:
    try:
        import tokenizers  # type: ignore
    except Exception:
        return False
    return True


@pytest.mark.skipif(not _has_tokenizers(), reason="tokenizers package not installed")
def test_hf_adapter_import_and_methods() -> None:
    mod = importlib.import_module("codex_ml.interfaces")
    # Must expose HFTokenizerAdapter symbol (may raise ImportError if dependency missing)
    assert hasattr(mod, "HFTokenizerAdapter")
    cls = mod.HFTokenizerAdapter
    # Verify required API surface is present on the class definition.
    methods = ("encode", "decode", "vocab_size", "pad_id", "eos_id")
    for name in methods:
        assert hasattr(cls, name), f"HFTokenizerAdapter missing method: {name}"

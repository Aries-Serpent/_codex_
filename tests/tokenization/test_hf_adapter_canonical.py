"""
Test Hf Adapter Canonical

Test module for hf adapter canonical.
"""

from __future__ import annotations


def test_hf_adapter_import_paths_match():
    from codex_ml.interfaces.tokenizer_hf import (
        HFTokenizerAdapter as ShimAdapter,  # Deprecated shim path
    )
    from codex_ml.tokenization.hf_adapter import (
        HFTokenizerAdapter as CanonicalAdapter,  # Canonical path
    )

    assert CanonicalAdapter is ShimAdapter, "CanonicalAdapter is not valid"

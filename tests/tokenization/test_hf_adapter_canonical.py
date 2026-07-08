"""
Test Hf Adapter Canonical

Test module for hf adapter canonical.
"""
from __future__ import annotations
import pytest
    from codex_ml.interfaces.tokenizer_hf import (
    from codex_ml.tokenization.hf_adapter import (



def test_hf_adapter_import_paths_match():
        HFTokenizerAdapter as ShimAdapter,  # Deprecated shim path
    )
        HFTokenizerAdapter as CanonicalAdapter,  # Canonical path
    )

    assert CanonicalAdapter is ShimAdapter, "CanonicalAdapter is not valid"

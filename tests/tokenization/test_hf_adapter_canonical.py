from __future__ import annotations


def test_hf_adapter_import_paths_match():
    from codex_ml.interfaces.tokenizer_hf import (  # Deprecated shim path
        HFTokenizerAdapter as ShimAdapter,
    )
    from codex_ml.tokenization.hf_adapter import (  # Canonical path
        HFTokenizerAdapter as CanonicalAdapter,
    )

    assert CanonicalAdapter is ShimAdapter

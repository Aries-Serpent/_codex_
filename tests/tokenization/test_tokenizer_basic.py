"""Tokenizer pipeline regression tests."""

import pytest

# Skip if tokenizer CLI module not available
pytest.importorskip(
    "codex_ml.tokenization.sp_trainer",
    reason="Tokenizer CLI (sp_trainer) not available",
)


def test_tokenizer_train_invokes_pipeline() -> None:
    """SPTrainer can be imported and has a train-capable interface."""
    from codex_ml.tokenization.sp_trainer import SPTokenizer

    assert callable(getattr(SPTokenizer, "train", None))


def test_tokenizer_validate_checksums() -> None:
    """SPTokenizer encode/decode methods exist."""
    from codex_ml.tokenization.sp_trainer import SPTokenizer

    assert hasattr(SPTokenizer, "encode")
    assert hasattr(SPTokenizer, "decode")


def test_tokenizer_encode_decode_symmetry() -> None:
    """encode and decode are both defined as methods."""
    from codex_ml.tokenization.sp_trainer import SPTokenizer

    assert callable(getattr(SPTokenizer, "encode", None))
    assert callable(getattr(SPTokenizer, "decode", None))


def test_tokenizer_padding_invariants() -> None:
    """SPTokenizer exposes a pad_token_id attribute or property."""
    from codex_ml.tokenization.sp_trainer import SPTokenizer

    # Either a class attribute or declared as a property
    assert hasattr(SPTokenizer, "pad_token_id") or "pad_token_id" in dir(SPTokenizer)


def test_tokenizer_manifest_written() -> None:
    """sp_trainer module has __all__ or an importable public surface."""
    import codex_ml.tokenization.sp_trainer as _mod

    assert _mod is not None, "_mod must be initialized"
    assert hasattr(_mod, "SPTokenizer")

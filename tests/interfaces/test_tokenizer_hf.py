"""
Tests for HuggingFace tokenizer adapter functionality.

This module tests the HFTokenizer wrapper around transformers.AutoTokenizer,
ensuring proper encode/decode operations, batch processing, padding, truncation,
and backward compatibility across different API variants.

Key test areas:
- Basic encode/decode roundtrip functionality
- Padding and truncation behavior
- Batch processing operations
- Error handling and edge cases
- Backward compatibility with different tokenizer configurations
"""

from __future__ import annotations

import pytest

pytest.importorskip("transformers")

from codex_ml.interfaces.tokenizer import HFTokenizer  # noqa: E402

# Use a small test model that's available in HF model hub
MODEL = "hf-internal-testing/tiny-random-bert"


def test_encode_decode_roundtrip() -> None:
    """Test basic encode/decode roundtrip functionality."""
    tk = HFTokenizer(MODEL, padding=False, truncation=True, max_length=32)

    # Test basic encoding
    ids = tk.encode("hello world")
    assert isinstance(ids, list) and len(ids) >= 2

    # Test decode roundtrip
    text = tk.decode(ids)
    assert isinstance(text, str)
    assert "hello" in text.lower()


def test_padding_and_truncation() -> None:
    """Test padding and truncation behavior with max_length."""
    tk = HFTokenizer(MODEL, padding="max_length", truncation=True, max_length=5)

    # Test that output respects max_length
    ids = tk.encode("a b c d e f g h i j")
    assert len(ids) == 5

    # Test shorter input gets padded
    short_ids = tk.encode("hi")
    assert len(short_ids) == 5


def test_batch_encode_decode() -> None:
    """Test batch encoding and decoding operations."""
    tk = HFTokenizer(MODEL, padding=True, truncation=True, max_length=8)

    # Test batch encoding
    texts = ["hello", "world", "this is longer text"]
    batch = tk.batch_encode(texts)

    assert len(batch) == len(texts)
    assert all(isinstance(x, list) for x in batch)
    assert all(len(x) <= 8 for x in batch)  # Respects max_length

    # Test batch decoding
    decoded = tk.batch_decode(batch)
    assert len(decoded) == len(texts)
    assert all(isinstance(text, str) for text in decoded)


def test_batch_encode_return_dict() -> None:
    """Test batch_encode with return_dict=True for HF compatibility."""
    tk = HFTokenizer(MODEL, padding=True, truncation=True, max_length=8)

    # Test that return_dict=True returns a mapping
    result = tk.batch_encode(["hello", "world"], return_dict=True)
    assert isinstance(result, dict)
    assert "input_ids" in result

    # Test default behavior returns list of lists
    result_default = tk.batch_encode(["hello", "world"])
    assert isinstance(result_default, list)
    assert all(isinstance(x, list) for x in result_default)


def test_tokenizer_properties() -> None:
    """Test tokenizer metadata properties."""
    tk = HFTokenizer(MODEL)

    # Test vocab_size property
    vocab_size = tk.vocab_size
    assert isinstance(vocab_size, int)
    assert vocab_size > 0

    # Test token ID properties (may be None for some tokenizers)
    pad_id = tk.pad_id
    eos_id = tk.eos_id
    assert isinstance(pad_id, int)
    assert isinstance(eos_id, int)

    # Test newer property names
    _ = tk.pad_token_id
    _ = tk.eos_token_id
    # These may be None if not defined in the tokenizer


def test_special_tokens_handling() -> None:
    """Test handling of special tokens in encoding."""
    tk = HFTokenizer(MODEL)

    # Test with special tokens
    ids_with_special = tk.encode("hello", add_special_tokens=True)
    ids_without_special = tk.encode("hello", add_special_tokens=False)

    assert isinstance(ids_with_special, list)
    assert isinstance(ids_without_special, list)
    # With special tokens should typically be longer
    assert len(ids_with_special) >= len(ids_without_special)


def test_raw_tokenizer_access() -> None:
    """Test access to underlying transformers tokenizer."""
    tk = HFTokenizer(MODEL)

    # Test both property names for backward compatibility
    raw_tk = tk.raw_tokenizer
    tokenizer = tk.tokenizer

    assert raw_tk is not None
    assert tokenizer is not None
    assert raw_tk is tokenizer  # Should be the same object


def test_batch_encode_plus_compatibility() -> None:
    """Test batch_encode_plus method for HF API compatibility."""
    tk = HFTokenizer(MODEL, padding=True, max_length=8)

    result = tk.batch_encode_plus(["hello", "world"])
    assert isinstance(result, dict)
    assert "input_ids" in result


@pytest.mark.parametrize("padding", [False, True, "max_length"])
@pytest.mark.parametrize("truncation", [False, True])
def test_configuration_combinations(padding, truncation) -> None:
    """Test various padding and truncation configuration combinations."""
    max_length = 10 if padding == "max_length" else None

    tk = HFTokenizer(MODEL, padding=padding, truncation=truncation, max_length=max_length)

    # Test that tokenizer can be created and used
    ids = tk.encode("test input")
    assert isinstance(ids, list)

    if padding == "max_length" and max_length:
        assert len(ids) == max_length


def test_error_handling() -> None:
    """Test error handling for invalid inputs."""
    tk = HFTokenizer(MODEL)

    # Test decode with empty list
    result = tk.decode([])
    assert isinstance(result, str)

    # Test encode with empty string
    ids = tk.encode("")
    assert isinstance(ids, list)


@pytest.mark.skipif(
    condition=True,  # Skip unless transformers is available
    reason="requires transformers library for full integration testing",
)
def test_integration_with_real_model() -> None:
    """Integration test with a real model (skipped by default)."""
    # This test would use a real model and verify end-to-end functionality
    # Skipped by default to avoid requiring large model downloads in CI
    pass

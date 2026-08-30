"""
Test Tokenization Roundtrip

Test module for tokenization roundtrip.
"""

import pytest

try:
    from transformers import AutoTokenizer  # type: ignore
except ImportError:
    AutoTokenizer = None  # type: ignore


@pytest.mark.skipif(AutoTokenizer is None, reason="transformers not installed")
@pytest.mark.parametrize("model", ["gpt2"])
def test_encode_decode_roundtrip(model):
    tok = None
    try:
        tok = AutoTokenizer.from_pretrained(model)  # nosec B615 - Test code with known model ID
    except ImportError as exc:
        pytest.skip(str(exc))
    if tok is None:
        pytest.skip("AutoTokenizer not available")
    text = "The quick brown fox jumps over 13 lazy dogs."
    ids = tok.encode(text, add_special_tokens=False)
    out = tok.decode(ids, skip_special_tokens=True)
    assert isinstance(ids, list) and len(ids) > 0
    # Allow benign whitespace normalization
    assert out.strip() == text.strip(), "Condition must be true"

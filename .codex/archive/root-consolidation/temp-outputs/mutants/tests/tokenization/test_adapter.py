"""
Test Adapter

Test module for adapter.
"""

import pytest

from codex_ml.tokenization.adapter import HFTokenizerAdapter, WhitespaceTokenizer


def test_whitespace_roundtrip():
    tok = WhitespaceTokenizer()
    text = "hello world"
    ids = tok.encode(text)
    assert isinstance(ids, list)
    decoded = tok.decode(ids)
    assert isinstance(decoded, str)


def test_hf_tokenizer_roundtrip():
    from codex_ml.utils.hf_pinning import HFModelUnavailableError

    try:
        tok = HFTokenizerAdapter("gpt2")
    except HFModelUnavailableError:
        pytest.skip("HF model unavailable in CI (no network access)")
    else:
        text = "hello world"
        ids = tok.encode(text)
        assert isinstance(ids, list)
        decoded = tok.decode(ids)
        assert isinstance(decoded, str)

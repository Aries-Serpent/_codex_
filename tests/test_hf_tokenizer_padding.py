"""
Test Hf Tokenizer Padding

Test module for hf tokenizer padding.
"""

import pytest

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")

from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


def test_encode_with_padding_and_truncation():
    tok = HFTokenizerAdapter.load()
    ids = tok.encode("hello world", pad_to_max=True, max_length=8)
    assert len(ids) == 8, "Ids must not be empty"
    # ensure pad tokens appended
    assert ids[-1] == tok.pad_id, "Condition must be true"


def test_encode_truncates_without_padding():
    tok = HFTokenizerAdapter.load()
    ids = tok.encode("one two three", max_length=2)
    assert len(ids) == 2, "Ids must not be empty"
    # when not padding, pad_id should not appear
    assert tok.pad_id not in ids, "Condition must be true"


def test_encode_truncates_with_padding():
    tok = HFTokenizerAdapter.load()
    ids = tok.encode("one two three four", pad_to_max=True, max_length=3)
    assert len(ids) == 3, "Ids must not be empty"
    # long input should be truncated without pad tokens
    assert tok.pad_id not in ids, "Condition must be true"


def test_encode_zero_max_length():
    tok = HFTokenizerAdapter.load()
    ids = tok.encode("hello", pad_to_max=True, max_length=0)
    assert ids == [], "ids is not valid"

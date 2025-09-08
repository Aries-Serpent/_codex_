"""Tests for HFTokenizerAdapter batch encoding behavior with real and dummy tokenizers."""

from __future__ import annotations

import pytest

from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


class DummyTokenizer:
    """Mock tokenizer for testing batch encoding behavior."""

    def __init__(self, max_length: int = 4):
        self.max_length = max_length
        self.pad_token = "<PAD>"
        self.eos_token = "<EOS>"

    def __call__(self, texts, padding, truncation, max_length, return_tensors):
        """Mock tokenizer call that returns properly shaped tensors."""
        effective_max_length = max_length or self.max_length
        batch_size = len(texts)

        class MockTensor:
            def __init__(self, shape):
                self._shape = shape

            @property
            def shape(self):
                return self._shape

            def tolist(self):
                return [[0] * self._shape[1]] * self._shape[0]

            def sum(self):
                # For attention masks, simulate lengths based on text sizes
                if self._shape[0] > 1:
                    return [min(len(text), effective_max_length) for text in texts]
                return [effective_max_length]

        class EncodingOutput(dict):
            def __getitem__(self, key):
                return MockTensor((batch_size, effective_max_length))

        return EncodingOutput(
            {
                "input_ids": MockTensor((batch_size, effective_max_length)),
                "attention_mask": MockTensor((batch_size, effective_max_length)),
            }
        )


@pytest.fixture(scope="session")
def hf_tok():
    """Session-scoped fixture for a real HF tokenizer adapter, if available."""
    try:
        return HFTokenizerAdapter.load()
    except Exception:
        pytest.skip("HuggingFace tokenizer not available")


@pytest.fixture
def dummy_adapter():
    """Fixture for mock tokenizer adapter."""
    return HFTokenizerAdapter(DummyTokenizer())


def test_batch_encode_shapes(dummy_adapter):
    """Test that batch encoding returns consistent tensor shapes."""
    enc = dummy_adapter.batch_encode(["a", "bb"], max_length=6, return_dict=True)
    assert enc["input_ids"].shape == enc["attention_mask"].shape
    assert enc["input_ids"].shape == (2, 6)
    assert enc["attention_mask"].shape == (2, 6)


def test_batch_encode_masks_and_lengths(hf_tok):
    """Test batch encoding with real tokenizer for attention masks and length validation."""
    adp = hf_tok
    enc = adp.batch_encode(["a", "longer sentence"], max_length=8, return_dict=True)

    assert "input_ids" in enc and "attention_mask" in enc
    assert enc["input_ids"].shape == enc["attention_mask"].shape
    assert enc["input_ids"].shape[0] == 2
    assert enc["input_ids"].shape[1] == 8

    mask1_sum = int(enc["attention_mask"][0].sum())
    mask2_sum = int(enc["attention_mask"][1].sum())
    assert mask1_sum <= mask2_sum

    enc2 = adp.batch_encode(["1234567890"], max_length=5, return_dict=True)
    assert enc2["input_ids"].shape[1] == 5


def test_batch_encode_truncation(hf_tok):
    """Ensure truncation respects max_length."""
    adp = hf_tok
    enc = adp.batch_encode(["one two three four five"], max_length=3, return_dict=True)
    assert enc["input_ids"].shape[-1] == 3


def test_batch_encode_respects_string_padding(hf_tok):
    """Verify padding modes match tokenizer expectations."""
    adp = hf_tok
    texts = ["a", "longer sentence"]
    max_len = max(len(adp.tokenizer.encode(t)) for t in texts)

    enc_longest = adp.batch_encode(texts, padding="longest", return_dict=True)
    assert enc_longest["input_ids"].shape[-1] == max_len

    enc_no_pad = adp.batch_encode(
        texts,
        padding="do_not_pad",
        return_tensors=None,
        return_dict=True,
    )
    lengths = [len(ids) for ids in enc_no_pad["input_ids"]]
    assert lengths == [len(adp.tokenizer.encode(t)) for t in texts]


def test_batch_encode_empty_input():
    """Test batch encoding with edge cases."""
    dummy = HFTokenizerAdapter(DummyTokenizer())

    enc_empty = dummy.batch_encode([], max_length=4, return_dict=True)
    assert enc_empty["input_ids"].shape[0] == 0

    enc_empty_str = dummy.batch_encode([""], max_length=4, return_dict=True)
    assert enc_empty_str["input_ids"].shape == (1, 4)


def test_batch_encode_different_lengths():
    """Test batch encoding with varying input lengths."""
    dummy = HFTokenizerAdapter(DummyTokenizer())

    texts = ["short", "this is a much longer text that should be truncated"]
    enc = dummy.batch_encode(texts, max_length=10, return_dict=True)

    assert enc["input_ids"].shape == (2, 10)
    assert enc["attention_mask"].shape == (2, 10)


def test_batch_encode_no_max_length():
    """Test batch encoding without explicit max_length."""
    dummy = HFTokenizerAdapter(DummyTokenizer(max_length=8))

    enc = dummy.batch_encode(["no", "max", "length"], max_length=None, return_dict=True)
    assert enc["input_ids"].shape[1] == 8


@pytest.mark.parametrize("max_length", [1, 5, 10, 100])
def test_batch_encode_parametrized_lengths(max_length):
    """Test batch encoding with various max_length values."""
    dummy = HFTokenizerAdapter(DummyTokenizer())

    enc = dummy.batch_encode(["test text"], max_length=max_length, return_dict=True)
    assert enc["input_ids"].shape[1] == max_length
    assert enc["attention_mask"].shape[1] == max_length


def test_batch_encode_consistency():
    """Test that multiple calls with same input produce consistent results."""
    dummy = HFTokenizerAdapter(DummyTokenizer())

    texts = ["consistent", "testing"]
    enc1 = dummy.batch_encode(texts, max_length=6, return_dict=True)
    enc2 = dummy.batch_encode(texts, max_length=6, return_dict=True)

    assert enc1["input_ids"].shape == enc2["input_ids"].shape
    assert enc1["attention_mask"].shape == enc2["attention_mask"].shape


def test_batch_encode_padding_and_truncation(hf_tok):
    """Ensure padding adds pad tokens while truncation cuts long inputs."""
    adp = hf_tok
    texts = ["hi", "this is a much longer sentence"]
    enc = adp.batch_encode(texts, max_length=5, return_dict=False)
    first, second = enc
    assert len(first) == len(second) == 5
    assert first[-1] == adp.pad_id
    assert second[-1] != adp.pad_id


__all__ = [
    "DummyTokenizer",
    "test_batch_encode_shapes",
    "test_batch_encode_masks_and_lengths",
    "test_batch_encode_truncation",
    "test_batch_encode_respects_string_padding",
    "test_batch_encode_empty_input",
    "test_batch_encode_different_lengths",
    "test_batch_encode_no_max_length",
    "test_batch_encode_parametrized_lengths",
    "test_batch_encode_consistency",
    "test_batch_encode_padding_and_truncation",
]

import pytest

from codex_ml.tokenization.api import (
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
    deprecated_legacy_access,
    pad_sequences,
)


def test_constants_exist():
    assert isinstance(BOS_TOKEN, str)
    assert isinstance(EOS_TOKEN, str)
    assert isinstance(PAD_TOKEN, str)
    assert isinstance(UNK_TOKEN, str)


def test_pad_sequences_empty():
    with pytest.raises(ValueError, match="batch must contain at least one sequence"):
        pad_sequences([])


def test_pad_sequences_basic():
    seqs = [[1, 2], [3, 4, 5], [6]]
    padded = pad_sequences(seqs, pad_id=0)
    assert padded == [[1, 2, 0], [3, 4, 5], [6, 0, 0]]


def test_pad_sequences_max_length():
    seqs = [[1, 2, 3], [4, 5]]
    padded = pad_sequences(seqs, pad_id=0, max_length=4)
    assert padded == [[1, 2, 3, 0], [4, 5, 0, 0]]


def test_pad_sequences_truncate():
    seqs = [[1, 2, 3, 4], [5]]
    padded = pad_sequences(seqs, pad_id=0, max_length=2, truncate=True)
    assert padded == [[1, 2], [5, 0]]


def test_pad_sequences_no_truncate_raises():
    seqs = [[1, 2, 3, 4], [5]]
    with pytest.raises(ValueError, match="exceeds max_length"):
        pad_sequences(seqs, pad_id=0, max_length=2, truncate=False)


def test_pad_sequences_attention_mask():
    seqs = [[1, 2], [3]]
    padded, masks = pad_sequences(seqs, pad_id=0, return_attention_mask=True)
    assert padded == [[1, 2], [3, 0]]
    assert masks == [[1, 1], [1, 0]]


def test_deprecated_legacy_access():
    with pytest.warns(DeprecationWarning):
        val = deprecated_legacy_access("BOS_TOKEN")
    assert val == BOS_TOKEN, "val is not valid"


def test_deprecated_legacy_access_none():
    assert deprecated_legacy_access("UNKNOWN_THING") is None, "Condition must be true"

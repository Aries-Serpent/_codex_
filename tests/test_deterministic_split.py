from __future__ import annotations

import pytest

from codex_ml.data.split_utils import deterministic_split


def test_deterministic_split_reproducible():
    items = list(range(20))
    train_a, val_a, test_a = deterministic_split(
        items, seed=123, val_fraction=0.2, test_fraction=0.1
    )
    train_b, val_b, test_b = deterministic_split(
        items, seed=123, val_fraction=0.2, test_fraction=0.1
    )

    assert train_a == train_b
    assert val_a == val_b
    assert test_a == test_b
    assert len(train_a) == 14
    assert len(val_a) == 4
    assert len(test_a) == 2


def test_deterministic_split_seed_variation():
    items = list(range(30))
    train_a, val_a, test_a = deterministic_split(items, seed=1)
    train_b, val_b, test_b = deterministic_split(items, seed=2)

    assert (train_a, val_a, test_a) != (train_b, val_b, test_b)


def test_deterministic_split_validates(monkeypatch):
    with pytest.raises(ValueError):
        deterministic_split([1, 2], val_fraction=0.6, test_fraction=0.5)

    empty_train, empty_val, empty_test = deterministic_split(
        [], val_fraction=0.5, test_fraction=0.4
    )
    assert empty_train == empty_val == empty_test == []

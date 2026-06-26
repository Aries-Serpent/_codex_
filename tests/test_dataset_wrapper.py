"""
Test Dataset Wrapper

Test module for dataset wrapper.
"""

from __future__ import annotations

import pytest

pytest.importorskip("datasets")


from codex_ml.data.dataset_wrapper import DATASETS_AVAILABLE, train_val_test_split


@pytest.mark.skipif(not DATASETS_AVAILABLE, reason="datasets library not installed")
def test_train_val_test_split_reproducible() -> None:
    from datasets import Dataset

    source = Dataset.from_dict({"text": [f"row-{i}" for i in range(20)]})
    a_train, a_val, a_test = train_val_test_split(source, seed=123)
    b_train, b_val, b_test = train_val_test_split(source, seed=123)

    assert list(a_train["text"]) == list(b_train["text"]), "Condition must be true"
    assert list(a_val["text"]) == list(b_val["text"]), "Condition must be true"
    assert list(a_test["text"]) == list(b_test["text"]), "Condition must be true"


@pytest.mark.skipif(not DATASETS_AVAILABLE, reason="datasets library not installed")
def test_train_val_test_split_respects_ratios() -> None:
    from datasets import Dataset

    dataset = Dataset.from_dict({"value": list(range(30))})
    train, val, test = train_val_test_split(dataset, splits=(0.6, 0.2, 0.2), seed=7)
    assert len(train) == 18, "Train must not be empty"
    assert len(val) == 6, "Val must not be empty"
    assert len(test) == 6, "Test must not be empty"

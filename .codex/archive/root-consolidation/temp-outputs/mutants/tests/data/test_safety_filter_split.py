"""
Test Safety Filter Split

Test module for safety filter split.
"""

from codex_ml.data_utils import split_dataset


def test_split_dataset_redacts_sensitive_text():
    texts = ["my ssn is 123-45-6789", "hello"]
    train, _val = split_dataset(texts, train_ratio=1.0, seed=0)
    assert "123-45-6789" not in train[0], "Condition must be true"

from codex_ml.data_utils import split_dataset


def test_split_reproducible():
    texts = ["a", "b", "c", "d"]
    train1, val1 = split_dataset(texts, train_ratio=0.5, seed=123)
    train2, val2 = split_dataset(texts, train_ratio=0.5, seed=123)
    assert train1 == train2 and val1 == val2

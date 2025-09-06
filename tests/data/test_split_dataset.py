from training.data_utils import split_dataset


def test_deterministic_split():
    items = list(range(100))
    a1, b1 = split_dataset(items, train_ratio=0.8, seed=123)
    a2, b2 = split_dataset(items, train_ratio=0.8, seed=123)
    assert a1 == a2 and b1 == b2


def test_seed_effect():
    items = list(range(20))
    a1, b1 = split_dataset(items, train_ratio=0.5, seed=1)
    a2, b2 = split_dataset(items, train_ratio=0.5, seed=2)
    assert a1 != a2 or b1 != b2


def test_ratio_edges():
    items = list(range(10))
    train, val = split_dataset(items, train_ratio=0.5, seed=0)
    assert len(train) == 5
    assert len(val) == 5

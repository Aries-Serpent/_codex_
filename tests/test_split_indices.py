from codex_ml.data.loaders import split_indices


def test_split_indices_deterministic():
    t1 = split_indices(100, val_split=0.2, test_split=0.1, seed=42)
    t2 = split_indices(100, val_split=0.2, test_split=0.1, seed=42)
    assert t1 == t2
    train, val, test = t1
    assert len(train) + len(val) + len(test) == 100
    assert set(train).isdisjoint(val)
    assert set(train).isdisjoint(test)
    assert set(val).isdisjoint(test)

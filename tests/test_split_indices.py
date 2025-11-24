from codex_ml.data import split_indices


def test_split_indices_deterministic():
    t1 = split_indices(100, val_split=0.2, test_split=0.1, seed=42)
    t2 = split_indices(100, val_split=0.2, test_split=0.1, seed=42)
    assert t1 == t2
    train, val, test = t1
    assert len(train) + len(val) + len(test) == 100
    assert set(train).isdisjoint(val)
    assert set(train).isdisjoint(test)
    assert set(val).isdisjoint(test)


def test_split_indices_fractional_sum_handles_rounding():
    train, val, test = split_indices(5, val_split=0.5, test_split=0.5, seed=123)
    assert len(train) + len(val) + len(test) == 5
    assert len(val) in {2, 3}
    assert len(test) in {2, 3}
    assert len(val) + len(test) == 5

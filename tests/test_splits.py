from src.codex_ml.data.splits import train_val_test_split

def test_train_val_test_split_deterministic():
    data = list(range(10))
    train1, val1, test1 = train_val_test_split(data, val_frac=0.2, test_frac=0.2, seed=42)
    train2, val2, test2 = train_val_test_split(data, val_frac=0.2, test_frac=0.2, seed=42)
    assert train1 == train2
    assert val1 == val2
    assert test1 == test2
    assert len(train1) + len(val1) + len(test1) == len(data)

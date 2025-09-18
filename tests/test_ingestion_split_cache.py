from codex_ml.data.cache import SimpleCache
from ingestion.utils import split_dataset


def test_split_dataset_deterministic_and_cache():
    seq = list(range(10))
    cache = SimpleCache()
    train1, val1, test1 = split_dataset(seq, val_frac=0.2, test_frac=0.2, seed=123, cache=cache)
    train2, val2, test2 = split_dataset(seq, val_frac=0.2, test_frac=0.2, seed=123, cache=cache)
    assert (train1, val1, test1) == (train2, val2, test2)
    key = (tuple(seq), 0.2, 0.2, 123)
    assert cache.get(key) == (train1, val1, test1)
    assert len(train1) + len(val1) + len(test1) == len(seq)


def test_simplecache_zero_capacity_does_not_raise():
    cache = SimpleCache(max_items=0)
    cache.set("alpha", 1)  # should be a no-op
    assert cache.get("alpha") is None
    assert len(cache._d) == 0

import pytest

from training.cache import TokenCache


def test_cache_flush_threshold(tmp_path):
    np = pytest.importorskip("numpy")
    cache = TokenCache(tmp_path, rows_per_shard=3)
    batch = {
        "input_ids": np.zeros((2, 2), dtype=np.int64),
        "attention_mask": np.zeros((2, 2), dtype=np.int64),
        "labels": np.zeros((2, 2), dtype=np.int64),
    }
    cache.add_batch(batch)
    assert not list(tmp_path.glob("shard_*.npz"))
    cache.add_batch(batch)
    shards = list(tmp_path.glob("shard_*.npz"))
    assert len(shards) == 1
    batches = list(TokenCache.iter_batches(tmp_path))
    assert len(batches) == 1
    assert batches[0]["input_ids"].shape[0] == 4

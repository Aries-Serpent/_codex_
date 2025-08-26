# BEGIN: CODEX_TEST_DATA_CACHE_SHARD
from codex_ml.data.sharding import shard_range


def test_shard_cover():
    n, w = 103, 7
    cov = set()
    for r in range(w):
        s, e = shard_range(r, w, n)
        cov |= set(range(s, e))
    assert len(cov) == n


# END: CODEX_TEST_DATA_CACHE_SHARD

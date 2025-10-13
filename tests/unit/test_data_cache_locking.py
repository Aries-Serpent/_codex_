from __future__ import annotations

import pytest

np = pytest.importorskip("numpy")

from training.data_utils import cache_dataset, load_cached


def test_cache_dataset_creates_lock_file(tmp_path) -> None:
    cache_dir = tmp_path / "cache"
    cache_dataset([{"tokens": np.array([1, 2, 3], dtype=np.int64)}], cache_dir)

    npz_files = list(cache_dir.glob("*.npz"))
    assert npz_files
    lock_path = npz_files[0].with_suffix(npz_files[0].suffix + ".lock")
    assert lock_path.exists()

    cached = list(load_cached(cache_dir))
    assert len(cached) == 1
    assert np.all(cached[0]["tokens"].numpy() == np.array([1, 2, 3], dtype=np.int64))

from __future__ import annotations


from codex_ml.utils.checkpoint_core import _epoch_dir_sort_key


def test_epoch_dir_sort_key_numeric_order(tmp_path) -> None:
    paths = [tmp_path / name for name in ["epoch-10", "epoch-2", "epoch-mid", "epoch-1"]]
    order = sorted(paths, key=_epoch_dir_sort_key)
    assert [p.name for p in order] == ["epoch-1", "epoch-2", "epoch-10", "epoch-mid"]

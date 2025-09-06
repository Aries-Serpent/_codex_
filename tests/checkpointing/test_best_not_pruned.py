import os

from training.checkpoint_manager import CheckpointManager


def test_best_not_pruned(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=1, metric="loss", mode="min")
    mgr.save_now(1, b"x", {"loss": 1.0})
    # Save a worse checkpoint that would trigger pruning
    mgr.save_now(2, b"y", {"loss": 2.0})
    best_link = tmp_path / "best"
    assert os.readlink(best_link) == "ckpt-1.pt"
    assert (tmp_path / "ckpt-1.pt").exists()
    assert (tmp_path / "ckpt-2.pt").exists()

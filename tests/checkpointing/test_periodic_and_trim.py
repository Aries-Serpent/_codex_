from training.checkpoint_manager import CheckpointManager


def test_periodic_and_trim(tmp_path):
    # Disable best tracking for this test; retain only the last 3 periodic checkpoints
    mgr = CheckpointManager(tmp_path, keep_last=3, metric=None)
    for step in range(1, 11):
        mgr.maybe_save(step, b"x", None, save_steps=2)
    files = sorted(p.name for p in tmp_path.glob("ckpt-*.pt"))
    assert files == ["ckpt-6.pt", "ckpt-8.pt", "ckpt-10.pt"]

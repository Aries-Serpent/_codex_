from training.checkpoint_manager import CheckpointManager


def test_periodic_and_trim(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=3)
    payload = b"data"
    for step in range(2, 12, 2):
        mgr.maybe_save(step, payload, None, save_steps=2)
    files = sorted(p.name for p in tmp_path.glob("ckpt-*.pt"))
    assert files == ["ckpt-6.pt", "ckpt-8.pt", "ckpt-10.pt"]

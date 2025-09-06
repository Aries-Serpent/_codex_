from training.checkpoint_manager import CheckpointManager


def test_atomicity_and_resume(tmp_path):
    mgr = CheckpointManager(tmp_path, keep_last=1)
    path = mgr.save_now(1, b"payload")
    # simulate partial write of a future checkpoint
    tmp = tmp_path / "ckpt-2.pt.tmp"
    tmp.write_bytes(b"partial")
    resume = CheckpointManager.find_resume(tmp_path)
    assert resume == path
    assert not (tmp_path / "ckpt-2.pt").exists()

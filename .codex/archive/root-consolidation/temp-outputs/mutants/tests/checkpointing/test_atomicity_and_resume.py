"""
Test Atomicity And Resume

Test module for atomicity and resume.
"""

import pytest

pytest.importorskip("tensorboard")

import os

from src.training.checkpoint_manager import CheckpointManager


def test_atomicity_and_resume(tmp_path, monkeypatch):
    mgr = CheckpointManager(tmp_path, keep_last=1, metric=None)
    orig_replace = os.replace

    def boom(src, dst):
        raise RuntimeError("boom")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(RuntimeError):
        mgr.save_now(1, b"x")
    assert not (tmp_path / "ckpt-1.pt").exists(), "Condition must be true"

    monkeypatch.setattr(os, "replace", orig_replace)
    p = mgr.save_now(2, b"x")
    assert CheckpointManager.find_resume(tmp_path) == str(p), "Condition must be true"

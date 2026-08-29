"""
Test Checkpoint Commit Meta

Test module for checkpoint commit meta.
"""

import subprocess
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from codex_ml.utils.checkpointing import save_checkpoint


@pytest.mark.ml
def test_checkpoint_records_git_commit(tmp_path):
    """Test that checkpoint records git commit hash."""

    class Toy(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(2, 2)

    model = Toy()
    path = tmp_path / "ckpt.pt"

    # Ensure the checkpoint directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    save_checkpoint(str(path), model, None, None, epoch=0)
    # Use map_location to avoid device issues and weights_only=False for custom classes
    ckpt = torch.load(
        str(path), weights_only=False, map_location="cpu"
    )  # nosec B614 - Test checkpoint with custom model class requires weights_only=False
    extra = ckpt["extra"]
    repo_root = Path(__file__).resolve().parent.parent
    commit = subprocess.check_output(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True
    ).strip()
    assert extra["git_commit"] == commit, "Condition must be true"
    assert "system" in extra, "Condition must be true"

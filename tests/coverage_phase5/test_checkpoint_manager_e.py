"""Test checkpoint manager module 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class CheckpointMetadata:
    checkpoint_id: str
    epoch: int
    loss: float


class CheckpointManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.checkpoints: Dict[str, CheckpointMetadata] = {}

    def save_checkpoint(self, ckpt_id: str, epoch: int, loss: float) -> bool:
        self.checkpoints[ckpt_id] = CheckpointMetadata(ckpt_id, epoch, loss)
        return True

    def load_checkpoint(self, ckpt_id: str) -> CheckpointMetadata:
        return self.checkpoints.get(ckpt_id)

    def list_checkpoints(self) -> Dict[str, CheckpointMetadata]:
        return self.checkpoints


def test_checkpoint_manager_4_init():
    """Test checkpoint manager initialization."""
    manager = CheckpointManager(os.path.join(tempfile.gettempdir(), "ckpts"))
    assert manager.base_dir == os.path.join(tempfile.gettempdir(), "ckpts"), "base_dir is not valid"


def test_checkpoint_manager_4_save():
    """Test saving checkpoints."""
    manager = CheckpointManager("/tmp")
    result = manager.save_checkpoint("ckpt_1", 10, 0.5)

    assert result is True, "Result must not be empty"
    assert "ckpt_1" in manager.checkpoints, "Condition must be true"


def test_checkpoint_manager_4_load():
    """Test loading checkpoints."""
    manager = CheckpointManager("/tmp")
    manager.save_checkpoint("ckpt_2", 20, 0.3)

    ckpt = manager.load_checkpoint("ckpt_2")
    assert ckpt.epoch == 20, "epoch is not valid"
    assert ckpt.loss == 0.3, "loss is not valid"


def test_checkpoint_manager_4_list():
    """Test listing checkpoints."""
    manager = CheckpointManager("/tmp")
    manager.save_checkpoint("ckpt_a", 5, 0.7)
    manager.save_checkpoint("ckpt_b", 10, 0.4)

    ckpts = manager.list_checkpoints()
    assert len(ckpts) == 2, "Ckpts must not be empty"

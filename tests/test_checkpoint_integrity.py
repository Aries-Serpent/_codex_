"""
Test Checkpoint Integrity

Test module for checkpoint integrity.
"""

import pytest

pytest.importorskip("torch")

from torch import nn
from torch.optim import SGD

from codex_ml.utils.checkpointing import (
    CheckpointLoadError,
    load_training_checkpoint,
    save_checkpoint,
)


def test_load_checkpoint_detects_corruption(tmp_path):
    model = nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    ckpt = tmp_path / "model.pt"
    save_checkpoint(str(ckpt), model, opt, None, epoch=1)

    # Corrupt checkpoint bytes
    data = ckpt.read_bytes()
    ckpt.write_bytes(b"corrupt" + data[7:])

    # Use exc_info to capture and check the exception without regex matching
    with pytest.raises(CheckpointLoadError) as exc_info:
        load_training_checkpoint(str(ckpt), model, opt)
    # Verify checksum is mentioned in the error
    assert "checksum" in str(exc_info.value), "Value must be initialized"

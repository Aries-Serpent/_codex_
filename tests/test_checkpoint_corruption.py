import pytest

pytest.importorskip("torch")

import torch

from codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint


def test_load_checkpoint_detects_corruption(tmp_path):
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.01)
    ckpt = tmp_path / "model.pt"

    save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=3, extra={"loss": 0.1})

    # Corrupt checkpoint file after checksum was written
    ckpt.write_bytes(b"bad-data")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        load_training_checkpoint(str(ckpt), model, opt)

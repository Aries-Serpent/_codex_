from pathlib import Path

import pytest
import torch

from codex_ml.utils.checkpointing import load_checkpoint, save_checkpoint


class DummyModel:
    def __init__(self):
        self.weights = {"w": torch.tensor([1.0, 2.0])}

    def state_dict(self):
        return self.weights

    def load_state_dict(self, state_dict):
        self.weights.update(state_dict)


class DummyOpt:
    def __init__(self):
        self.state = {"lr": 0.01}

    def state_dict(self):
        return self.state

    def load_state_dict(self, state_dict):
        self.state.update(state_dict)


def test_load_checkpoint_detects_corruption(tmp_path: Path):
    model = DummyModel()
    opt = DummyOpt()
    ckpt = tmp_path / "model.pt"
    save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=1, extra={})
    original = ckpt.read_bytes()
    ckpt.write_bytes(b"corrupted")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        load_checkpoint(str(ckpt), model, opt)
    ckpt.write_bytes(original)

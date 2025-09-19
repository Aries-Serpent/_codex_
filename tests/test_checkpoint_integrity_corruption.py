import pytest

pytest.importorskip("torch")

import torch

from codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint


class DummyModel:
    def __init__(self):
        self.weights = {"w": torch.tensor([1.0, 2.0])}

    def state_dict(self):
        return self.weights

    def load_state_dict(self, state):
        self.weights.update(state)


class DummyOpt:
    def __init__(self):
        self.state = {"lr": 0.1}

    def state_dict(self):
        return self.state

    def load_state_dict(self, state):
        self.state.update(state)


def test_load_checkpoint_detects_corruption(tmp_path):
    path = tmp_path / "model.pt"
    model = DummyModel()
    opt = DummyOpt()

    save_checkpoint(str(path), model, opt, scheduler=None, epoch=1, extra={})
    original = path.read_bytes()
    path.write_bytes(b"corrupted")

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        load_training_checkpoint(str(path), model, opt)

    path.write_bytes(original)

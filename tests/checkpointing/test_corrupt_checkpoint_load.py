import pytest

from codex_ml.utils.checkpointing import (
    CheckpointLoadError,
    load_training_checkpoint,
    save_checkpoint,
)

torch = pytest.importorskip("torch")


class TinyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = torch.nn.Linear(2, 2)

    def forward(self, x):
        return self.lin(x)


def test_load_checkpoint_detects_corruption(tmp_path):
    model = TinyModel()
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    ckpt = tmp_path / "model.pt"

    save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=1, extra={})
    # Corrupt the checkpoint file after saving
    ckpt.write_bytes(b"corrupted")

    with pytest.raises(CheckpointLoadError, match="checksum mismatch"):
        load_training_checkpoint(str(ckpt), model, opt)

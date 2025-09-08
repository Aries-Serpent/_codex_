import pytest
from torch import nn
from torch.optim import SGD

from codex_ml.utils.checkpointing import load_checkpoint, save_checkpoint


def test_load_checkpoint_detects_corruption(tmp_path):
    model = nn.Linear(2, 2)
    opt = SGD(model.parameters(), lr=0.1)
    ckpt = tmp_path / "model.pt"
    save_checkpoint(str(ckpt), model, opt, None, epoch=1)

    # Corrupt checkpoint bytes
    data = ckpt.read_bytes()
    ckpt.write_bytes(b"corrupt" + data[7:])

    with pytest.raises(RuntimeError, match="checksum"):
        load_checkpoint(str(ckpt), model, opt)

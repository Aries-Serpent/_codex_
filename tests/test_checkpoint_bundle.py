"""
Test Checkpoint Bundle

Test module for checkpoint bundle.
"""

import pathlib
import sys

import pytest

torch = pytest.importorskip("torch")

from codex_ml.utils.checkpointing import (
    load_training_checkpoint,
    save_checkpoint,
)

# PyTorch 2.x + Python 3.12: issubclass() arg 2 union-type bug in torch.serialization
_TORCH_312_BUG = sys.version_info >= (3, 12) and tuple(
    int(x) for x in torch.__version__.split(".")[:2]
) < (2, 7)


class TinyModule(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(2, 2)


@pytest.mark.parametrize("epoch", [0, 3])
@pytest.mark.skipif(
    _TORCH_312_BUG,
    reason="PyTorch 2.x + Python 3.12: issubclass() union-type bug in torch.serialization",
)
def test_checkpoint_roundtrip(tmp_path: pathlib.Path, epoch: int) -> None:
    model = TinyModule()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    ckpt_path = tmp_path / "model.pt"
    save_checkpoint(str(ckpt_path), model, optimizer, None, epoch, extra={"note": "ok"})
    assert ckpt_path.exists(), "Condition must be true"

    restored = TinyModule()
    opt2 = torch.optim.SGD(restored.parameters(), lr=0.01)
    state = load_training_checkpoint(str(ckpt_path), model=restored, optimizer=opt2)

    assert state.get("epoch") == epoch, "Condition must be true"
    for original, target in zip(model.parameters(), restored.parameters()):
        assert torch.allclose(original, target)

import pathlib

import pytest

torch = pytest.importorskip("torch")  # noqa: F401

from codex_ml.utils.checkpointing import load_training_checkpoint, save_checkpoint


class TinyModule(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(2, 2)


@pytest.mark.parametrize("epoch", [0, 3])
def test_checkpoint_roundtrip(tmp_path: pathlib.Path, epoch: int) -> None:
    model = TinyModule()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    ckpt_path = tmp_path / "model.pt"
    save_checkpoint(str(ckpt_path), model, optimizer, None, epoch, extra={"note": "ok"})
    assert ckpt_path.exists()

    restored = TinyModule()
    opt2 = torch.optim.SGD(restored.parameters(), lr=0.01)
    state = load_training_checkpoint(str(ckpt_path), model=restored, optimizer=opt2)

    assert state.get("epoch") == epoch
    for original, target in zip(model.parameters(), restored.parameters()):
        assert torch.allclose(original, target)

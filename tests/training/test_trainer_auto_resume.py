import pytest

from training.checkpointing import save_checkpoint
from training.trainer import CheckpointConfig, Trainer, TrainerConfig

try:  # pragma: no cover - optional dependency
    import torch  # type: ignore
except Exception:  # pragma: no cover - torch missing
    torch = None  # type: ignore


HAS_TORCH_RUNTIME = bool(
    torch
    and hasattr(torch, "nn")
    and hasattr(torch, "optim")
    and hasattr(torch.nn, "Linear")
    and hasattr(torch.optim, "SGD")
)


def _make_loader(torch):
    inputs = torch.zeros((4, 2))
    targets = torch.zeros((4,), dtype=torch.long)
    return [(inputs, targets)]


@pytest.mark.skipif(not HAS_TORCH_RUNTIME, reason="torch runtime modules unavailable")
def test_trainer_auto_resumes_latest_checkpoint(tmp_path):
    assert torch is not None  # for type checkers
    model = torch.nn.Linear(2, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    save_checkpoint(
        model,
        optimizer,
        epoch=3,
        val_metric=0.123,
        out_dir=tmp_path,
        mode="min",
        keep_best_k=1,
    )

    new_model = torch.nn.Linear(2, 2)
    new_optimizer = torch.optim.SGD(new_model.parameters(), lr=0.1)
    trainer = Trainer(
        new_model,
        new_optimizer,
        _make_loader(torch),
        trainer_config=TrainerConfig(epochs=1),
        checkpoint_config=CheckpointConfig(directory=str(tmp_path)),
    )

    assert trainer.state.epoch == 3
    assert trainer.state.best_metric == pytest.approx(0.123)
    for key, value in model.state_dict().items():
        assert torch.allclose(trainer.simple.model.state_dict()[key], value)

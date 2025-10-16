from pathlib import Path

import pytest


torch = pytest.importorskip("torch", reason="torch required")

pytestmark = pytest.mark.requires_torch


def _toy_model(d_in: int = 8, d_out: int = 3) -> "torch.nn.Module":
    return torch.nn.Sequential(
        torch.nn.Linear(d_in, 16),
        torch.nn.ReLU(),
        torch.nn.Linear(16, d_out),
    )


def test_save_and_load_with_rng(tmp_path: Path) -> None:
    from src.training.checkpointing import load_checkpoint, save_checkpoint, snapshot_rng_state

    model = _toy_model()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    _ = torch.randn(4)
    before = snapshot_rng_state()

    ckpt_path = save_checkpoint(
        model,
        optimizer,
        epoch=1,
        val_metric=0.5,
        out_dir=tmp_path,
        keep_best_k=2,
    )
    assert ckpt_path.exists()

    _ = torch.nn.init.xavier_uniform_(next(model.parameters()))
    epoch, metric = load_checkpoint(ckpt_path, model, optimizer, restore_rng=True)
    assert epoch == 1
    assert metric == 0.5

    after = snapshot_rng_state()
    assert torch.equal(before.cpu, after.cpu)


def test_best_k_ties_and_nan(tmp_path: Path) -> None:
    from src.training.checkpointing import save_checkpoint

    model = _toy_model()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    save_checkpoint(
        model,
        optimizer,
        epoch=1,
        val_metric=0.30,
        out_dir=tmp_path,
        keep_best_k=1,
        mode="min",
    )
    save_checkpoint(
        model,
        optimizer,
        epoch=2,
        val_metric=0.30,
        out_dir=tmp_path,
        keep_best_k=1,
        mode="min",
    )
    save_checkpoint(
        model,
        optimizer,
        epoch=3,
        val_metric=float("nan"),
        out_dir=tmp_path,
        keep_best_k=1,
        mode="min",
    )

    kept = sorted(tmp_path.glob("epoch*-metric*.pt"))
    assert len(kept) == 1
    assert kept[0].stem.startswith("epoch2-metric0.300000")

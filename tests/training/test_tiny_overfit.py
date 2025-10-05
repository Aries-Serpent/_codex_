from __future__ import annotations

import math
from pathlib import Path

import pytest

pytest.importorskip("torch")

import torch
from torch import nn
from torch.utils.data import Dataset

from training.functional_training import TrainCfg, run_custom_trainer
from training.seed import ensure_global_seed


class TinyRegressionDataset(Dataset):
    def __init__(self, n_items: int = 64) -> None:
        ensure_global_seed(7)
        xs = torch.linspace(-1.0, 1.0, n_items)
        noise = torch.zeros_like(xs)
        self.inputs = xs
        self.targets = 3 * xs + 1 + noise

    def __len__(self) -> int:
        return len(self.inputs)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        x = self.inputs[idx]
        y = self.targets[idx]
        return {
            "input_ids": x.unsqueeze(0),
            "labels": y.unsqueeze(0),
        }


class TinyRegressor(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor) -> dict[str, torch.Tensor]:
        preds = self.linear(input_ids)
        loss = nn.functional.mse_loss(preds, labels)
        return {"loss": loss, "logits": preds}


@pytest.mark.cpu_only
@pytest.mark.slow(reason="performs 10 tiny optimisation steps to assert determinism")
def test_custom_trainer_tiny_overfit(tmp_path: Path) -> None:
    dataset = TinyRegressionDataset()
    model = TinyRegressor()
    cfg = TrainCfg(
        epochs=5,
        batch_size=4,
        grad_accum=1,
        lr=0.1,
        max_steps=10,
        log_every=1,
        checkpoint_dir=str(tmp_path / "ckpts"),
        log_dir=str(tmp_path / "logs"),
        save_every=0,
        dtype="fp32",
        deterministic=True,
        seed=11,
        mlflow_enable=False,
    )

    result = run_custom_trainer(model, tokenizer=None, train_ds=dataset, val_ds=None, cfg=cfg)
    assert result["global_step"] == 10
    assert result["history"], "loss history should not be empty"
    # Final loss should be small for a well-conditioned linear problem.
    assert result["history"][-1] < 1e-3

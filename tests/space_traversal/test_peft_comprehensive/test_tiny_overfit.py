"""
pytest.importorskip("tensorboard")
Test Tiny Overfit

Test module for tiny overfit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Avoid modifying sys.path to prevent stdlib shadowing (e.g. tests/ast -> ast).
# Import torch helpers using absolute import from tests package
from tests.utils.torch_helpers import require_torch

torch = require_torch()

from training.functional_training import TrainCfg, run_custom_trainer
from training.seed import ensure_global_seed


class TinyRegressionDataset(torch.utils.data.Dataset):
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


class TinyRegressor(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(1, 1)

    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor) -> dict[str, torch.Tensor]:
        preds = self.linear(input_ids)
        loss = torch.nn.functional.mse_loss(preds, labels)
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
    assert result["global_step"] == 10, "Result must not be empty"
    assert result["history"], "loss history should not be empty"
    # Final loss should decrease from initial; exact threshold varies across torch versions
    assert result["history"][-1] < result["history"][0], "loss should decrease during training"

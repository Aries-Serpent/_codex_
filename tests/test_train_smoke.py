import math

import pytest

torch = pytest.importorskip("torch")
training_ft = pytest.importorskip("training.functional_training")

TrainCfg = training_ft.TrainCfg
run_custom_trainer = training_ft.run_custom_trainer


class _ToyDataset(torch.utils.data.Dataset):
    def __init__(self) -> None:
        super().__init__()
        inputs = torch.linspace(-1.0, 1.0, steps=8, dtype=torch.float32).unsqueeze(-1)
        self._inputs = inputs
        self._labels = 2.5 * inputs + 0.25

    def __len__(self) -> int:
        return len(self._inputs)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        x = self._inputs[index]
        y = self._labels[index]
        mask = torch.ones_like(x)
        return {
            "input_ids": x.clone(),
            "attention_mask": mask,
            "labels": y.clone(),
        }


class _ToyModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(1, 1)

    def forward(self, input_ids, attention_mask=None, labels=None):  # type: ignore[override]
        preds = self.linear(input_ids)
        loss = torch.nn.functional.mse_loss(preds, labels)
        return {"loss": loss, "logits": preds}


def test_run_custom_trainer_smoke(tmp_path, monkeypatch):
    dataset = _ToyDataset()
    model = _ToyModel()

    monkeypatch.setattr(
        "training.functional_training._codex_logging_bootstrap", lambda *a, **k: {}, raising=False
    )
    monkeypatch.setattr(
        "training.functional_training._codex_log_all", lambda *a, **k: None, raising=False
    )

    cfg = TrainCfg(
        epochs=1,
        batch_size=4,
        grad_accum=1,
        lr=0.3,
        weight_decay=0.0,
        log_every=1,
        save_every=2,
        checkpoint_dir=str(tmp_path / "ckpts"),
        max_grad_norm=None,
        seed=7,
    )

    result = run_custom_trainer(model, None, dataset, None, cfg)

    history = result["history"]
    assert result["global_step"] == 2
    assert len(history) >= 2
    assert all(math.isfinite(v) for v in history)
    assert history[0] > history[-1]

    checkpoint_path = tmp_path / "ckpts" / "step2.pt"
    assert checkpoint_path.exists()

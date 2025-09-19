import pytest

pytest.importorskip("torch")
pytest.importorskip("opacus")

import torch
import torch.nn.functional as F

from codex.training import TrainCfg, run_custom_trainer


def test_dp_training_runs(monkeypatch, tmp_path):
    opacus = pytest.importorskip("opacus")

    class DummyPrivacyEngine:
        def __init__(self) -> None:
            self.calls: dict[str, float] = {}

        def make_private(self, module, optimizer, data_loader, *, noise_multiplier, max_grad_norm):
            self.calls["noise_multiplier"] = float(noise_multiplier)
            self.calls["max_grad_norm"] = float(max_grad_norm)
            return module, optimizer, data_loader

    engine = DummyPrivacyEngine()
    monkeypatch.setattr(opacus, "PrivacyEngine", lambda *a, **k: engine)

    class DummyDataset(torch.utils.data.Dataset):
        def __init__(self) -> None:
            self.inputs = torch.eye(4)
            self.labels = torch.tensor([0, 1, 0, 1], dtype=torch.long)

        def __len__(self) -> int:
            return self.inputs.shape[0]

        def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
            return {
                "input_ids": self.inputs[idx],
                "attention_mask": torch.ones_like(self.inputs[idx]),
                "labels": self.labels[idx],
            }

    class DummyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.linear = torch.nn.Linear(4, 2)

        def forward(self, input_ids=None, attention_mask=None, labels=None):  # type: ignore[override]
            x = input_ids.float()
            logits = self.linear(x)
            target = labels if labels is not None else torch.zeros(x.size(0), dtype=torch.long)
            loss = F.cross_entropy(logits, target)
            return {"loss": loss, "logits": logits}

    dataset = DummyDataset()
    cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        log_every=1,
        save_every=10,
        max_steps=2,
        checkpoint_dir=str(tmp_path),
        dp_enabled=True,
        dp_noise_multiplier=1.0,
        dp_max_grad_norm=1.0,
        limit_train_batches=1,
    )

    result = run_custom_trainer(DummyModel(), None, dataset, None, cfg)

    assert "history" in result and result["history"]
    assert engine.calls["noise_multiplier"] == pytest.approx(1.0)
    assert engine.calls["max_grad_norm"] == pytest.approx(1.0)

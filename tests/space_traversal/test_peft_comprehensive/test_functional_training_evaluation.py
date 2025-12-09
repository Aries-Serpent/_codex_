from __future__ import annotations

import types
from typing import Any, Dict, List

import pytest

torch = pytest.importorskip("torch")

if not hasattr(torch, "tensor") or not hasattr(torch, "utils"):
    pytest.skip("PyTorch runtime not available", allow_module_level=True)


class DummyDataset(torch.utils.data.Dataset):
    def __init__(self, mapping: Dict[str, Any]):
        self._data = {k: torch.tensor(v) for k, v in mapping.items()}

    def __len__(self) -> int:
        return int(self._data["input_ids"].shape[0])

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return {key: value[index] for key, value in self._data.items()}

    @classmethod
    def from_dict(cls, mapping: Dict[str, Any]) -> "DummyDataset":
        return cls(mapping)

    def with_format(self, fmt: str) -> "DummyDataset":
        assert fmt == "torch"
        return self


class DummyTokenizer:
    pad_token: int = 0
    eos_token: int = 0

    @classmethod
    def from_pretrained(cls, name: str) -> "DummyTokenizer":
        return cls()

    def __call__(
        self, texts: List[str], padding: bool = True, return_tensors: str = "pt"
    ) -> Dict[str, Any]:
        max_len = max(len(text.split()) for text in texts)
        input_ids = []
        attention = []
        for text in texts:
            tokens = list(range(1, len(text.split()) + 1))
            if len(tokens) < max_len:
                tokens.extend([0] * (max_len - len(tokens)))
            input_ids.append(tokens)
            attention.append([1 if tok else 0 for tok in tokens])
        return {
            "input_ids": torch.tensor(input_ids),
            "attention_mask": torch.tensor(attention),
        }


class DummyModel(torch.nn.Module):
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        labels: torch.Tensor | None = None,
    ):
        loss = torch.tensor(0.5, dtype=torch.float32, device=input_ids.device)
        return types.SimpleNamespace(loss=loss)


def test_run_functional_training_appends_validation_metrics(monkeypatch):
    import sys

    from codex_ml import training

    monkeypatch.setitem(sys.modules, "datasets", types.SimpleNamespace(Dataset=DummyDataset))
    monkeypatch.setitem(
        sys.modules, "transformers", types.SimpleNamespace(AutoTokenizer=DummyTokenizer)
    )

    monkeypatch.setattr("codex_ml.models.registry.get_model", lambda *_, **__: DummyModel())

    def fake_run_custom_trainer(model: Any, tokenizer: Any, train_ds: Any, val_ds: Any, cfg: Any):
        return {"metrics": {"train_loss": 0.25}, "trainer_cfg": cfg}

    monkeypatch.setattr(
        "training.functional_training.run_custom_trainer",
        fake_run_custom_trainer,
    )

    config = {
        "seed": 0,
        "model": {"name": "dummy"},
        "learning_rate": 1e-3,
        "batch_size": 2,
        "max_epochs": 1,
        "gradient_accumulation": 1,
        "dataset": {"train_texts": ["a b", "c d"], "eval_texts": ["e f"], "format": "jsonl"},
        "tensorboard": False,
        "mlflow_enable": False,
        "wandb_enable": False,
        "system_metrics": "off",
    }

    result = training.run_functional_training(config)
    assert "metrics" in result
    assert "val_loss" in result["metrics"]
    assert "val_perplexity" in result["metrics"]

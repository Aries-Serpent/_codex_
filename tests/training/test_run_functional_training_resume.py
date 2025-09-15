from __future__ import annotations

import sys
import types

import numpy as np
import pytest

from codex_ml.training import run_functional_training


class _DummyTokenizer:
    pad_token = None
    eos_token = 0

    @classmethod
    def from_pretrained(cls, _name: str) -> "_DummyTokenizer":
        return cls()

    def __call__(self, texts, *, padding, return_tensors):
        length = max(len(t) for t in texts) if texts else 1
        data = np.zeros((len(texts), length), dtype=np.int64)
        attention = np.ones_like(data)
        return {
            "input_ids": _TensorWrapper(data),
            "attention_mask": _TensorWrapper(attention),
        }


class _TensorWrapper:
    def __init__(self, array: np.ndarray) -> None:
        self._array = array

    def clone(self) -> "_TensorWrapper":
        return _TensorWrapper(self._array.copy())

    def numpy(self) -> np.ndarray:
        return self._array

    def __array__(self):  # pragma: no cover - numpy protocol
        return self._array

    def __getattr__(self, name: str):  # pragma: no cover - delegation
        return getattr(self._array, name)

    def __getitem__(self, item):
        return self._array.__getitem__(item)

    def __setitem__(self, key, value):
        self._array.__setitem__(key, value)


class _DatasetModule:
    class Dataset:
        @staticmethod
        def from_dict(data):
            return {"data": data}


@pytest.fixture(autouse=True)
def _stub_modules(monkeypatch):
    transformers_mod = types.SimpleNamespace(AutoTokenizer=_DummyTokenizer)
    datasets_mod = types.SimpleNamespace(Dataset=_DatasetModule.Dataset)
    training_mod = types.ModuleType("training.functional_training")

    class _TrainCfg:
        __dataclass_fields__ = {
            name: None
            for name in [
                "epochs",
                "batch_size",
                "grad_accum",
                "lr",
                "resume_from",
                "checkpoint_dir",
            ]
        }

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    training_mod.TrainCfg = _TrainCfg
    training_mod.run_custom_trainer = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "transformers", transformers_mod)
    monkeypatch.setitem(sys.modules, "datasets", datasets_mod)
    monkeypatch.setitem(sys.modules, "training.functional_training", training_mod)
    registry_mod = types.ModuleType("codex_ml.models.registry")
    registry_mod.get_model = lambda *_, **__: object()
    monkeypatch.setitem(sys.modules, "codex_ml.models.registry", registry_mod)


def test_run_functional_training_resume(monkeypatch, tmp_path):
    checkpoint_dir = tmp_path / "ckpts"
    checkpoint_dir.mkdir()
    latest = checkpoint_dir / "step10.pt"
    latest.write_bytes(b"stub")

    recorded = {}

    def fake_load_ckpt(path: str):
        recorded["loaded"] = path

    def fake_run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg):
        recorded.update(
            {
                "resume_from": cfg.resume_from,
                "checkpoint_dir": cfg.checkpoint_dir,
                "texts": train_ds["data"]["input_ids"].tolist(),
            }
        )
        return {"result": "ok"}

    monkeypatch.setattr("codex_ml.utils.checkpointing.load_training_checkpoint", fake_load_ckpt)
    training_module = sys.modules["training.functional_training"]
    monkeypatch.setattr(training_module, "run_custom_trainer", fake_run_custom_trainer)

    config = {
        "training": {
            "texts": ["hello"],
            "val_texts": ["world"],
            "checkpoint_dir": str(checkpoint_dir),
        }
    }

    result = run_functional_training(config, resume=True)

    assert result == {"result": "ok"}
    assert recorded["resume_from"].endswith("step10.pt")
    assert recorded["checkpoint_dir"] == str(checkpoint_dir)
    assert recorded["loaded"].endswith("step10.pt")

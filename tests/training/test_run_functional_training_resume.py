from __future__ import annotations

import random
import sys
import types

import pytest

from codex_ml.training import run_functional_training
from codex_ml.utils.provenance import load_environment_summary

np = pytest.importorskip("numpy")


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
    latest = checkpoint_dir / "step10.ptz"
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
    assert recorded["resume_from"].endswith("step10.ptz")
    assert recorded["checkpoint_dir"] == str(checkpoint_dir)
    assert recorded["loaded"].endswith("step10.ptz")


def test_run_functional_training_accepts_string_model(monkeypatch, tmp_path):
    registry_module = sys.modules["codex_ml.models.registry"]

    recorded: dict[str, object] = {}

    def fake_get_model(name: str, cfg: dict[str, object]) -> object:
        recorded["name"] = name
        recorded["cfg"] = cfg
        return object()

    monkeypatch.setattr(registry_module, "get_model", fake_get_model, raising=False)

    config = {
        "training": {
            "texts": ["hello"],
            "model": "minilm",
            "checkpoint_dir": str(tmp_path / "ckpts"),
        }
    }

    run_functional_training(config)

    assert recorded["name"] == "minilm"
    assert isinstance(recorded["cfg"], dict)
    assert recorded["cfg"]["name"] == "minilm"


def test_run_functional_training_repeatable(monkeypatch, tmp_path):
    training_module = sys.modules["training.functional_training"]

    def fake_run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg):
        return {
            "train_ids": train_ds["data"]["input_ids"].tolist(),
            "seed": cfg.seed,
        }

    monkeypatch.setattr(training_module, "run_custom_trainer", fake_run_custom_trainer)

    base_config = {
        "seed": 99,
        "output_dir": str(tmp_path / "run1"),
        "dataset": {"train_texts": ["alpha", "beta"]},
    }

    first = run_functional_training(base_config, resume=False)

    random.random()
    np.random.rand()

    second_config = dict(base_config)
    second_config["output_dir"] = str(tmp_path / "run2")
    second = run_functional_training(second_config, resume=False)

    assert first == second

    prov1 = load_environment_summary(tmp_path / "run1" / "provenance")
    prov2 = load_environment_summary(tmp_path / "run2" / "provenance")
    assert prov1["seed"] == prov2["seed"] == 99
    assert prov1["command"] == prov2["command"] == "train"

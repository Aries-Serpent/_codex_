import sys
import types
from pathlib import Path

from omegaconf import OmegaConf

import training.functional_training as ft


def test_main_invokes_run_hf_trainer(monkeypatch, tmp_path: Path):
    cfg = OmegaConf.create({"training": {"texts": ["hi"], "seed": 123}})
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)
    called = {}

    def fake_run(texts, output_dir, **kwargs):
        called["texts"] = list(texts)
        called["output_dir"] = output_dir
        called.update(kwargs)
        return {"loss": 0.0}

    monkeypatch.setattr(ft, "run_hf_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "hf"])
    assert called["texts"] == ["hi"]
    assert called["output_dir"] == tmp_path
    assert called["seed"] == 123


def test_main_populates_labels_for_custom_engine(monkeypatch, tmp_path: Path) -> None:
    cfg = OmegaConf.create({"training": {"texts": ["hi"], "seed": 0}})
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)

    class _Tok:
        def __call__(self, txts, padding=True, return_tensors="pt"):
            import torch

            t = torch.tensor([[0]])
            return {"input_ids": t, "attention_mask": t}

        @classmethod
        def from_pretrained(cls, name):  # pragma: no cover - simple stub
            return cls()

    class _Model:
        @classmethod
        def from_pretrained(cls, name):  # pragma: no cover - simple stub
            return cls()

        def to(self, device):  # pragma: no cover - no-op for test
            pass

    class _Dataset:
        def __init__(self, data):
            self._data = data
            self.column_names = list(data.keys())

        @classmethod
        def from_dict(cls, data):
            return cls(data)

        def __getitem__(self, idx):
            return {k: v[idx] for k, v in self._data.items()}

    monkeypatch.setitem(
        sys.modules,
        "transformers",
        types.SimpleNamespace(AutoTokenizer=_Tok, AutoModelForCausalLM=_Model),
    )
    monkeypatch.setitem(
        sys.modules,
        "datasets",
        types.SimpleNamespace(Dataset=_Dataset),
    )
    captured = {}

    def fake_run(model, tokenizer, train_ds, val_ds, train_cfg):
        captured["columns"] = train_ds.column_names
        captured["input_ids"] = train_ds[0]["input_ids"]
        captured["labels"] = train_ds[0]["labels"]
        return {}

    monkeypatch.setattr(ft, "run_custom_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "custom"])
    assert "labels" in captured["columns"]
    assert captured["input_ids"].equal(captured["labels"])

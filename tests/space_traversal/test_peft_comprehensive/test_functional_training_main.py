import sys
import types
from pathlib import Path
from typing import Any

import pytest

import codex.training as ft
from omegaconf import OmegaConf

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")


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
    # Ensure hydra_cfg is provided for downstream compatibility
    assert isinstance(called.get("hydra_cfg"), dict)
    assert called["hydra_cfg"].get("seed") == 123


def test_main_populates_labels_for_custom_engine(monkeypatch, tmp_path: Path) -> None:
    cfg = OmegaConf.create(
        {"training": {"texts": ["hi"], "val_texts": ["bye"], "seed": 0, "grad_accum": 3}}
    )
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)

    class _Tok:
        pad_token = None
        eos_token = "</s>"
        pad_token_id = 0
        eos_token_id = 0

        def __call__(self, txts, padding=True, return_tensors="pt"):
            assert self.pad_token is not None

            ids = torch.tensor([[5, 6, self.pad_token_id]] * len(txts))
            mask = torch.tensor([[1, 1, 0]] * len(txts))
            return {"input_ids": ids, "attention_mask": mask}

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
            return {k: torch.tensor(v[idx]) for k, v in self._data.items()}

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
        row = train_ds[0]
        captured["input_ids"] = row["input_ids"]
        captured["labels"] = row["labels"]
        captured["val_labels"] = val_ds[0]["labels"] if val_ds else None
        captured["grad_accum"] = train_cfg.grad_accum
        return {}

    monkeypatch.setattr(ft, "run_custom_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "custom"])
    assert "labels" in captured["columns"]
    assert captured["input_ids"].tolist() == [5, 6, 0]
    assert captured["labels"].tolist() == [5, 6, -100]
    assert captured["val_labels"].tolist() == [5, 6, -100]
    assert captured["grad_accum"] == 3


def test_main_passes_lora_config(monkeypatch, tmp_path: Path):
    cfg = OmegaConf.create(
        {"training": {"texts": ["hi"], "lora": {"enable": True, "r": 8, "alpha": 32}}}
    )
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)
    called: dict[str, Any] = {}

    def fake_run(texts, output_dir, **kwargs):
        called.update(kwargs)
        return {}

    monkeypatch.setattr(ft, "run_hf_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "hf"])
    assert called["lora_r"] == 8
    assert called["lora_alpha"] == 32


def test_main_cli_overrides_lora(monkeypatch, tmp_path: Path):
    cfg = OmegaConf.create({"training": {"texts": ["hi"]}})
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)
    called: dict[str, Any] = {}

    def fake_run(texts, output_dir, **kwargs):
        called.update(kwargs)
        return {}

    monkeypatch.setattr(ft, "run_hf_trainer", fake_run)
    ft.main(
        [
            "--output-dir",
            str(tmp_path),
            "--engine",
            "hf",
            "--lora-r",
            "4",
            "--lora-alpha",
            "32",
            "--lora-dropout",
            "0.2",
        ]
    )
    assert called["lora_r"] == 4
    assert called["lora_alpha"] == 32
    assert called["lora_dropout"] == 0.2


def test_main_propagates_grad_accum_and_determinism(monkeypatch, tmp_path: Path) -> None:
    cfg = OmegaConf.create(
        {
            "training": {
                "texts": ["hi"],
                "grad_accum": 5,
                "reproducibility": {"cudnn_deterministic": True},
            }
        }
    )
    monkeypatch.setattr(ft, "load_training_cfg", lambda **kwargs: cfg)
    captured: dict[str, Any] = {}

    def fake_run(texts, output_dir, **kwargs):
        captured.update(kwargs)
        return {}

    monkeypatch.setattr(ft, "run_hf_trainer", fake_run)
    ft.main(["--output-dir", str(tmp_path), "--engine", "hf"])
    assert captured["gradient_accumulation_steps"] == 5
    assert captured["deterministic"] is True

from __future__ import annotations

from pathlib import Path

import torch

from training import engine_hf_trainer as hf


def test_run_hf_trainer_applies_lora(monkeypatch, tmp_path: Path) -> None:
    seen: dict[str, object] = {}

    def fake_apply_lora(model, cfg):
        seen["cfg"] = cfg
        setattr(model, "peft_config", dict(cfg))
        return model

    monkeypatch.setattr(hf, "apply_lora", fake_apply_lora)

    class DummyTokenizer:
        pad_token = None
        eos_token = "</s>"
        pad_token_id = 0
        eos_token_id = 0

        def __call__(self, text, truncation=True):  # pragma: no cover - simple stub
            return {"input_ids": [0]}

    monkeypatch.setattr(
        hf,
        "AutoTokenizer",
        type(
            "DT",
            (),
            {"from_pretrained": staticmethod(lambda name, use_fast=True: DummyTokenizer())},
        ),
    )
    monkeypatch.setattr(hf, "prepare_dataset", lambda texts, tokenizer: list(texts))
    monkeypatch.setattr(hf, "DataCollatorForLanguageModeling", lambda tokenizer, mlm=False: None)

    class DummyTrainer:
        class State:
            def __init__(self) -> None:
                self.global_step = 0

        def __init__(self, *args, **kwargs):
            self.state = self.State()

        def train(self, resume_from_checkpoint=None):  # pragma: no cover - noop
            return type("O", (), {"metrics": {"train_loss": 0.0}})()

        def save_model(self):  # pragma: no cover - noop
            return None

    monkeypatch.setattr(hf, "Trainer", DummyTrainer)

    class DummyModel(torch.nn.Module):
        def to(self, *args, **kwargs):  # pragma: no cover - simple stub
            return self

    model = DummyModel()

    hf.run_hf_trainer(
        ["hi"],
        tmp_path,
        model=model,
        lora_r=4,
        lora_alpha=32,
        lora_dropout=0.2,
        distributed=False,
    )

    assert seen["cfg"] == {"r": 4, "lora_alpha": 32, "lora_dropout": 0.2}
    assert getattr(model, "peft_config") == seen["cfg"]

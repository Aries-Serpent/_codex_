import types

import pytest

pytest.importorskip("numpy")
pytest.importorskip("torch")

import torch

from training.engine_hf_trainer import run_hf_trainer


def test_hf_trainer_hydra_lora_cfg(monkeypatch, tmp_path):
    captured = {}

    def fake_tok_from_pretrained(name, use_fast=True):
        class Tok:
            pad_token = None
            eos_token = "</s>"
            pad_token_id = 0

            def __call__(self, text, truncation=True):
                return {"input_ids": [0]}

            def save_pretrained(self, output_dir):
                return None

        return Tok()

    def fake_model_from_pretrained(name):
        class M(torch.nn.Module):
            def forward(self, input_ids=None, labels=None):
                return types.SimpleNamespace(loss=torch.tensor(0.0))

        return M()

    def fake_train(self, resume_from_checkpoint=None):
        return types.SimpleNamespace(metrics={"train_loss": 0.0})

    def fake_apply_lora(model, cfg):
        captured["cfg"] = cfg
        return model

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", fake_tok_from_pretrained
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained",
        fake_model_from_pretrained,
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer.train", fake_train)
    monkeypatch.setattr("training.engine_hf_trainer.apply_lora", fake_apply_lora)

    run_hf_trainer(
        ["hi"],
        tmp_path,
        model_name="sshleifer/tiny-gpt2",
        hydra_cfg={"lora_r": 2, "lora_alpha": 32, "lora_dropout": 0.1},
        distributed=False,
    )

    assert captured["cfg"] == {"r": 2, "lora_alpha": 32, "lora_dropout": 0.1}

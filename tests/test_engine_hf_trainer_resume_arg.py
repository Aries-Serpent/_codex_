import torch

from training.engine_hf_trainer import run_hf_trainer


def test_run_hf_trainer_passes_resume_from(monkeypatch, tmp_path):
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()

    captured = {}

    def fake_tok_from_pretrained(name, use_fast=True):
        class Tok:
            pad_token = None
            eos_token = "</s>"
            pad_token_id = 0

            def __call__(self, text, truncation=True):
                return {"input_ids": [0]}

        return Tok()

    def fake_model_from_pretrained(name):
        class M(torch.nn.Module):
            def forward(self, input_ids=None, labels=None):
                return type("O", (), {"loss": torch.tensor(0.0)})()

        return M()

    class DummyTrainer:
        class State:
            global_step = 0

        def __init__(self, *a, **k):
            self.state = self.State()

        def train(self, *, resume_from_checkpoint=None, **k):
            captured["resume"] = resume_from_checkpoint
            return type("O", (), {"metrics": {}})()

        def save_model(self):
            return None

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", fake_tok_from_pretrained
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained",
        fake_model_from_pretrained,
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer", DummyTrainer)

    run_hf_trainer(["hi"], tmp_path / "out", resume_from=str(ckpt), distributed=False)
    assert captured["resume"] == str(ckpt)


def test_run_hf_trainer_ignores_missing_resume_from(monkeypatch, tmp_path):
    captured = {}

    def fake_tok_from_pretrained(name, use_fast=True):
        class Tok:
            pad_token = None
            eos_token = "</s>"
            pad_token_id = 0

            def __call__(self, text, truncation=True):
                return {"input_ids": [0]}

        return Tok()

    def fake_model_from_pretrained(name):
        class M(torch.nn.Module):
            def forward(self, input_ids=None, labels=None):
                return type("O", (), {"loss": torch.tensor(0.0)})()

        return M()

    class DummyTrainer:
        class State:
            global_step = 0

        def __init__(self, *a, **k):
            self.state = self.State()

        def train(self, *, resume_from_checkpoint=None, **k):
            captured["resume"] = resume_from_checkpoint
            return type("O", (), {"metrics": {}})()

        def save_model(self):
            return None

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", fake_tok_from_pretrained
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained",
        fake_model_from_pretrained,
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer", DummyTrainer)

    run_hf_trainer(["hi"], tmp_path / "out", resume_from="missing", distributed=False)
    assert captured["resume"] is None

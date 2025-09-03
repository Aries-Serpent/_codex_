from transformers import Trainer

from training.engine_hf_trainer import run_hf_trainer


def test_run_hf_trainer_passes_resume(monkeypatch, tmp_path):
    ckpt = tmp_path / "ckpt"
    ckpt.mkdir()
    (ckpt / "pytorch_model.bin").write_bytes(b"")

    called = {}

    def fake_train(self, resume_from_checkpoint=None):
        called["resume"] = resume_from_checkpoint

        class Result:
            metrics = {"train_loss": 0.0}

        return Result()

    monkeypatch.setattr(Trainer, "train", fake_train)
    texts = ["hi"]
    run_hf_trainer(texts, tmp_path / "out", resume_from=str(ckpt), distributed=False)
    assert called.get("resume") == str(ckpt)


def test_missing_resume_checkpoint_starts_fresh(monkeypatch, tmp_path):
    called = {}

    def fake_train(self, resume_from_checkpoint=None):
        called["resume"] = resume_from_checkpoint

        class Result:
            metrics = {"train_loss": 0.0}

        return Result()

    monkeypatch.setattr(Trainer, "train", fake_train)
    run_hf_trainer(["hi"], tmp_path / "out", resume_from="missing", distributed=False)
    assert called.get("resume") is None

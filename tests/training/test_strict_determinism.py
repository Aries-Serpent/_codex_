import types

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")

import torch

from codex.training import TrainCfg, run_custom_trainer
from codex_ml.models import MiniLM, MiniLMConfig
from training.data_utils import TextDataset
from training.engine_hf_trainer import run_hf_trainer


class _Tok:
    vocab = {str(i): i for i in range(5)}

    def encode(self, txt: str) -> list[int]:
        return [self.vocab[t] for t in txt.split()]


def _setup(tmp_path):
    tok = _Tok()
    ds = TextDataset(["0 1"], tok, block_size=2)
    model = MiniLM(MiniLMConfig(vocab_size=5, n_layers=1, d_model=8, n_heads=1, max_seq_len=2))
    cfg = TrainCfg(epochs=0, batch_size=1, max_steps=0, checkpoint_dir=str(tmp_path), device="cpu")
    return model, tok, ds, cfg


def _patch_cuda(monkeypatch, deterministic: bool) -> None:
    calls = {"count": 0}

    def fake_is_available() -> bool:
        calls["count"] += 1
        return calls["count"] == 1

    monkeypatch.setattr(torch.cuda, "is_available", fake_is_available)
    # cudnn.deterministic may not exist on some builds; allow non-raising set
    monkeypatch.setattr(torch.backends.cudnn, "deterministic", deterministic, raising=False)


def test_passes_when_deterministic(monkeypatch, tmp_path):
    model, tok, ds, cfg = _setup(tmp_path)
    _patch_cuda(monkeypatch, True)
    run_custom_trainer(model, tok, ds, None, cfg)


def test_raises_when_nondeterministic(monkeypatch, tmp_path):
    model, tok, ds, cfg = _setup(tmp_path)
    _patch_cuda(monkeypatch, False)
    with pytest.raises(AssertionError):
        run_custom_trainer(model, tok, ds, None, cfg)


def _patch_cuda_simple(monkeypatch, deterministic: bool) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.backends.cudnn, "deterministic", deterministic, raising=False)


def _stub_hf_components(monkeypatch) -> None:
    class Tok:
        pad_token = None
        eos_token = "</s>"
        pad_token_id = 0

        def __call__(self, text, truncation=True):
            return {"input_ids": [0]}

        def save_pretrained(self, output_dir):  # pragma: no cover - stub
            return None

    class M(torch.nn.Module):
        def forward(self, input_ids=None, labels=None):  # pragma: no cover - stub
            return types.SimpleNamespace(loss=torch.tensor(0.0))

    class DummyTrainer:
        class State:
            global_step = 0

        def __init__(self, *args, **kwargs):
            self.state = self.State()

        def train(self, *args, **kwargs):  # pragma: no cover - stub
            return types.SimpleNamespace(metrics={"train_loss": 0.0})

        def save_model(self):  # pragma: no cover - stub
            return None

    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoTokenizer.from_pretrained", lambda *a, **k: Tok()
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.AutoModelForCausalLM.from_pretrained", lambda *a, **k: M()
    )
    monkeypatch.setattr("training.engine_hf_trainer.Trainer", DummyTrainer)
    monkeypatch.setattr(
        "training.engine_hf_trainer.prepare_dataset", lambda texts, tok: list(texts or [])
    )
    monkeypatch.setattr(
        "training.engine_hf_trainer.DataCollatorForLanguageModeling", lambda *a, **k: object()
    )
    monkeypatch.setattr("training.engine_hf_trainer._make_accelerator", lambda **kw: None)


def test_hf_trainer_passes_when_deterministic(monkeypatch, tmp_path):
    _patch_cuda_simple(monkeypatch, True)
    _stub_hf_components(monkeypatch)
    monkeypatch.setattr("training.engine_hf_trainer.set_reproducible", lambda seed: None)
    run_hf_trainer(["hi"], tmp_path, distributed=False)


def test_hf_trainer_raises_when_nondeterministic(monkeypatch, tmp_path):
    _patch_cuda_simple(monkeypatch, False)
    _stub_hf_components(monkeypatch)
    monkeypatch.setattr("training.engine_hf_trainer.set_reproducible", lambda seed: None)
    with pytest.raises(AssertionError):
        run_hf_trainer(["hi"], tmp_path, distributed=False)

import pytest
import torch

from codex_ml.models import MiniLM, MiniLMConfig
from training.data_utils import TextDataset
from training.functional_training import TrainCfg, run_custom_trainer


class _Tok:
    vocab = {str(i): i for i in range(5)}

    def encode(self, txt: str) -> list[int]:
        return [self.vocab[t] for t in txt.split()]


def _setup(tmp_path):
    tok = _Tok()
    ds = TextDataset(["0 1"], tok, block_size=2)
    model = MiniLM(MiniLMConfig(vocab_size=5, n_layers=1, d_model=8, n_heads=1, max_seq_len=2))
    cfg = TrainCfg(
        epochs=0,
        batch_size=1,
        max_steps=0,
        checkpoint_dir=str(tmp_path),
    )
    return model, tok, ds, cfg


def _patch_cuda(monkeypatch, deterministic: bool) -> None:
    calls = {"count": 0}

    def fake_is_available() -> bool:
        calls["count"] += 1
        return calls["count"] == 1

    monkeypatch.setattr(torch.cuda, "is_available", fake_is_available)
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

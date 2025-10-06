import pytest

from codex.training import TrainCfg, run_custom_trainer
from codex_ml.models import MiniLM, MiniLMConfig
from training.data_utils import TextDataset, split_texts

pytestmark = pytest.mark.requires_torch

torch = pytest.importorskip("torch")


class _Tok:
    vocab = {str(i): i for i in range(6)}

    def encode(self, txt: str) -> list[int]:
        return [self.vocab[t] for t in txt.split()]


def _build_ds():
    texts = ["0 1 2 3 4 5"] * 4
    train_txt, val_txt = split_texts(texts, seed=0)
    tok = _Tok()
    return (
        tok,
        TextDataset(train_txt, tok, block_size=6),
        TextDataset(val_txt, tok, block_size=6),
    )


def test_checkpoint_resume(tmp_path) -> None:
    tok, train_ds, val_ds = _build_ds()

    # Baseline training without interruption
    base_model = MiniLM(
        MiniLMConfig(vocab_size=6, n_layers=1, d_model=16, n_heads=2, max_seq_len=6)
    )
    base_cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        log_every=1,
        save_every=2,
        max_steps=4,
        checkpoint_dir=str(tmp_path / "base"),
    )
    run_custom_trainer(base_model, tok, train_ds, val_ds, base_cfg)
    base_state = {k: v.clone() for k, v in base_model.state_dict().items()}

    # Train, save checkpoint mid-epoch, then resume
    model = MiniLM(MiniLMConfig(vocab_size=6, n_layers=1, d_model=16, n_heads=2, max_seq_len=6))
    ckpt_dir = tmp_path / "ckpts"
    cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        log_every=1,
        save_every=2,
        max_steps=2,
        checkpoint_dir=str(ckpt_dir),
    )
    run_custom_trainer(model, tok, train_ds, val_ds, cfg)
    ckpt = ckpt_dir / "step2.ptz"
    assert ckpt.exists()
    cfg2 = TrainCfg(
        epochs=1,
        batch_size=2,
        log_every=1,
        max_steps=4,
        checkpoint_dir=str(ckpt_dir),
        resume_from=str(ckpt),
    )
    result = run_custom_trainer(model, tok, train_ds, val_ds, cfg2)
    assert result["global_step"] == 4
    for k, v in base_state.items():
        assert torch.allclose(model.state_dict()[k], v)

import pytest

from codex_ml.models import MiniLM, MiniLMConfig
from training.codex.training import TrainCfg, run_custom_trainer
from training.data_utils import TextDataset, split_texts


class _Tok:
    vocab = {str(i): i for i in range(5)}

    def encode(self, txt: str) -> list[int]:
        return [self.vocab[t] for t in txt.split()]


def _has_peft() -> bool:
    try:  # pragma: no cover - optional dependency
        import peft  # noqa: F401

        return True
    except Exception:
        return False


@pytest.mark.skipif(not _has_peft(), reason="peft not installed")
def test_lora_parameters_trainable(tmp_path) -> None:
    texts = ["0 1 2 3 4"] * 2
    train_txt, val_txt = split_texts(texts, seed=0)
    tok = _Tok()
    train_ds = TextDataset(train_txt, tok, block_size=5)
    val_ds = TextDataset(val_txt, tok, block_size=5)
    model = MiniLM(MiniLMConfig(vocab_size=5, n_layers=1, d_model=16, n_heads=2, max_seq_len=5))
    cfg = TrainCfg(
        epochs=1,
        batch_size=2,
        max_steps=1,
        use_lora=True,
        log_every=10,
        checkpoint_dir=str(tmp_path),
    )
    run_custom_trainer(model, tok, train_ds, val_ds, cfg)
    trainable = [n for n, p in model.named_parameters() if p.requires_grad]
    assert any("lora" in n for n in trainable)
    assert any("lora" not in n and not p.requires_grad for n, p in model.named_parameters())

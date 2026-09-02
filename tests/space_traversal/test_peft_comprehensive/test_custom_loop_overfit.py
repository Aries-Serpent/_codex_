"""
Test Custom Loop Overfit

Test module for custom loop overfit.
"""

import pytest

pytest.importorskip("numpy", reason="numpy required")


from codex.training import TrainCfg, run_custom_trainer

from codex_ml.models import MiniLM, MiniLMConfig
from training.data_utils import TextDataset, split_texts


@pytest.fixture(autouse=True)
def disable_torch_profiler_and_meta(monkeypatch):
    """Disable PyTorch profiler and force CPU device to avoid meta tensor issues."""
    try:
        import torch
        import torch.profiler as profiler_module

        # Disable profiler record function to prevent Protocol isinstance errors
        if hasattr(profiler_module, "_record_function_enter"):
            monkeypatch.setattr(
                profiler_module, "_record_function_enter", lambda *args, **kwargs: None
            )
        if hasattr(profiler_module, "_record_function_exit"):
            monkeypatch.setattr(
                profiler_module, "_record_function_exit", lambda *args, **kwargs: None
            )

        # Force CPU device to avoid meta tensor initialization issues
        torch.set_default_device("cpu")

    except (ImportError, AttributeError):
        _ = None  # PyTorch profiler not available or already disabled


class _Tok:
    vocab = {str(i): i for i in range(10)}

    def encode(self, txt: str) -> list[int]:
        return [self.vocab[t] for t in txt.split()]


def test_overfit_tiny(tmp_path) -> None:
    texts = ["0 1 2 3 4 5 6 7 8 9"] * 4
    train_txt, val_txt = split_texts(texts, seed=0)
    tok = _Tok()
    train_ds = TextDataset(train_txt, tok, block_size=10)
    val_ds = TextDataset(val_txt, tok, block_size=10)
    model = MiniLM(MiniLMConfig(vocab_size=10, n_layers=1, d_model=16, n_heads=2, max_seq_len=10))
    cfg = TrainCfg(epochs=3, batch_size=2, log_every=1, save_every=0, checkpoint_dir=str(tmp_path))
    result = run_custom_trainer(model, tok, train_ds, val_ds, cfg)
    assert result["history"][0] > result["history"][-1], "Value must be greater than zero"

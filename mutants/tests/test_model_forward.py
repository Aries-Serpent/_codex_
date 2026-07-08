"""MiniLM forward pass shape test."""

import sys

import pytest

torch = pytest.importorskip("torch", reason="torch not installed")

_TORCH_312_BUG = sys.version_info >= (3, 12) and torch.__version__.startswith("2.")

from codex_ml.models import MiniLM, MiniLMConfig


@pytest.mark.ml
@pytest.mark.skipif(_TORCH_312_BUG, reason="PyTorch 2.x + Python 3.12 isinstance union bug")
def test_minilm_forward_shape():
    cfg = MiniLMConfig(vocab_size=100, d_model=32, n_layers=2, n_heads=4)
    model = MiniLM(cfg)
    x = torch.randint(0, cfg.vocab_size, (2, 8))
    logits = model(x)
    assert logits.shape == (2, 8, cfg.vocab_size)

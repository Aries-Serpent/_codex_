"""MiniLM forward pass shape test."""

import pytest
import torch

from codex_ml.models import MiniLM, MiniLMConfig


@pytest.mark.ml
def test_minilm_forward_shape():
    cfg = MiniLMConfig(vocab_size=100, d_model=32, n_layers=2, n_heads=4)
    model = MiniLM(cfg)
    x = torch.randint(0, cfg.vocab_size, (2, 8))
    logits = model(x)
    assert logits.shape == (2, 8, cfg.vocab_size)

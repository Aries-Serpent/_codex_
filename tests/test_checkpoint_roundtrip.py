from pathlib import Path

import torch

from codex_ml.models import MiniLM, MiniLMConfig


def test_checkpoint_roundtrip(tmp_path: Path):
    cfg = MiniLMConfig(vocab_size=5, n_layers=1, d_model=8, n_heads=2, max_seq_len=4)
    model = MiniLM(cfg)
    for p in model.parameters():
        torch.nn.init.constant_(p, 0.5)

    model.save_pretrained(tmp_path)
    reloaded = MiniLM.from_pretrained(tmp_path)

    for k in model.state_dict():
        assert torch.equal(model.state_dict()[k], reloaded.state_dict()[k])

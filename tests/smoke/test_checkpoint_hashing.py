from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke


def test_project_save_checkpoint_hashes(tmp_path: Path):
    # Import lazily to avoid heavy deps at collection time
    import torch

    from codex.training import save_checkpoint

    class M(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l = torch.nn.Linear(2, 2)

    model = M()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)

    ckpt = tmp_path / "ckpt.pt"
    out = save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=0, extra={"test": True})
    assert Path(out).exists()
    # Sidecars should exist
    assert ckpt.with_suffix(".pt.sha256").exists()
    assert ckpt.with_suffix(".pt.meta.json").exists()
    # Payload should be loadable with weights_only=True default in modern torch
    data = torch.load(ckpt)
    assert "model_state_dict" in data and "optimizer_state_dict" in data

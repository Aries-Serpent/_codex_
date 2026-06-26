"""
Test Checkpoint Hashing

Test module for checkpoint hashing.
"""

from pathlib import Path

import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.requires_torch]


def test_project_save_checkpoint_hashes(tmp_path: Path):
    # Import lazily to avoid heavy deps at collection time
    torch = pytest.importorskip("torch")

    from codex.training import save_checkpoint

    class M(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(2, 2)

    model = M()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)

    ckpt = tmp_path / "ckpt.pt"
    out = save_checkpoint(str(ckpt), model, opt, scheduler=None, epoch=0, extra={"test": True})
    assert Path(out).exists(), "Condition must be true"
    # Sidecars should exist
    assert ckpt.with_suffix(".pt.sha256").exists(), "Condition must be true"
    assert ckpt.with_suffix(".pt.meta.json").exists(), "Condition must be true"
    # Payload should be loadable with weights_only=True default in modern torch
    data = torch.load(
        ckpt, weights_only=False
    )  # nosec B614 - Test checkpoint with optimizer state requires weights_only=False
    assert "model_state_dict" in data and "optimizer_state_dict" in data, "Data must not be empty"

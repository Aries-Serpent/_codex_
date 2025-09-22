from __future__ import annotations

from pathlib import Path

import pytest

from codex_ml.utils.checkpointing import (
    TORCH_AVAILABLE,
    load_checkpoint,
    save_checkpoint,
)

pytestmark = pytest.mark.skipif(not TORCH_AVAILABLE, reason="requires torch")


def test_save_and_load_checkpoint(tmp_path: Path) -> None:
    import torch

    if not hasattr(torch, "nn") or not hasattr(torch.nn, "Linear"):
        pytest.skip("torch.nn Linear unavailable", allow_module_level=False)

    model = torch.nn.Linear(2, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    checkpoint_path = tmp_path / "unit.ckpt"
    save_checkpoint(
        str(checkpoint_path), model, optimizer, scheduler=None, epoch=1, extra={"seed": 42}
    )

    assert checkpoint_path.exists()

    payload = load_checkpoint(checkpoint_path)
    assert isinstance(payload, dict)
    assert payload.get("epoch") == 1
    extra = payload.get("extra", {})
    if isinstance(extra, dict):
        assert extra.get("seed") == 42

"""
Test Checkpoint Manifest

Test module for checkpoint manifest.
"""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="numpy required")

import json
from pathlib import Path

from training import checkpointing


def _require_torch():
    torch = pytest.importorskip("torch")
    if not hasattr(torch, "nn") or not hasattr(torch, "optim"):
        pytest.skip("torch.nn and torch.optim are required for checkpoint tests")
    return torch


def test_save_checkpoint_writes_manifest(tmp_path: Path) -> None:
    torch = _require_torch()

    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    manifest = {"git": "deadbeef", "cfg": {"seed": 42}}

    checkpoint_path = checkpointing.save_checkpoint(
        model,
        optimizer,
        epoch=1,
        val_metric=0.1234,
        out_dir=tmp_path,
        manifest=manifest,
    )

    manifest_path = checkpoint_path.parent / "manifest.json"
    assert manifest_path.exists(), "Condition must be true"

    with manifest_path.open("r", encoding="utf-8") as handle:
        saved_manifest = json.load(handle)

    assert saved_manifest == manifest, "saved_manifest is not valid"

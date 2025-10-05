from __future__ import annotations

import json
import random

import pytest

pytest.importorskip("torch")

import torch
from torch import nn

from training.checkpoint_manager import CheckpointManager
from codex_ml.utils.checkpointing import build_payload_bytes, load_payload


def test_checkpoint_manager_persists_rng(tmp_path):
    model = nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    manager = CheckpointManager(tmp_path)

    random.seed(123)
    torch.manual_seed(123)
    baseline_rand = random.random()
    baseline_tensor = torch.rand(1)

    payload = build_payload_bytes(model, optimizer, rng_state=True)
    path = manager.save_now(1, payload, {"loss": 1.0}, rng_state=True)

    # Advance RNG states
    random.random()
    torch.rand(1)

    load_payload(str(path), model, optimizer)
    restored_rand = random.random()
    restored_tensor = torch.rand(1)

    assert abs(restored_rand - baseline_rand) < 1e-12
    assert torch.allclose(restored_tensor, baseline_tensor)

    meta = json.loads(path.with_suffix(".meta.json").read_text())
    assert meta["metrics"]["loss"] == 1.0
    assert "rng" in meta and meta["rng"]

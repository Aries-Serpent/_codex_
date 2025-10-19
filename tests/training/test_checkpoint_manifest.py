from __future__ import annotations

import importlib.util
import json
import pickle
from pathlib import Path
from types import SimpleNamespace

from src.training import checkpointing


def _use_stub_torch() -> bool:
    return (
        importlib.util.find_spec("torch.nn") is None
        or importlib.util.find_spec("torch.optim") is None
    )


def test_save_checkpoint_writes_manifest(tmp_path: Path) -> None:
    manifest = {"git": "deadbeef", "cfg": {"seed": 42}}

    if _use_stub_torch():
        fake_torch = SimpleNamespace(
            save=lambda payload, filename: Path(filename).write_bytes(pickle.dumps(payload))
        )

        class _StubModel:
            def state_dict(self) -> dict[str, object]:
                return {"weight": [1.0]}

        class _StubOptimizer:
            def state_dict(self) -> dict[str, object]:
                return {"lr": 0.1}

        model = _StubModel()
        optimizer = _StubOptimizer()

        original_torch = checkpointing.torch
        original_snapshot = checkpointing.snapshot_rng_state
        checkpointing.torch = fake_torch
        checkpointing.snapshot_rng_state = lambda: checkpointing.RNGState()
        try:
            checkpoint_path = checkpointing.save_checkpoint(
                model,
                optimizer,
                epoch=1,
                val_metric=0.123,
                out_dir=tmp_path,
                manifest=manifest,
            )
        finally:
            checkpointing.torch = original_torch
            checkpointing.snapshot_rng_state = original_snapshot
    else:
        import torch

        class _TinyModel(torch.nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.layer = torch.nn.Linear(2, 2)

        model = _TinyModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

        checkpoint_path = checkpointing.save_checkpoint(
            model,
            optimizer,
            epoch=1,
            val_metric=0.123,
            out_dir=tmp_path,
            manifest=manifest,
        )

    manifest_path = tmp_path / "manifest.json"

    assert checkpoint_path.exists()
    assert manifest_path.exists()

    with manifest_path.open("r", encoding="utf-8") as fh:
        loaded = json.load(fh)

    assert loaded == manifest

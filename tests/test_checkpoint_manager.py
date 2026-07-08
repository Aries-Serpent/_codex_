"""
Test Checkpoint Manager

Test module for checkpoint manager.
"""

from __future__ import annotations

import types
from pathlib import Path

import pytest

from codex_ml.utils import checkpoint_manager
from codex_ml.utils.checkpoint_manager import load_checkpoint, save_checkpoint
from codex_ml.utils.safe_pickle import safe_pickle_dump


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "checkpoints" / "step-1.pt"
    state = {"epoch": 1, "loss": 0.5}
    save_checkpoint(state, target)
    loaded = load_checkpoint(target)
    assert loaded == state, "loaded is not valid"


def test_prunes_old_checkpoints(tmp_path: Path) -> None:
    root = tmp_path / "ckpts"
    for step in range(4):
        save_checkpoint({"step": step}, root / f"ckpt-{step}.pt", keep_last_k=2)
    remaining = sorted(p.name for p in root.glob("*.pt"))
    assert remaining == ["ckpt-2.pt", "ckpt-3.pt"]


def test_load_missing_checkpoint(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_checkpoint(tmp_path / "missing.pt")


def test_load_checkpoint_pickle_fallback_when_torch_available(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that load_checkpoint falls back to pickle when torch.load fails.

    SECURITY NOTE: This test validates the fallback path when torch.load raises
    an error. The fallback file is created by this test through the trusted
    safe_pickle wrapper, making it a trusted source. In production, checkpoints
    should prefer torch.save or safe_pickle_load with RestrictedUnpickler.
    """
    target = tmp_path / "pickled.pt"
    payload = {"epoch": 3}
    safe_pickle_dump(payload, str(target))

    def raise_invalid(*_: object, **__: object) -> None:
        raise RuntimeError("invalid header")

    dummy_torch = types.SimpleNamespace(load=raise_invalid)
    monkeypatch.setattr(checkpoint_manager, "torch", dummy_torch)

    loaded = checkpoint_manager.load_checkpoint(target)
    assert loaded == payload, "loaded is not valid"

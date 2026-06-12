"""
Test Checkpoint Manager

Test module for checkpoint manager.
"""

from __future__ import annotations

import pickle
import types
from pathlib import Path

import pytest

from codex_ml.utils import checkpoint_manager
from codex_ml.utils.checkpoint_manager import load_checkpoint, save_checkpoint


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "checkpoints" / "step-1.pt"
    state = {"epoch": 1, "loss": 0.5}
    save_checkpoint(state, target)
    loaded = load_checkpoint(target)
    assert loaded == state


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
    an error. The pickle.load here is operating on a file WE just created in the
    test, making it a trusted source. In production, checkpoints should use
    torch.save or safe_pickle_load with RestrictedUnpickler.
    """
    target = tmp_path / "pickled.pt"
    payload = {"epoch": 3}
    with target.open("wb") as handle:
        # nosec B301 - Test fixture: we're creating a known-safe pickle for testing
        # nosemgrep: semgrep_rules.py-pickle-dump
        pickle.dump(payload, handle)

    def raise_invalid(*_: object, **__: object) -> None:
        raise RuntimeError("invalid header")

    dummy_torch = types.SimpleNamespace(load=raise_invalid)
    monkeypatch.setattr(checkpoint_manager, "torch", dummy_torch)

    loaded = checkpoint_manager.load_checkpoint(target)
    assert loaded == payload

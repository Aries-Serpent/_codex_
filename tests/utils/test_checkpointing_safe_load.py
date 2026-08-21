"""
Test Checkpointing Safe Load

Test module for checkpointing safe load.
"""

from __future__ import annotations

import inspect
import pickle
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

# Resolve load_checkpoint from either layout:
try:  # prefer top-level utils layout if available
    from utils.checkpointing import load_checkpoint  # type: ignore
except ImportError:  # pragma: no cover - fallback to package layout
    from codex_ml.utils.checkpointing import load_checkpoint  # type: ignore


def _require_torch() -> Any:
    """Return a real torch module or skip with a helpful reason."""
    torch = pytest.importorskip("torch")
    missing = [name for name in ("save", "load", "randn") if not hasattr(torch, name)]
    if missing:
        pytest.skip(f"PyTorch stub missing attributes: {', '.join(missing)}")
    return torch


def _make_state_dict(torch: Any) -> Mapping[str, Any]:
    """Create a minimal, tensor-only state-dict (no custom objects)."""
    return {
        "linear.weight": torch.randn(2, 3),
        "linear.bias": torch.randn(2),
    }


def test_load_checkpoint_safe_roundtrip(tmp_path: Path) -> None:
    """load_checkpoint(safe=True) succeeds when torch supports weights_only.

    Behavior:
      - If current torch exposes the `weights_only` parameter, the safe load
        should succeed and return a plain mapping of tensors.
      - Otherwise, our implementation raises RuntimeError (safer default).
    """
    torch = _require_torch()
    state = _make_state_dict(torch)
    ckpt_path = tmp_path / "state.pt"
    torch.save(state, ckpt_path)

    supports_weights_only = "weights_only" in inspect.signature(torch.load).parameters

    if supports_weights_only:
        out = load_checkpoint(ckpt_path, safe=True, map_location="cpu")
        assert isinstance(out, Mapping)
        assert set(out.keys()) == set(state.keys()), "Condition must be true"
        for t in out.values():
            # sanity checks that we got tensors back
            assert hasattr(t, "shape")
            assert getattr(t, "dtype", None) is not None
            # be strict: ensure values are real tensors
            assert torch.is_tensor(t), "t is not valid"
    else:
        with pytest.raises(RuntimeError):
            load_checkpoint(ckpt_path, safe=True, map_location="cpu")


def test_load_checkpoint_trusted_path(tmp_path: Path) -> None:
    """load_checkpoint(safe=False) must round-trip regardless of weights_only."""
    torch = _require_torch()
    state = _make_state_dict(torch)
    ckpt_path = tmp_path / "state.pt"
    torch.save(state, ckpt_path)

    out = load_checkpoint(ckpt_path, safe=False, map_location="cpu")
    assert isinstance(out, Mapping)
    assert set(out.keys()) == set(state.keys()), "Condition must be true"
    for t in out.values():
        assert hasattr(t, "shape")
        assert torch.is_tensor(t), "t is not valid"


def test_load_checkpoint_legacy_weights_only_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """safe=True falls back when the runtime rejects the weights_only keyword."""
    torch = _require_torch()
    state = _make_state_dict(torch)
    ckpt_path = tmp_path / "legacy_state.pkl"
    ckpt_path.write_bytes(pickle.dumps(state))

    real_load = torch.load

    def fake_load(source: object, *args: object, **kwargs: object) -> object:
        if kwargs.get("weights_only") is True:
            raise TypeError("unexpected keyword argument 'weights_only'")
        return real_load(source, *args, **kwargs)

    fake_load.__signature__ = inspect.signature(real_load)  # type: ignore[attr-defined]

    monkeypatch.setattr(torch, "load", fake_load)

    out = load_checkpoint(ckpt_path, safe=True, map_location="cpu")
    assert isinstance(out, Mapping)
    assert set(out.keys()) == set(state.keys())
    for tensor in out.values():
        assert torch.is_tensor(tensor)

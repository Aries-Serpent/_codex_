from __future__ import annotations

import os
import random
import tempfile
from typing import Any, Dict

try:  # pragma: no cover - optional dependency
    import numpy as _np
except Exception:  # pragma: no cover - handle missing dependency
    _np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import torch as _torch
except Exception:  # pragma: no cover - handle missing dependency
    _torch = None  # type: ignore[assignment]


def _rng_state() -> Dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    if _np is None:
        raise RuntimeError("numpy is required to capture RNG state")

    state: Dict[str, Any] = {
        "torch": _torch.get_rng_state().tolist(),
        "python": random.getstate(),
        "numpy": _np.random.get_state(),
    }
    if _torch.cuda.is_available():
        state["cuda"] = [tensor.tolist() for tensor in _torch.cuda.get_rng_state_all()]
    else:
        state["cuda"] = None
    return state


def save_checkpoint(state: Dict[str, Any], path: str, archive_latest: bool = True) -> None:
    """Atomically persist a checkpoint along with RNG metadata."""

    if _torch is None:
        raise RuntimeError("torch is required to save checkpoints")

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path) or None)
    os.close(fd)
    augmented = dict(state)
    augmented["_rng"] = _rng_state()
    _torch.save(augmented, tmp_path)
    os.replace(tmp_path, path)
    if archive_latest and os.path.islink(path):
        os.unlink(path)


def load_checkpoint(path: str, device: str = "cpu") -> Dict[str, Any]:
    if _torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    state = _torch.load(path, map_location=device)
    rng = state.pop("_rng", None)
    if rng:
        _torch.set_rng_state(_torch.tensor(rng["torch"], dtype=_torch.uint8))
        if _np is not None:
            try:
                _np.random.set_state(rng["numpy"])
            except Exception:
                pass
        try:
            random.setstate(rng["python"])
        except Exception:
            pass
        if rng.get("cuda") and _torch.cuda.is_available():
            # Best-effort restoration for CUDA RNGs. Device mapping is context dependent.
            for idx, tensor_state in enumerate(rng["cuda"]):
                try:
                    _torch.cuda.set_rng_state(
                        _torch.tensor(tensor_state, dtype=_torch.uint8), device=idx
                    )
                except Exception:
                    continue
    return state

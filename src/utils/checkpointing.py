"""
Legacy checkpointing manager (compat shim).

Prefer codex_ml.utils.checkpointing.CheckpointManager for new code.
"""

from __future__ import annotations

import random as _random
from typing import Any, Dict

import warnings as _warnings

_warnings.warn(
    "src.utils.checkpointing is legacy; use codex_ml.utils.checkpointing for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical manager where compatible, to reduce duplication.
try:  # pragma: no cover - mirror class
    from codex_ml.utils.checkpointing import CheckpointManager  # type: ignore
except Exception:  # pragma: no cover - defensive
    CheckpointManager = object  # type: ignore[misc,assignment]


try:  # pragma: no cover - prefer canonical RNG helpers
    from codex_ml.utils.checkpoint_core import (  # type: ignore
        dump_rng_state as _canonical_dump_rng_state,
        load_rng_state as _canonical_load_rng_state,
        set_seed as _canonical_set_seed,
    )
except Exception:  # pragma: no cover - canonical RNG helpers unavailable
    _canonical_dump_rng_state = None  # type: ignore[assignment]
    _canonical_load_rng_state = None  # type: ignore[assignment]
    _canonical_set_seed = None  # type: ignore[assignment]

try:  # pragma: no cover - optional numpy
    import numpy as _np
except Exception:  # pragma: no cover - numpy optional
    _np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional torch
    import torch as _torch
except Exception:  # pragma: no cover - torch optional
    _torch = None  # type: ignore[assignment]


# Optional helper aliases to ease migration of call-sites
def save_ckpt(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import save_checkpoint as _save  # type: ignore

    return _save(*args, **kwargs)


def verify_ckpt_integrity(*args, **kwargs):  # pragma: no cover - passthrough
    from codex_ml.utils.checkpoint_core import verify_checkpoint as _verify  # type: ignore

    return _verify(*args, **kwargs)


def dump_rng_state() -> Dict[str, Any]:  # pragma: no cover - passthrough
    """Capture RNG state while preserving legacy structure."""

    if _canonical_dump_rng_state is not None:
        return _canonical_dump_rng_state()

    state: Dict[str, Any] = {"python": _random.getstate()}
    if _np is not None:
        state["numpy"] = _np.random.get_state()
    if _torch is not None:
        torch_state = {"cpu": _torch.random.get_rng_state().tolist()}
        cuda_mod = getattr(_torch, "cuda", None)
        if cuda_mod is not None and callable(getattr(cuda_mod, "is_available", None)) and cuda_mod.is_available():
            torch_state["cuda"] = [s.tolist() for s in cuda_mod.get_rng_state_all()]  # pragma: no cover - cuda optional
        state["torch"] = torch_state
    return state


def load_rng_state(state: Dict[str, Any]) -> None:  # pragma: no cover - passthrough
    """Restore RNG state captured by :func:`dump_rng_state`."""

    if _canonical_load_rng_state is not None:
        _canonical_load_rng_state(state)
        return

    if "python" in state:
        _random.setstate(state["python"])
    if _np is not None and "numpy" in state:
        _np.random.set_state(state["numpy"])
    if _torch is not None and "torch" in state:
        torch_state = state["torch"]
        cpu_state = torch_state.get("cpu")
        if cpu_state is not None:
            _torch.random.set_rng_state(_torch.tensor(cpu_state, dtype=_torch.uint8))
        cuda_mod = getattr(_torch, "cuda", None)
        if (
            cuda_mod is not None
            and callable(getattr(cuda_mod, "is_available", None))
            and cuda_mod.is_available()
            and "cuda" in torch_state
        ):
            cuda_states = [
                _torch.tensor(entry, dtype=_torch.uint8)
                for entry in torch_state.get("cuda", [])
            ]
            cuda_mod.set_rng_state_all(cuda_states)


def set_seed(seed: int) -> None:  # pragma: no cover - passthrough
    """Seed available RNG backends with ``seed``."""

    if _canonical_set_seed is not None:
        _canonical_set_seed(seed)
        return

    _random.seed(seed)
    if _np is not None:
        _np.random.seed(seed)
    if _torch is not None:
        _torch.manual_seed(seed)
        cuda_mod = getattr(_torch, "cuda", None)
        if cuda_mod is not None and callable(getattr(cuda_mod, "is_available", None)) and cuda_mod.is_available():
            cuda_mod.manual_seed_all(seed)


__all__ = [
    "CheckpointManager",
    "save_ckpt",
    "verify_ckpt_integrity",
    "dump_rng_state",
    "load_rng_state",
    "set_seed",
]

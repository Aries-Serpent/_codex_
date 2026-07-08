"""Reproducibility utilities for _codex_.

This module centralizes simple helpers for:
- Setting global seeds across common RNG libraries (random, numpy, torch if present).
- Capturing a small snapshot of RNG-related state.

The goal is to provide a stable import path for future integrations with more
advanced MLOps reproducibility tooling, without introducing hard dependencies.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import random
import secrets
from dataclasses import asdict, dataclass
from typing import Any

logger = logging.getLogger(__name__)

_np_spec = importlib.util.find_spec("numpy")
if _np_spec is not None:
    import numpy as _np
else:  # pragma: no cover
    _np = None

_torch_spec = importlib.util.find_spec("torch")
if _torch_spec is not None:
    import torch as _torch
else:  # pragma: no cover
    _torch = None  # type: ignore[assignment]


@dataclass
class SeedConfig:
    """Simple container for seed configuration and environment hints."""

    seed: int
    env_var_name: str = "CODEX_GLOBAL_SEED"


def set_global_seed(seed: int, *, set_env: bool = True) -> SeedConfig:
    """set global RNG seeds for random / numpy / torch (if available).

    Parameters
    ----------
    seed:
        Integer seed to apply.
    set_env:
        If True, also write the seed to CODEX_GLOBAL_SEED env var for traceability.

    Returns
    -------
    SeedConfig
        The configuration that was applied.
    """
    random.seed(seed)

    if _np is not None:  # pragma: no cover - optional dep
        try:
            _np.random.seed(seed)
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover
            logger.debug("Suppressed exception in handler", exc_info=True)
    if _torch is not None:  # pragma: no cover - optional dep
        try:
            _torch.manual_seed(seed)
            if hasattr(_torch, "cuda"):
                try:
                    _torch.cuda.manual_seed_all(seed)
                except (ValueError, TypeError, RuntimeError):  # pragma: no cover
                    logger.debug("Suppressed exception in handler", exc_info=True)
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover
            logger.debug("Suppressed exception in handler", exc_info=True)
    if set_env:
        os.environ["CODEX_GLOBAL_SEED"] = str(seed)

    return SeedConfig(seed=seed)


def capture_rng_snapshot() -> dict[str, Any]:
    """Capture a tiny, implementation-agnostic snapshot of RNG-related state.

    This is not a full serialization of RNG engines; it is only a hint for
    logging and debugging. Real reproducibility should rely on:
    - set_global_seed(...)
    - recorded versions of dependencies
    - deterministic algorithm configs
    """
    snapshot: dict[str, Any] = {
        "env_seed": os.environ.get("CODEX_GLOBAL_SEED"),
    }

    snapshot["random_state_hint"] = secrets.token_hex(8)

    if _np is not None:  # pragma: no cover - optional dep
        try:
            snapshot["numpy_state_hint"] = float(_np.random.rand())
        except Exception:  # pragma: no cover
            snapshot["numpy_state_hint"] = None
    else:
        snapshot["numpy_state_hint"] = None

    if _torch is not None:  # pragma: no cover - optional dep
        try:
            snapshot["torch_rng_hint"] = float(_torch.rand(1).item())
        except Exception:  # pragma: no cover
            snapshot["torch_rng_hint"] = None
    else:
        snapshot["torch_rng_hint"] = None

    return snapshot


def seed_config_as_dict(cfg: SeedConfig) -> dict[str, Any]:
    """Convert SeedConfig to a dict (helper to keep dataclasses internal)."""
    return asdict(cfg)

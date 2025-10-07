"""Unified Training Orchestrator (Superseding preliminary patch)

Capabilities:
 - Backend strategy selection (functional / legacy) with easy future extension.
 - Deterministic seeding.
 - Resume support via consolidated checkpoint_core.
 - Callback dispatch points.
 - Deprecation channel for legacy loop.
 - Structured result dictionary.

Schema Alignment:
 - Checkpoint metadata uses schema_version=2 (see checkpoint_core).

Usage:
    from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
    cfg = UnifiedTrainingConfig(model_name="demo", epochs=1)
    run_unified_training(cfg)
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from codex_ml.training.strategies import (
    resolve_strategy,
    TrainingCallback,
    TrainingResult,
)
from codex_ml.utils.checkpoint_core import (
    save_checkpoint,
    load_checkpoint,
    capture_environment_summary,
)


try:  # optional torch
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


# ----------------------------- Config & Validation ----------------------------


@dataclass
class UnifiedTrainingConfig:
    model_name: str = "dummy"
    epochs: int = 1
    batch_size: int = 8
    grad_accum: int = 1
    learning_rate: float = 3e-4
    seed: int = 42
    output_dir: str = "runs/unified"
    backend: Optional[str] = None  # "functional" | "legacy" | None (auto)
    mlflow_enable: bool = False
    wandb_enable: bool = False
    grad_clip_norm: float | None = None
    dtype: str = "fp32"
    resume_from: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        errors: List[str] = []
        if self.epochs < 0:
            errors.append("epochs must be >= 0")
        if self.batch_size < 1:
            errors.append("batch_size must be >=1")
        if self.grad_accum < 1:
            errors.append("grad_accum must be >=1")
        if self.dtype not in {"fp32", "fp16", "bf16"}:
            errors.append("dtype must be one of {fp32, fp16, bf16}")
        if not (0 <= self.seed < 2**32):
            errors.append("seed must be in [0, 2**32)")
        if errors:
            raise ValueError("; ".join(errors))


# ------------------------------ Seeding & Helpers -----------------------------


def _seed_all(seed: int) -> None:
    import random

    random.seed(seed)
    try:
        import numpy as np  # type: ignore
    except Exception:  # pragma: no cover
        np = None  # type: ignore
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)
            except Exception:
                pass


def _auto_backend(cfg: UnifiedTrainingConfig) -> str:
    if cfg.backend:
        return cfg.backend
    return "functional"


# ------------------------------- Orchestrator ---------------------------------


def _emit_checkpoint_epoch(
    cfg: UnifiedTrainingConfig, epoch: int, state: Dict[str, Any], metrics: Dict[str, float]
) -> str:
    ckpt_dir = f"{cfg.output_dir}/epoch-{epoch}"
    payload = {
        "model_state": state.get("model_state"),
        "optimizer_state": state.get("optimizer_state"),
        "scheduler_state": state.get("scheduler_state"),
        "scaler_state": state.get("scaler_state"),
        "backend_name": state.get("backend_name"),
    }
    meta = {
        "epoch": epoch,
        "global_step": state.get("global_step"),
        "backend_name": state.get("backend_name"),
        "metrics": metrics,
        "environment": capture_environment_summary(),
        "schema_version": 2,
    }
    save_checkpoint(ckpt_dir, payload=payload, metadata=meta, include_rng=True)
    return ckpt_dir


def run_unified_training(
    cfg: UnifiedTrainingConfig,
    callbacks: Optional[Iterable[TrainingCallback]] = None,
) -> Dict[str, Any]:
    """Execute training under unified orchestrator."""
    start = time.time()
    _seed_all(cfg.seed)

    backend_name = _auto_backend(cfg)
    strategy = resolve_strategy(backend_name)

    # State object passed to callbacks (extendable)
    state: Dict[str, Any] = {
        "backend_name": backend_name,
        "global_step": 0,
        "resume_from": cfg.resume_from,
    }

    # Pre-resume load if requested
    if cfg.resume_from:
        try:
            loaded = load_checkpoint(cfg.resume_from)
            state.update({"resume_loaded": True, "resume_payload_keys": sorted(loaded.keys())})
        except Exception as exc:  # pragma: no cover
            state.update({"resume_error": repr(exc)})

    cbs = list(callbacks) if callbacks else []

    # Wrap strategy run
    result: TrainingResult = strategy.run(cfg, cbs, resume_from=cfg.resume_from)

    # Emit final synthetic checkpoint (epoch = cfg.epochs)
    final_status = 1.0 if result.status == "ok" else 0.0
    try:
        ckpt_path = _emit_checkpoint_epoch(
            cfg, cfg.epochs, state, {"final_status": final_status}
        )
        for cb in cbs:
            try:
                cb.on_checkpoint(cfg.epochs, ckpt_path, {"final_status": final_status}, state)
            except Exception:
                pass
    except Exception:
        pass

    return {
        "status": result.status,
        "backend": result.backend,
        "final_epoch": result.final_epoch,
        "output_dir": result.output_dir,
        "elapsed_s": round(time.time() - start, 4),
        "resume_from": cfg.resume_from,
    }


def _emit_legacy_warning(entrypoint: str, redirect: str) -> None:
    warnings.warn(
        (
            "codex_ml.training.unified_training.{entry} is deprecated and will be "
            "removed in a future release; use {redirect} instead."
        ).format(entry=entrypoint, redirect=redirect),
        DeprecationWarning,
        stacklevel=3,
    )


def train_loop(*args: Any, **kwargs: Any) -> Any:
    """Compatibility shim preserving the historical ``train_loop`` entrypoint."""

    _emit_legacy_warning(
        "train_loop",
        "codex_ml.train_loop.run_training or run_unified_training",
    )
    from codex_ml.train_loop import run_training as _legacy_train_loop

    return _legacy_train_loop(*args, **kwargs)


def functional_training(*args: Any, **kwargs: Any) -> Any:
    """Compatibility shim for ``functional_training`` callers."""

    _emit_legacy_warning(
        "functional_training",
        "codex_ml.training.legacy_api.run_functional_training or run_unified_training",
    )
    from codex_ml.training.legacy_api import run_functional_training as _legacy_functional

    return _legacy_functional(*args, **kwargs)


__all__ = [
    "UnifiedTrainingConfig",
    "run_unified_training",
    "train_loop",
    "functional_training",
]

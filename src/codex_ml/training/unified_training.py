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

import json
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from codex_ml.training.strategies import TrainingCallback, TrainingResult, resolve_strategy
from codex_ml.utils.checkpoint_core import CheckpointMeta, load_checkpoint, save_checkpoint

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
    keep_last: int = 3
    best_k: int = 0
    best_metric: str = "val_loss"

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


def _coerce_metric_value(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _emit_checkpoint_epoch(
    cfg: UnifiedTrainingConfig, epoch: int, state: Dict[str, Any], metrics: Dict[str, float]
) -> str:
    ckpt_dir = Path(cfg.output_dir) / f"epoch-{epoch}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_state: Dict[str, Any] = {
        "model_state": state.get("model_state"),
        "optimizer_state": state.get("optimizer_state"),
        "scheduler_state": state.get("scheduler_state"),
        "scaler_state": state.get("scaler_state"),
        "backend_name": state.get("backend_name"),
        "global_step": state.get("global_step"),
        "epoch": epoch,
        "metrics": metrics,
    }

    metric_value = _coerce_metric_value(metrics.get(cfg.best_metric))

    checkpoint_path, checkpoint_meta = save_checkpoint(
        ckpt_dir,
        state=checkpoint_state,
        metric_value=metric_value,
        metric_key=cfg.best_metric,
        config={
            "epoch": epoch,
            "metrics": metrics,
            "keep_last": cfg.keep_last,
            "best_k": cfg.best_k,
        },
    )

    _write_checkpoint_metadata(
        ckpt_dir,
        checkpoint_path,
        checkpoint_meta,
        epoch=epoch,
        state=state,
        metrics=metrics,
    )

    return str(ckpt_dir)


def _write_checkpoint_metadata(
    ckpt_dir: Path,
    checkpoint_path: Path,
    checkpoint_meta: CheckpointMeta,
    *,
    epoch: int,
    state: Dict[str, Any],
    metrics: Dict[str, float],
) -> None:
    payload: Dict[str, Any] = {
        "epoch": epoch,
        "global_step": state.get("global_step"),
        "metrics": metrics,
        "schema_version": checkpoint_meta.schema_version,
        "environment": checkpoint_meta.env,
        "checkpoint": {
            "file": checkpoint_path.name,
            "created_at": checkpoint_meta.created_at,
            "metric_key": checkpoint_meta.metric_key,
            "metric_value": checkpoint_meta.metric_value,
            "sha256": checkpoint_meta.sha256,
        },
    }
    if checkpoint_meta.git_sha is not None:
        payload["git_sha"] = checkpoint_meta.git_sha
    if checkpoint_meta.config_hash is not None:
        payload["config_hash"] = checkpoint_meta.config_hash
    if checkpoint_meta.rng:
        payload["rng"] = checkpoint_meta.rng

    try:
        (ckpt_dir / "metadata.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
    except Exception:  # pragma: no cover
        pass


def run_unified_training(
    cfg: UnifiedTrainingConfig,
    callbacks: Optional[Iterable[TrainingCallback]] = None,
    ndjson_log_path: Optional[str] = None,
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
            loaded_state, _ = load_checkpoint(cfg.resume_from)
            if isinstance(loaded_state, dict):
                payload_keys = sorted(loaded_state.keys())
            else:
                payload_keys = []
            state.update({"resume_loaded": True, "resume_payload_keys": payload_keys})
        except Exception as exc:  # pragma: no cover
            state.update({"resume_error": repr(exc)})

    cbs = list(callbacks) if callbacks else []
    if ndjson_log_path:
        from codex_ml.callbacks.ndjson_logger import NDJSONLogger

        cbs.append(NDJSONLogger(ndjson_log_path))

    # Wrap strategy run
    result: TrainingResult = strategy.run(cfg, cbs, resume_from=cfg.resume_from)

    # Emit final synthetic checkpoint (epoch = cfg.epochs)
    final_status = 1.0 if result.status == "ok" else 0.0
    try:
        ckpt_path = _emit_checkpoint_epoch(cfg, cfg.epochs, state, {"final_status": final_status})
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

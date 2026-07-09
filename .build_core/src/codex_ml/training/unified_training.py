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

import contextlib
import importlib
import importlib.util
import json
import logging
import os
import time
import warnings
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from codex_ml.logging.mlflow_guard import (
    init_mlflow_safe,
    log_metric_safe,
    log_params_safe,
)
from codex_ml.training import strategies
from codex_ml.training.device_strategy import DeviceConfig, DeviceMapper
from codex_ml.training.rng_checkpoint import RNGState
from codex_ml.training.strategies import (
    TrainingCallback,
    TrainingResult,
    resolve_strategy,
)
from codex_ml.utils import checkpoint_core as _ckpt_core
from codex_ml.utils.checkpoint_core import CheckpointMeta
from codex_ml.utils.repro import capture_environment, set_seed

# Re-export checkpoint_core functions under patchable module-level names so
# that tests can monkeypatch `codex_ml.training.unified_training.save_checkpoint`
# and `codex_ml.training.unified_training.load_checkpoint`.
save_checkpoint = _ckpt_core.save_checkpoint
load_checkpoint = _ckpt_core.load_checkpoint

logger = logging.getLogger(__name__)

try:  # optional torch
    import torch
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]


# ----------------------------- Config & Validation ----------------------------


def _to_plain_container(value: Any) -> Any:
    """Best-effort conversion of OmegaConf containers to builtin types."""

    if isinstance(value, Mapping):
        return {k: _to_plain_container(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_plain_container(v) for v in value]
    return value


def _materialise_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("continual sections must be mappings")
    return {str(k): _to_plain_container(v) for k, v in value.items()}


@dataclass
class ContinualPhase:
    name: str
    epochs: int = 1
    dataset: dict[str, Any] = field(default_factory=dict)
    replay_ratio: float | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if int(self.epochs) < 1:
            raise ValueError("continual phase epochs must be >= 1")
        self.epochs = int(self.epochs)
        if isinstance(self.dataset, Mapping):
            self.dataset = _materialise_mapping(self.dataset)
        if self.replay_ratio is not None:
            ratio = float(self.replay_ratio)
            if not 0.0 <= ratio <= 1.0:
                raise ValueError("continual replay_ratio must be between 0 and 1")
            self.replay_ratio = ratio


@dataclass
class ContinualConfig:
    strategy: str = "replay"
    buffer_size: int | None = None
    replay_ratio: float | None = None
    active_corpus: str | None = None
    corpora: dict[str, Any] = field(default_factory=dict)
    curriculum: dict[str, Any] = field(default_factory=dict)
    rehearsal: dict[str, Any] = field(default_factory=dict)
    phases: list[ContinualPhase] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.buffer_size is not None:
            self.buffer_size = int(self.buffer_size)
            if self.buffer_size < 0:
                raise ValueError("continual buffer_size must be >= 0")
        if self.replay_ratio is not None:
            ratio = float(self.replay_ratio)
            if not 0.0 <= ratio <= 1.0:
                raise ValueError("continual replay_ratio must be between 0 and 1")
            self.replay_ratio = ratio
        if self.active_corpus is not None:
            self.active_corpus = str(self.active_corpus)
        self.corpora = _materialise_mapping(self.corpora)
        self.curriculum = _materialise_mapping(self.curriculum)
        self.rehearsal = _materialise_mapping(self.rehearsal)
        raw_phases: Sequence[Any] | None = self.phases
        normalised: list[ContinualPhase] = []
        for phase in raw_phases or []:
            if isinstance(phase, ContinualPhase):
                normalised.append(phase)
            elif isinstance(phase, Mapping):
                normalised.append(ContinualPhase(**_materialise_mapping(phase)))
            else:
                raise TypeError("continual phases must be mappings or ContinualPhase instances")
        self.phases = normalised


@dataclass
class UnifiedTrainingConfig:
    model_name: str = "dummy"
    epochs: int = 1
    batch_size: int = 8
    grad_accum: int = 1
    learning_rate: float = 3e-4
    seed: int | None = 42
    device: str | None = None  # explicit device override ("cpu", "cuda", "auto", …)
    output_dir: str = "runs/unified"
    checkpoint_dir: str | None = None  # explicit checkpoint directory override
    config_version: str = "1.0"
    dataset_version: str | None = None
    deterministic: bool = True
    auto_capture_env: bool = True
    backend: str | None = None  # "functional" | "legacy" | None (auto)
    mlflow_enable: bool = False
    mlflow_tracking: bool = False  # alias accepted by comprehensive tests
    wandb_enable: bool = False
    enable_eval_callback: bool = True
    enable_logging_callback: bool = True
    grad_clip_norm: float | None = None
    dtype: str = "fp32"
    resume_from: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
    keep_last: int = 3
    best_k: int = 0
    best_metric: str = "val_loss"
    continual: Any = None  # ContinualConfig | dict[str, Any] | None - validated in __post_init__
    continual_phases: list[Any] | None = (
        None  # list[ContinualPhase] for multi-phase continual learning
    )
    callbacks: list[Any] | None = None  # list of TrainingCallback instances

    def __post_init__(self) -> None:
        errors: list[str] = []
        # model_name must be a non-empty string
        if self.model_name is None:
            errors.append("model_name must not be None")
        # epochs must be a positive integer (0 is not a valid training run)
        if self.epochs is not None and self.epochs < 1:
            errors.append("epochs must be >= 1")
        if self.batch_size < 1:
            errors.append("batch_size must be >=1")
        if self.grad_accum < 1:
            errors.append("grad_accum must be >=1")
        if self.dtype not in {"fp32", "fp16", "bf16"}:
            errors.append("dtype must be one of {fp32, fp16, bf16}")
        if self.seed is not None:
            try:
                seed_int = int(self.seed)
            except (TypeError, ValueError):
                errors.append("seed must be an integer or None")
                seed_int = None
            if seed_int is not None and not (0 <= seed_int < 2**32):
                errors.append("seed must be in [0, 2**32)")
            else:
                self.seed = seed_int if seed_int is not None else self.seed
        self.config_version = str(self.config_version)
        self.deterministic = bool(self.deterministic)
        self.auto_capture_env = bool(self.auto_capture_env)
        # sync mlflow_tracking → mlflow_enable so either alias works
        if self.mlflow_tracking and not self.mlflow_enable:
            self.mlflow_enable = True
        if self.continual is not None and not isinstance(self.continual, ContinualConfig):
            if isinstance(self.continual, Mapping):
                self.continual = ContinualConfig(**dict(self.continual))
            else:
                errors.append("continual must be a ContinualConfig or mapping")
        if errors:
            raise ValueError("; ".join(errors))


# ------------------------------ Seeding & Helpers -----------------------------


def _seed_all(seed: int, *, deterministic: bool = True) -> None:
    set_seed(seed, deterministic=deterministic)

    # Preserve legacy behavior for tests and call-sites that monkeypatch the
    # module-level torch reference directly.
    if torch is None:
        return

    manual_seed = getattr(torch, "manual_seed", None)
    if callable(manual_seed):
        manual_seed(seed)

    cuda = getattr(torch, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)) and cuda.is_available():
        manual_seed_all = getattr(cuda, "manual_seed_all", None)
        if callable(manual_seed_all):
            manual_seed_all(seed)


def _auto_backend(cfg: UnifiedTrainingConfig) -> str:
    if cfg.backend:
        return cfg.backend
    return "functional"


def distributed_context() -> dict[str, Any]:
    """Capture distributed training context from environment and torch (best effort)."""

    context: dict[str, Any] = {
        "world_size": int(os.getenv("WORLD_SIZE", "1") or 1),
        "rank": int(os.getenv("RANK", "0") or 0),
        "local_rank": int(os.getenv("LOCAL_RANK", os.getenv("LOCALWORLD", "0")) or 0),
    }
    if torch is not None:
        try:  # pragma: no cover - torch.distributed is optional
            import torch.distributed as dist

            if dist.is_available() and dist.is_initialized():
                context["backend"] = dist.get_backend()
                context["world_size"] = max(context["world_size"], dist.get_world_size())
                context["rank"] = max(context["rank"], dist.get_rank())
        except (ValueError, TypeError, RuntimeError):
            logger.debug("Exception occurred", exc_info=True)
            context.setdefault("backend_error", "unavailable")
    return context


# ------------------------------- Orchestrator ---------------------------------


def _coerce_metric_value(raw: Any) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        logger.debug("Exception caught, returning", exc_info=True)
        return None


def _emit_checkpoint_epoch(
    cfg: UnifiedTrainingConfig,
    epoch: int,
    state: dict[str, Any],
    metrics: dict[str, float],
    *,
    rng_state: RNGState | None = None,
) -> str:
    ckpt_dir = Path(cfg.output_dir) / f"epoch-{epoch}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_state: dict[str, Any] = {
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
        metadata={"epoch": epoch, "metrics": metrics},
        metric_value=metric_value,
        metric_key=cfg.best_metric,
        config={
            "epoch": epoch,
            "metrics": metrics,
            "keep_last": cfg.keep_last,
            "best_k": cfg.best_k,
            "config_version": cfg.config_version,
            "dataset_version": cfg.dataset_version,
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

    if rng_state is not None:
        try:
            rng_state.capture()
            rng_path = RNGState.path_for_checkpoint(checkpoint_path)
            rng_state.save_to_file(rng_path)
            state.setdefault("rng_state_paths", []).append(str(rng_path))
        except (IOError, OSError) as exc:  # pragma: no cover - defensive
            state.setdefault("rng_state_error", repr(exc))

    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            log_metric_safe(f"checkpoint/{key}", float(value), step=epoch)

    return str(ckpt_dir)


def _write_checkpoint_metadata(
    ckpt_dir: Path,
    checkpoint_path: Path,
    checkpoint_meta: CheckpointMeta,
    *,
    epoch: int,
    state: dict[str, Any],
    metrics: dict[str, float],
) -> None:
    payload: dict[str, Any] = {
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
    if checkpoint_meta.config_version is not None:
        payload["config_version"] = checkpoint_meta.config_version
    if checkpoint_meta.dataset_version is not None:
        payload["dataset_version"] = checkpoint_meta.dataset_version

    with contextlib.suppress(Exception):  # pragma: no cover
        (ckpt_dir / "metadata.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )


def run_unified_training(
    cfg: UnifiedTrainingConfig,
    callbacks: Iterable[TrainingCallback] | None = None,
    ndjson_log_path: str | None = None,
) -> dict[str, Any]:
    """Execute training under unified orchestrator."""
    start = time.time()
    if cfg.seed is not None:
        _seed_all(cfg.seed, deterministic=bool(cfg.deterministic))
    rng_state = RNGState()
    output_root = Path(cfg.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    mlflow_active = bool(cfg.mlflow_enable and init_mlflow_safe())

    backend_name = _auto_backend(cfg)
    strategy = strategies.resolve_strategy(backend_name)

    # State object passed to callbacks (extendable)
    state: dict[str, Any] = {
        "backend_name": backend_name,
        "global_step": 0,
        "resume_from": cfg.resume_from,
        "mlflow_active": mlflow_active,
        "output_dir": str(output_root),
    }
    state["distributed"] = distributed_context()
    if cfg.dataset_version is not None:
        state["dataset_version"] = cfg.dataset_version
    if cfg.auto_capture_env:
        env_dir = output_root / "environment"
        try:
            capture_environment(env_dir)
            state["environment_snapshot"] = str(env_dir)
        except Exception as exc:  # pragma: no cover - best effort capture
            state["environment_snapshot_error"] = repr(exc)
    if isinstance(cfg.continual, ContinualConfig):
        state["continual"] = asdict(cfg.continual)

    device_config: DeviceConfig | None = None
    strategy_name = None
    if isinstance(cfg.extra, Mapping):
        strategy_name = cfg.extra.get("device_strategy")
    try:
        if strategy_name:
            device_config = DeviceMapper.get_strategy(str(strategy_name))
        else:
            device_config = DeviceConfig.auto_detect()
        if device_config is not None and torch is not None:
            dtype_overrides = {
                "fp32": torch.float32,
                "fp16": torch.float16,
                "bf16": getattr(torch, "bfloat16", torch.float16),
            }
            if cfg.dtype in dtype_overrides:
                desired_dtype = dtype_overrides[cfg.dtype]
                device_config = DeviceConfig(
                    device=device_config.device,
                    dtype=desired_dtype,
                    mixed_precision=device_config.mixed_precision and cfg.dtype != "fp32",
                )
    except Exception as exc:  # pragma: no cover - defensive fallback
        state["device_detect_error"] = repr(exc)
    else:
        if device_config is not None:
            state["device"] = device_config.device
            state["dtype_effective"] = str(device_config.dtype)
            state["mixed_precision"] = bool(device_config.mixed_precision)

    if mlflow_active:
        log_params_safe(
            {
                "training.model": cfg.model_name,
                "training.epochs": cfg.epochs,
                "training.batch_size": cfg.batch_size,
                "training.grad_accum": cfg.grad_accum,
                "training.backend": backend_name,
            }
        )

    # Pre-resume load if requested
    if cfg.resume_from:
        try:
            loaded_state, _ = load_checkpoint(cfg.resume_from, restore_rng=True)
            payload_keys = sorted(loaded_state.keys()) if isinstance(loaded_state, dict) else []
            state.update({"resume_loaded": True, "resume_payload_keys": payload_keys})
        except (IOError, OSError) as exc:  # pragma: no cover
            state.update({"resume_error": repr(exc)})
        else:
            rng_candidate = RNGState.path_for_checkpoint(Path(cfg.resume_from))
            if rng_candidate.exists():
                try:
                    loaded_rng = RNGState.load_from_file(rng_candidate)
                    loaded_rng.restore()
                    state["rng_resumed_from"] = str(rng_candidate)
                except (IOError, OSError) as exc:  # pragma: no cover - defensive
                    state["rng_resume_error"] = repr(exc)

    class _StateRelay:
        __slots__ = ("_callback", "_shared_state")

        def __init__(self, callback: TrainingCallback, shared_state: dict[str, Any]) -> None:
            self._callback = callback
            self._shared_state = shared_state

        def __getattr__(self, name: str) -> Any:  # pragma: no cover - passthrough
            return getattr(self._callback, name)

        def _merge_state(self, payload: Any) -> None:
            if isinstance(payload, dict):
                self._shared_state.update(payload)

        def on_train_start(self, state: dict[str, Any]) -> None:
            del state
            method = getattr(self._callback, "on_train_start", None)
            if callable(method):
                method(self._shared_state)

        def on_epoch_start(self, epoch: int, state: dict[str, Any]) -> None:
            self._merge_state(state)
            method = getattr(self._callback, "on_epoch_start", None)
            if callable(method):
                method(epoch, self._shared_state)

        def on_epoch_end(self, epoch: int, metrics: dict[str, Any], state: dict[str, Any]) -> Any:
            self._merge_state(state)
            method = getattr(self._callback, "on_epoch_end", None)
            if callable(method):
                return method(epoch, metrics, self._shared_state)
            return None

        def on_step(
            self, batch_index: int, global_step: int, loss: float, state: dict[str, Any]
        ) -> Any:
            self._merge_state(state)
            method = getattr(self._callback, "on_step", None)
            if callable(method):
                return method(batch_index, global_step, loss, self._shared_state)
            return None

        def on_checkpoint(
            self, epoch: int, path: str, metrics: dict[str, Any], state: dict[str, Any]
        ) -> Any:
            self._merge_state(state)
            method = getattr(self._callback, "on_checkpoint", None)
            if callable(method):
                return method(epoch, path, metrics, self._shared_state)
            return None

        def on_train_end(self, state: dict[str, Any]) -> None:
            del state
            method = getattr(self._callback, "on_train_end", None)
            if callable(method):
                method(self._shared_state)

    cbs = list(callbacks) if callbacks else []
    callbacks_module = None
    if cfg.enable_eval_callback or cfg.enable_logging_callback:
        callbacks_spec = importlib.util.find_spec("codex_ml.callbacks.base")
        if callbacks_spec is not None:
            callbacks_module = importlib.import_module("codex_ml.callbacks.base")
    if cfg.enable_eval_callback and callbacks_module is not None:
        evaluation_cls = getattr(callbacks_module, "EvaluationCallback", None)
        if evaluation_cls is not None and not any(isinstance(cb, evaluation_cls) for cb in cbs):
            cbs.append(evaluation_cls(None))
    if cfg.enable_logging_callback and callbacks_module is not None:
        logging_cls = getattr(callbacks_module, "LoggingCallback", None)
        if logging_cls is not None and not any(isinstance(cb, logging_cls) for cb in cbs):
            cbs.append(logging_cls())
    if ndjson_log_path:
        from codex_ml.callbacks.ndjson_logger import NDJSONLogger

        cbs.append(NDJSONLogger(ndjson_log_path))

    wrapped_callbacks = [_StateRelay(cb, state) for cb in cbs]
    for cb in wrapped_callbacks:
        with contextlib.suppress(Exception):
            cb.on_train_start(state)

    # Wrap strategy run
    result: TrainingResult = strategy.run(cfg, wrapped_callbacks, resume_from=cfg.resume_from)

    for cb in wrapped_callbacks:
        with contextlib.suppress(Exception):
            cb.on_train_end(state)

    # Emit final synthetic checkpoint (epoch = cfg.epochs)
    final_status = 1.0 if result.status == "ok" else 0.0
    with contextlib.suppress(Exception):
        ckpt_path = _emit_checkpoint_epoch(
            cfg,
            cfg.epochs,
            state,
            {"final_status": final_status},
            rng_state=rng_state,
        )
        state["final_checkpoint_dir"] = ckpt_path
        log_metric_safe("training/final_status", final_status, step=result.final_epoch)
        for cb in wrapped_callbacks:
            with contextlib.suppress(Exception):
                cb.on_checkpoint(cfg.epochs, ckpt_path, {"final_status": final_status}, state)

    return {
        "status": result.status,
        "backend": result.backend,
        "final_epoch": result.final_epoch,
        "output_dir": result.output_dir,
        "elapsed_s": round(time.time() - start, 4),
        "resume_from": cfg.resume_from,
        "mlflow_active": mlflow_active,
        "config_version": cfg.config_version,
        "dataset_version": cfg.dataset_version,
    }


def _emit_legacy_warning(entrypoint: str, redirect: str) -> None:
    warnings.warn(
        (
            f"codex_ml.training.unified_training.{entrypoint} is deprecated and will be "
            f"removed in a future release; use {redirect} instead."
        ),
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
    "ContinualConfig",
    "ContinualPhase",
    "UnifiedTrainingConfig",
    "distributed_context",
    "functional_training",
    "resolve_strategy",  # re-exported for monkeypatching
    "run_unified_training",
    "train_loop",
]

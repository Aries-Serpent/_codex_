"""Utilities for optional MLflow integration.

This module provides a small, backward-compatible helper surface for starting
MLflow runs and logging parameters, metrics and artifacts. All MLflow usage is
optional and guarded by the provided `MlflowConfig` or per-call flags.

Design goals / behavior:
- Safe lazy import of `mlflow` so module import never fails when MLflow is
  absent.
- `start_run` returns a context manager:
    - If MLflow is disabled via config, yields None (no-op).
    - If MLflow is enabled but the package cannot be imported, raises RuntimeError.
    - Otherwise returns the `mlflow.start_run()` context manager.
- `log_*` helpers are no-ops when MLflow is not available unless explicitly
  enabled=True was requested (in which case we raise to surface the missing dependency).
- Comprehensive error handling: IO and MLflow failures are wrapped in
  RuntimeError with context.
- Backwards compatibility: accepts experiment name strings in `start_run`
  like older call sites; preserves previous function names and semantics.
"""

from __future__ import annotations

import contextlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ContextManager, Dict, Iterable, Mapping, Optional, Union

# Lazy import variables
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False

# Attempt a top-level lazy import (non-fatal)
try:  # pragma: no cover - optional dependency
    import mlflow as _m  # type: ignore
    _mlf = _m
    _HAS_MLFLOW = True
except Exception:
    _mlf = None
    _HAS_MLFLOW = False


@dataclass
class MlflowConfig:
    """Configuration for MLflow usage.

    Fields
    - enable: whether to enable MLflow operations (default False)
    - tracking_uri: location for MLflow tracking store (defaults to "./mlruns")
    - experiment: experiment name to use for runs
    - run_tags: optional run tags mapping forwarded to mlflow.start_run
    - enable_system_metrics: optionally set environment flag for MLflow system metrics
    """
    enable: bool = False
    tracking_uri: Optional[str] = "./mlruns"
    experiment: Optional[str] = None
    run_tags: Optional[Dict[str, str]] = None
    enable_system_metrics: Optional[bool] = None


__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
    "_ensure_mlflow_available",
]


def _ensure_mlflow_available() -> None:
    """Ensure mlflow is importable at call time.

    Tries a runtime import if the top-level import failed. Raises a
    RuntimeError if mlflow is requested but cannot be imported.
    """
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW and _mlf is not None:
        return
    try:
        import importlib
        _m = importlib.import_module("mlflow")  # type: ignore
        _mlf = _m
        _HAS_MLFLOW = True
    except Exception as exc:
        _mlf = None
        _HAS_MLFLOW = False
        raise RuntimeError("MLflow requested but not installed or importable") from exc


def _coerce_config(
    cfg_or_experiment: Union[MlflowConfig, str, None],
    *,
    tracking_uri: Optional[str] = None,
    experiment: Optional[str] = None,
    run_tags: Optional[Dict[str, str]] = None,
    enable_system_metrics: Optional[bool] = None,
) -> MlflowConfig:
    """Normalize inputs into an MlflowConfig.

    Accepts:
    - MlflowConfig: returned with overrides applied
    - str: treated as experiment name and enables MLflow (backwards compat)
    - None: returns a default MlflowConfig()
    """
    if isinstance(cfg_or_experiment, MlflowConfig):
        cfg = MlflowConfig(
            enable=cfg_or_experiment.enable,
            tracking_uri=cfg_or_experiment.tracking_uri,
            experiment=cfg_or_experiment.experiment,
            run_tags=cfg_or_experiment.run_tags.copy() if cfg_or_experiment.run_tags else None,
            enable_system_metrics=cfg_or_experiment.enable_system_metrics,
        )
    elif isinstance(cfg_or_experiment, str):
        cfg = MlflowConfig(enable=True, tracking_uri=tracking_uri or "./mlruns", experiment=cfg_or_experiment)
    else:
        cfg = MlflowConfig(enable=False, tracking_uri=tracking_uri or "./mlruns", experiment=experiment)

    # Apply explicit overrides if provided
    if tracking_uri is not None:
        cfg.tracking_uri = tracking_uri
    if experiment is not None:
        cfg.experiment = experiment
    if run_tags is not None:
        cfg.run_tags = run_tags
    if enable_system_metrics is not None:
        cfg.enable_system_metrics = enable_system_metrics

    return cfg


def start_run(
    cfg_or_experiment: Union[MlflowConfig, str, None] = None,
    *,
    tracking_uri: Optional[str] = None,
    experiment: Optional[str] = None,
    run_tags: Optional[Dict[str, str]] = None,
    enable_system_metrics: Optional[bool] = None,
) -> ContextManager[Any]:
    """Start (or no-op) an MLflow run as a context manager.

    Usage:
      - start_run(MlflowConfig(...))
      - start_run("experiment-name", tracking_uri="./mlruns")
      - start_run() -> no-op context (disabled)

    Behavior:
    - If MLflow is disabled via config, returns a context manager yielding None.
    - If MLflow is enabled but mlflow package is not importable, raises RuntimeError.
    - Otherwise configures tracking URI, experiment and returns mlflow.start_run().
    """
    cfg = _coerce_config(
        cfg_or_experiment,
        tracking_uri=tracking_uri,
        experiment=experiment,
        run_tags=run_tags,
        enable_system_metrics=enable_system_metrics,
    )

    if not cfg.enable:
        # No-op context manager; yields None (indicates mlflow not active).
        return contextlib.nullcontext(None)

    # Ensure mlflow is available - raises if not importable
    _ensure_mlflow_available()

    # Set system metrics env var only if explicitly provided
    if cfg.enable_system_metrics is not None:
        os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS", "1" if cfg.enable_system_metrics else "0")

    try:
        # Configure tracking URI and experiment if provided
        if cfg.tracking_uri:
            _mlf.set_tracking_uri(cfg.tracking_uri)  # type: ignore[attr-defined]
        if cfg.experiment:
            _mlf.set_experiment(cfg.experiment)  # type: ignore[attr-defined]

        # Start the run with optional tags. mlflow.start_run returns a context manager.
        return _mlf.start_run(tags=cfg.run_tags or {})  # type: ignore[return-value]
    except Exception as exc:
        raise RuntimeError("Failed to initialize MLflow run") from exc


def _mlflow_noop_or_raise(enabled: Optional[bool]) -> Optional[Any]:
    """Internal helper to check mlflow availability based on enabled flag.

    Returns:
    - None if operation should be a no-op (mlflow not present and not explicitly enabled)
    - raises RuntimeError if enabled=True but mlflow missing
    - returns _mlf module if available
    """
    if enabled is False:
        return None
    if _HAS_MLFLOW and _mlf is not None:
        return _mlf
    if enabled is True:
        # Caller explicitly asked for MLflow but it's missing -> surface error
        _ensure_mlflow_available()  # will raise if unavailable
        return _mlf
    # enabled is None: permissive - no-op when mlflow isn't present
    if not _HAS_MLFLOW or _mlf is None:
        return None
    return _mlf


def log_params(d: Mapping[str, Any], *, enabled: Optional[bool] = None) -> None:
    """Log a mapping of parameters to MLflow if enabled.

    If enabled is True and MLflow is not available, a RuntimeError is raised.
    If enabled is None and MLflow is not installed, this becomes a no-op.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None:
        return
    try:
        ml.log_params(dict(d))  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError("Failed to log parameters to MLflow") from exc


def log_metrics(d: Mapping[str, float], *, step: Optional[int] = None, enabled: Optional[bool] = None) -> None:
    """Log metrics mapping to MLflow if enabled.

    `step` may be provided to associate a step index with the metrics.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None:
        return
    try:
        if step is None:
            ml.log_metrics(dict(d))  # type: ignore[arg-type]
        else:
            ml.log_metrics(dict(d), step=step)  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError("Failed to log metrics to MLflow") from exc


def log_artifacts(path: Union[str, Path, Iterable[Union[str, Path]]], *, enabled: Optional[bool] = None) -> None:
    """Log a file, directory, or iterable of paths as MLflow artifacts if enabled.

    - If a single path to a directory is provided, mlflow.log_artifacts is used.
    - If a single path to a file is provided, mlflow.log_artifact is used.
    - If an iterable is provided, each element is logged appropriately.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None:
        return

    def _log_single(p: Union[str, Path]) -> None:
        p = Path(p)
        try:
            if p.is_dir():
                # log_artifacts expects a directory path
                ml.log_artifacts(str(p))  # type: ignore[arg-type]
            else:
                ml.log_artifact(str(p))  # type: ignore[arg-type]
        except Exception as exc:
            raise RuntimeError(f"Failed to log artifact {p}") from exc

    # Accept both single path or iterable
    if isinstance(path, (str, Path)):
        _log_single(path)
        return

    for p in path:
        _log_single(p)


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path, *, enabled: Optional[bool] = None) -> Path:
    """Write seeds.json under out_dir and optionally log it to MLflow.

    Returns the path to the written seeds.json. Raises RuntimeError on IO failure.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    try:
        path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write seeds snapshot to {path}") from exc

    # Log the written file as an artifact when requested.
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(run_dir: Path, summary: Dict[str, Any], seeds: Mapping[str, Any], *, enabled: Optional[bool] = None) -> None:
    """Ensure a local run directory has summary.json and seeds.json written.

    Also writes seeds via seed_snapshot (which will log the seeds.json when
    `enabled` is True at that call site).
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    try:
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write summary to {summary_path}") from exc

    # Write seeds (may log to MLflow depending on `enabled`)
    seed_snapshot(seeds, run_dir, enabled=enabled)

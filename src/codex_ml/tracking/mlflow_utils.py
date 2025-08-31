# -*- coding: utf-8 -*-
"""Utilities for optional MLflow integration.

This module provides a small, backward-compatible helper surface for starting
MLflow runs and logging parameters, metrics and artifacts. All MLflow usage is
optional and guarded by the provided `MlflowConfig` or per-call flags.
"""
from __future__ import annotations

import contextlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ContextManager, Dict, Mapping, Optional, Union

# Lazy import of mlflow
try:  # pragma: no cover - runtime import behavior is environment-dependent
    import mlflow as _mlf  # type: ignore
    _HAS_MLFLOW = True
except Exception:  # pragma: no cover
    _HAS_MLFLOW = False
    _mlf = None  # type: ignore

__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
]


@dataclass
class MlflowConfig:
    """Configuration for MLflow usage.

    enable: whether to enable MLflow operations
    tracking_uri: location for MLflow tracking store (defaults to ./mlruns)
    experiment: experiment name to use for runs
    """
    enable: bool = False
    tracking_uri: str = "./mlruns"
    experiment: str = "codex-experiments"


def _ensure_mlflow_available() -> None:
    """Ensure mlflow is importable at call time.

    Attempts a runtime import if the top-level import failed. Raises a
    RuntimeError if mlflow is requested but cannot be imported.
    """
    global _mlf, _HAS_MLFLOW
    if _HAS_MLFLOW and _mlf is not None:
        return
    try:
        import mlflow as _m  # type: ignore
        _mlf = _m
        _HAS_MLFLOW = True
    except Exception as exc:
        _HAS_MLFLOW = False
        _mlf = None  # type: ignore
        raise RuntimeError("MLflow requested but not installed or importable") from exc


def start_run(
    cfg_or_experiment: Union[MlflowConfig, str],
    tracking_uri: Optional[str] = None,
) -> ContextManager[Any]:
    """Start (or no-op) an MLflow run as a context manager.

    Accepts either:
    - an MlflowConfig instance, or
    - an experiment name (str) for backward compatibility.

    Behavior:
    - If MLflow is disabled via config, returns a context manager yielding False.
    - If MLflow is enabled but mlflow package is not importable, raises RuntimeError.
    - Otherwise, sets the tracking URI and experiment and returns mlflow.start_run().

    Examples:
        cfg = MlflowConfig(enable=True, tracking_uri="./mlruns", experiment="exp")
        with start_run(cfg) as run: ...
        with start_run("exp-name", tracking_uri="./mlruns") as run: ...
    """
    # Normalize to MlflowConfig
    if isinstance(cfg_or_experiment, MlflowConfig):
        cfg = cfg_or_experiment
        # If an explicit tracking_uri argument was passed, allow it to override the config.
        if tracking_uri is not None:
            cfg = MlflowConfig(enable=cfg.enable, tracking_uri=tracking_uri, experiment=cfg.experiment)
    else:
        # treat string as experiment name for backward compatibility
        cfg = MlflowConfig(
            enable=True,
            tracking_uri=tracking_uri or MlflowConfig().tracking_uri,
            experiment=cfg_or_experiment,
        )

    if not cfg.enable:
        # No-op context manager; yields False to indicate mlflow not active.
        return contextlib.nullcontext(False)

    # Ensure mlflow is importable and available
    _ensure_mlflow_available()

    # Configure MLflow environment and start the run
    os.environ.setdefault("MLFLOW_ENABLE_SYSTEM_METRICS", "false")
    try:
        _mlf.set_tracking_uri(cfg.tracking_uri)  # type: ignore[attr-defined]
        _mlf.set_experiment(cfg.experiment)  # type: ignore[attr-defined]
        return _mlf.start_run()  # type: ignore[return-value]
    except Exception as exc:
        raise RuntimeError("Failed to initialize MLflow run") from exc


def log_params(d: Mapping[str, Any], *, enabled: bool = False) -> None:
    """Log a mapping of parameters to MLflow if enabled.

    If enabled is True and MLflow is not available, a RuntimeError is raised.
    """
    if not enabled:
        return
    if not _HAS_MLFLOW or _mlf is None:
        raise RuntimeError("MLflow requested but not installed")
    try:
        _mlf.log_params(dict(d))  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError("Failed to log parameters to MLflow") from exc


def log_metrics(d: Mapping[str, float], step: Optional[int] = None, *, enabled: bool = False) -> None:
    """Log metrics mapping to MLflow if enabled.

    `step` may be provided to associate a step index with the metrics.
    """
    if not enabled:
        return
    if not _HAS_MLFLOW or _mlf is None:
        raise RuntimeError("MLflow requested but not installed")
    try:
        # mlflow.log_metrics accepts a dict and optional step keyword
        if step is None:
            _mlf.log_metrics(dict(d))  # type: ignore[arg-type]
        else:
            _mlf.log_metrics(dict(d), step=step)  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError("Failed to log metrics to MLflow") from exc


def log_artifacts(path: str | Path, *, enabled: bool = False) -> None:
    """Log a file or directory as MLflow artifacts if enabled.

    `path` can be a Path or string; it's converted to str for MLflow.
    """
    if not enabled:
        return
    if not _HAS_MLFLOW or _mlf is None:
        raise RuntimeError("MLflow requested but not installed")
    try:
        _mlf.log_artifacts(str(path))  # type: ignore[arg-type]
    except Exception as exc:
        raise RuntimeError(f"Failed to log artifacts from {path!s} to MLflow") from exc


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = False) -> Path:
    """Write seeds.json under out_dir and optionally log it to MLflow.

    Returns the path to the written seeds.json.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    try:
        path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write seeds snapshot to {path}") from exc

    # Log the written file as an artifact when requested
    try:
        log_artifacts(path, enabled=enabled)
    except RuntimeError:
        # Do not mask the file write error. Propagate MLflow logging error separately.
        raise
    return path


def ensure_local_artifacts(run_dir: Path, summary: Dict[str, Any], seeds: Dict[str, Any]) -> None:
    """Ensure a local run directory has summary.json and seeds.json written.

    Also writes seeds via seed_snapshot (which will log the seeds.json when
    `enabled` is used at that call site).
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    try:
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to write summary to {summary_path}") from exc

    # Write seeds (no MLflow logging by default here).
    seed_snapshot(seeds, run_dir)

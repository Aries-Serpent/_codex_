"""Minimal, user-friendly helpers for optional MLflow integration.

The functions exposed here intentionally mirror the small public surface that
historically lived under :mod:`codex_ml.tracking`. They allow lightweight
scripts to opt into MLflow without pulling the heavier runtime into memory
until the very first tracking call is executed.

Key behaviours for callers:

* Importing the module never raises when MLflow is missing; runtime helpers
  only error when the caller explicitly requests MLflow interaction.
* :func:`start_run` provides a context manager that either yields ``None`` for
  no-op tracking, or the real ``mlflow.start_run`` context when the package is
  available.
* ``log_*`` helpers accept a rich mapping surface but degrade gracefully when
  MLflow is not enabled, so notebooks can share code paths across environments.
"""

from __future__ import annotations

import contextlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ContextManager, Dict, Iterable, Mapping, Optional, Union

from codex_ml.tracking import mlflow_guard

# Lazy import variables
# Lazy import variables
_mlf = None  # Actual mlflow module if import succeeds
_HAS_MLFLOW = False
# Historical constant retained for compatibility with downstream tooling/tests
MLFLOW_DEFAULT_URI = "file:./artifacts/mlruns"


# Prefer a project-local artifacts directory by default to avoid polluting
# the repository root when running audits offline. Can be overridden via
# CODEX_MLFLOW_URI.
def _default_tracking_uri() -> str:
    env_codex = os.getenv("CODEX_MLFLOW_URI")
    env_mlflow = os.getenv("MLFLOW_TRACKING_URI")
    if env_codex:
        return env_codex
    if env_mlflow:
        return env_mlflow
    return mlflow_guard.bootstrap_offline_tracking()


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
    - tracking_uri: location for MLflow tracking store (defaults to env CODEX_MLFLOW_URI or "file:mlruns")
    - experiment: experiment name to use for runs
    - run_tags: optional run tags mapping forwarded to mlflow.start_run
    - enable_system_metrics: optionally set environment flag for MLflow system metrics
    """

    enable: bool = False
    tracking_uri: Optional[str] = None
    experiment: Optional[str] = None
    run_tags: Optional[Dict[str, str]] = None
    enable_system_metrics: Optional[bool] = None

    def __post_init__(self) -> None:
        if not self.tracking_uri:
            self.tracking_uri = _default_tracking_uri()


__all__ = [
    "MlflowConfig",
    "start_run",
    "log_params",
    "log_metrics",
    "log_artifacts",
    "seed_snapshot",
    "ensure_local_artifacts",
    "_ensure_mlflow_available",
    "bootstrap_offline_tracking",
    "MLFLOW_DEFAULT_URI",
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


def bootstrap_offline_tracking(force: bool = False, requested_uri: str | None = None) -> str:
    """Ensure MLflow uses the local file-backed store by default."""

    return mlflow_guard.bootstrap_offline_tracking(force=force, requested_uri=requested_uri)


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
        cfg = MlflowConfig(
            enable=True,
            tracking_uri=tracking_uri or _default_tracking_uri(),
            experiment=cfg_or_experiment,
        )
    else:
        cfg = MlflowConfig(
            enable=False,
            tracking_uri=tracking_uri or _default_tracking_uri(),
            experiment=experiment,
        )

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
      - start_run("experiment-name", tracking_uri="file:mlruns")
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
        os.environ.setdefault(
            "MLFLOW_ENABLE_SYSTEM_METRICS", "1" if cfg.enable_system_metrics else "0"
        )

    try:
        # Configure tracking URI and experiment if provided
        target_uri = mlflow_guard.bootstrap_offline_tracking(requested_uri=cfg.tracking_uri)
        if target_uri:
            _mlf.set_tracking_uri(target_uri)  # type: ignore[attr-defined]
        if cfg.experiment:
            _mlf.set_experiment(cfg.experiment)  # type: ignore[attr-defined]

        # Start the run with optional tags. mlflow.start_run returns a context manager.
        return _mlf.start_run(tags=cfg.run_tags or {})  # type: ignore[return-value]
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Failed to initialize MLflow run") from exc


def _mlflow_noop_or_raise(enabled: Optional[bool]) -> Optional[Any]:
    """Internal helper to check mlflow availability based on enabled flag.

    Returns:
    - ``None`` when logging is disabled or not explicitly requested
    - raises ``RuntimeError`` if ``enabled=True`` but mlflow is missing
    - returns the ``mlflow`` module when available and explicitly enabled
    """
    # Treat ``enabled=None`` as disabled for backward-compatible opt-in behavior.
    if enabled is not True:
        return None

    # ``enabled`` is True: ensure mlflow is importable and return the module.
    if not _HAS_MLFLOW or _mlf is None:
        _ensure_mlflow_available()  # will raise if unavailable
    return _mlf


def log_params(d: Mapping[str, Any], *, enabled: Optional[bool] = None) -> None:
    """Send configuration parameters to MLflow when tracking is enabled.

    Parameters
    ----------
    d:
        Mapping of parameter names to serialisable values. The mapping is
        eagerly copied so callers can pass generators or other transient
        structures.
    enabled:
        Explicit opt-in to MLflow logging. When ``None`` (the default) or
        ``False`` the helper is a silent no-op. When ``True`` the function
        raises :class:`RuntimeError` if MLflow cannot be imported.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None:
        return
    try:
        ml.log_params(dict(d))  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Failed to log parameters to MLflow") from exc


def log_metrics(
    metrics: Mapping[str, float], *, step: Optional[int] = None, enabled: Optional[bool] = None
) -> None:
    """Record scalar metrics against an explicit training step.

    Parameters
    ----------
    metrics:
        Mapping of metric names to numeric values. A ``_step`` entry is treated
        as a default ``step`` when none is provided, mirroring legacy behaviour.
    step:
        Optional step override. Providing a value ensures MLflow renders
        time-series charts correctly.
    enabled:
        Explicit opt-in to MLflow logging. When ``None`` or ``False`` the call
        is a no-op; when ``True`` MLflow must be importable.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None or not metrics:
        return
    if step is None:
        step = int(metrics.get("_step", 0))
    metrics = {k: v for k, v in metrics.items() if k != "_step"}
    for k, v in metrics.items():
        try:
            ml.log_metric(k, float(v), step=step)  # type: ignore[arg-type]
        except Exception:
            # be robust; drop bad values quietly
            pass


def log_artifacts(
    path: Union[str, Path, Iterable[Union[str, Path]]], *, enabled: Optional[bool] = None
) -> None:
    """Persist files or directories to MLflow artifact storage.

    Parameters
    ----------
    path:
        Single filesystem location or an iterable of paths to push to MLflow.
        Directories are forwarded to ``mlflow.log_artifacts`` while individual
        files use ``mlflow.log_artifact``.
    enabled:
        Explicit opt-in flag. When ``None`` or ``False`` nothing happens; when
        ``True`` MLflow must be importable otherwise a :class:`RuntimeError` is
        raised.
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
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to log artifact {p}") from exc

    # Accept both single path or iterable
    if isinstance(path, (str, Path)):
        _log_single(path)
        return

    for p in path:
        _log_single(p)


def seed_snapshot(seeds: Mapping[str, Any], out_dir: Path, *, enabled: bool = False) -> Path:
    """Write a reproducibility snapshot of random seeds.

    The resulting ``seeds.json`` is always emitted locally so offline audits can
    inspect the randomness state. When ``enabled`` is ``True`` the file is also
    uploaded to MLflow. Any I/O failure surfaces as :class:`RuntimeError` with
    contextual information.

    Returns
    -------
    pathlib.Path
        Location of the written ``seeds.json`` file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "seeds.json"
    try:
        path.write_text(json.dumps(dict(seeds), indent=2), encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to write seeds snapshot to {path}") from exc

    # Log the written file as an artifact when requested.
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(
    run_dir: Path,
    summary: Dict[str, Any],
    seeds: Mapping[str, Any],
    *,
    enabled: bool = False,
) -> None:
    """Write ``summary.json`` and ``seeds.json`` to ``run_dir`` for inspection.

    Parameters
    ----------
    run_dir:
        Destination directory that will receive both files.
    summary:
        Mapping of summary keys to values which will be pretty-printed to
        ``summary.json``.
    seeds:
        Mapping of random seeds forwarded to :func:`seed_snapshot`.
    enabled:
        When ``True`` the seeds snapshot is also uploaded as an MLflow artifact
        to keep remote tracking stores in sync with the local files. The default
        ``False`` mode keeps the helper side-effect free for offline runs.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    try:
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to write summary to {summary_path}") from exc

    # Write seeds (optionally log to MLflow)
    seed_snapshot(seeds, run_dir, enabled=enabled)

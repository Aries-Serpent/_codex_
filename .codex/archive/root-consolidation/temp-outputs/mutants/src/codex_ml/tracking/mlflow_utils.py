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

import logging

logger = logging.getLogger(__name__)

import contextlib  # noqa: E402
import hashlib  # noqa: E402
import importlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, ContextManager, Optional  # noqa: E402

from codex_ml.tracking import mlflow_guard  # noqa: E402
from codex_ml.utils.optional_dependencies import (  # noqa: E402
    build_optional_dependency_error,
)

# Attempt to import mlflow at module level for backward-compat aliases.
# codex_ml.monitoring.mlflow_utils accesses _mlf to expose the module
# without requiring mlflow to be installed.
try:
    import mlflow as _mlf  # noqa: E402
except ImportError as exc:
    logger.debug("Failed to import mlflow at module load: %s", exc)
    _mlf = None
except AttributeError:
    logger.warning("Unexpected failure importing mlflow at module load", exc_info=True)
    _mlf = None

# Prefer a project-local artifacts directory by default to avoid polluting
# the repository root when running audits offline. Can be overridden via
# CODEX_MLFLOW_URI.
_CODEX_URI = os.getenv("CODEX_MLFLOW_URI")
_DEFAULT_LITERAL_URI = "file:./artifacts/mlruns"
# Bootstrap the guard to ensure directories exist and env vars are normalised,
# but keep the historical literal default for compatibility checks.
_ = mlflow_guard.bootstrap_offline_tracking(requested_uri=_CODEX_URI or _DEFAULT_LITERAL_URI)
MLFLOW_DEFAULT_URI = _DEFAULT_LITERAL_URI


def _resolve_tracking_uri_default() -> Optional[str]:
    codex_env = os.getenv("CODEX_MLFLOW_URI")
    if codex_env:
        return codex_env
    tracking_env = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_env:
        return tracking_env
    return MLFLOW_DEFAULT_URI


@dataclass
class MlflowConfig:
    """Configuration for MLflow usage.

    Fields
    - enable: whether to enable MLflow operations (default False)
    - tracking_uri: location for MLflow tracking store (defaults to env CODEX_MLFLOW_URI or "file:mlruns")
    - experiment: experiment name to use for runs
    - run_tags: optional run tags mapping forwarded to mlflow.start_run
    - enable_system_metrics: optionally set environment flag for MLflow system metrics
    """  # noqa: E501

    enable: bool = False
    tracking_uri: Optional[str] = field(default_factory=_resolve_tracking_uri_default)
    experiment: Optional[str] = None
    run_tags: Optional[dict[str, str]] = None
    enable_system_metrics: Optional[bool] = None


__all__ = [
    "MlflowConfig",
    "_ensure_mlflow_available",
    "_mlf",
    "bootstrap_offline_tracking",
    "current_commit_hash",
    "ensure_local_artifacts",
    "init_run",
    "log_artifacts",
    "log_metrics",
    "log_params",
    "seed_snapshot",
    "start_run",
]


def _ensure_mlflow_available() -> Any:
    """Ensure mlflow is importable at call time.

    Tries a runtime import if the top-level import failed. Raises a
    RuntimeError with installation guidance when MLflow is unavailable.
    """
    try:
        return importlib.import_module("mlflow")
    except (IOError, OSError) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        err = build_optional_dependency_error("mlflow", "experiment tracking")
        raise RuntimeError(err.args[0]) from exc


def bootstrap_offline_tracking(force: bool = False, requested_uri: str | None = None) -> str:
    """Ensure MLflow uses the local file-backed store by default."""

    return mlflow_guard.bootstrap_offline_tracking(force=force, requested_uri=requested_uri)


def _coerce_config(
    cfg_or_experiment: MlflowConfig | str | None,
    *,
    tracking_uri: Optional[str] = None,
    experiment: Optional[str] = None,
    run_tags: Optional[dict[str, str]] = None,
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
            tracking_uri=tracking_uri or MLFLOW_DEFAULT_URI,
            experiment=cfg_or_experiment,
        )
    else:
        cfg = MlflowConfig(
            enable=False,
            tracking_uri=tracking_uri or MLFLOW_DEFAULT_URI,
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
    cfg_or_experiment: MlflowConfig | str | None = None,
    *,
    tracking_uri: Optional[str] = None,
    experiment: Optional[str] = None,
    run_tags: Optional[dict[str, str]] = None,
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
        ml = _ensure_mlflow_available()
        if target_uri:
            ml.set_tracking_uri(target_uri)
        if cfg.experiment:
            ml.set_experiment(cfg.experiment)

        # Start the run with optional tags. mlflow.start_run returns a context manager.
        return ml.start_run(tags=cfg.run_tags or {})
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
    return _ensure_mlflow_available()


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
        ml.log_params(dict(d))
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Failed to log parameters to MLflow") from exc


def log_metrics(
    metrics: Mapping[str, float],
    *,
    step: Optional[int] = None,
    enabled: Optional[bool] = None,
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
            ml.log_metric(k, float(v), step=step)
        except (IOError, OSError):
            logger.debug("log_metric failed for key %s; skipping", k, exc_info=True)
            # be robust; drop bad values quietly


def log_artifacts(
    path: str | Path | Iterable[str | Path],
    *,
    enabled: Optional[bool] = None,
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
        ``True`` MLflow must be importable otherwise a :class:`ImportError` is
        raised.
    """
    ml = _mlflow_noop_or_raise(enabled)
    if ml is None:
        return

    def _log_single(p: str | Path) -> None:
        p = Path(p)
        try:
            if p.is_dir():
                # log_artifacts expects a directory path
                ml.log_artifacts(str(p))
            else:
                ml.log_artifact(str(p))
        except (IOError, OSError) as exc:  # pragma: no cover
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
    except (IOError, OSError) as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to write seeds snapshot to {path}") from exc

    # Log the written file as an artifact when requested.
    log_artifacts(path, enabled=enabled)
    return path


def ensure_local_artifacts(
    run_dir: Path,
    summary: dict[str, Any],
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
    except (IOError, OSError) as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to write summary to {summary_path}") from exc

    # Write seeds (optionally log to MLflow)
    seed_snapshot(seeds, run_dir, enabled=enabled)


def current_commit_hash() -> str:
    """Return the active git commit hash, or an empty string when unavailable."""

    try:
        import git

        repo = git.Repo(search_parent_directories=True)
        return repo.head.commit.hexsha
    except (ImportError, AttributeError):
        logger.debug("git commit hash unavailable", exc_info=True)
        return ""


def init_run(
    run_name: Optional[str] = None,
    config: Optional[Any] = None,
    **kwargs: Any,
) -> None:
    """Start an MLflow run and attach git/config provenance tags."""

    ml = _ensure_mlflow_available()
    run = ml.start_run(run_name=run_name, **kwargs)

    try:
        commit = current_commit_hash()
        if commit:
            ml.set_tag("git_commit", commit[:7])
    except (ValueError, TypeError) as e:
        logger.debug("git_commit tag unavailable: %s", e)

    if config is not None:
        try:
            try:
                payload = json.dumps(config, sort_keys=True, default=str)
            except TypeError as e:
                logger.debug("config serialization failed: %s; falling back to str()", e)
                payload = str(config)
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
            ml.set_tag("config_hash", digest)
        except (ValueError, TypeError) as e:
            logger.debug("config_hash tag unavailable: %s", e)

    return run

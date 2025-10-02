"""Offline-safe MLflow adapter utilities."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from importlib import util
from typing import Any, Iterator, Mapping

from codex_ml.tracking.mlflow_guard import bootstrap_offline_tracking, last_decision

if util.find_spec("mlflow") is not None:  # pragma: no branch - deterministic import path
    import mlflow  # type: ignore[import-not-found]
else:  # pragma: no cover - exercised when MLflow is absent
    mlflow = None  # type: ignore[assignment]


LOG = logging.getLogger(__name__)

# Default to a local, file-backed store under the repo's artifacts/ path.
# Safe for offline runs and avoids accidental remote logging.
DEFAULT_LOCAL_URI = "file:./artifacts/mlruns"

# Opt-in escape hatch for developers who *intentionally* want remote tracking.
# ``CODEX_MLFLOW_ALLOW_REMOTE`` is retained for backward compatibility; the
# guard also recognises ``MLFLOW_ALLOW_REMOTE``.
ALLOW_REMOTE_ENV = "CODEX_MLFLOW_ALLOW_REMOTE"


def ensure_local_tracking(default_uri: str = DEFAULT_LOCAL_URI) -> str:
    """Guard MLflow to use a local file-backed tracking URI by default.

    Behavior:
        * When ``MLFLOW_TRACKING_URI`` is unset, force ``default_uri``.
        * Remote URIs are rejected unless ``MLFLOW_ALLOW_REMOTE`` or the legacy
          ``CODEX_MLFLOW_ALLOW_REMOTE`` opt-in is provided.
        * Returns the effective URI recorded by
          :func:`codex_ml.tracking.mlflow_guard.bootstrap_offline_tracking`.

    Returns the effective MLflow tracking URI.
    """

    env_uri = os.environ.get("MLFLOW_TRACKING_URI", "").strip()
    candidate = env_uri or default_uri
    effective = bootstrap_offline_tracking(requested_uri=candidate, force=not bool(env_uri))
    guard_decision = last_decision()
    if guard_decision is not None:
        if guard_decision.fallback_reason:
            LOG.warning(
                "Blocking remote MLflow tracking URI '%s'; using %s",
                guard_decision.requested_uri,
                guard_decision.effective_uri,
            )
        elif guard_decision.allow_remote and guard_decision.requested_uri:
            LOG.info(
                "Allowing remote MLflow tracking URI via %s=%s: %s",
                guard_decision.allow_remote_env,
                guard_decision.allow_remote_flag or "<empty>",
                guard_decision.requested_uri,
            )
    if effective.startswith("file:"):
        os.environ["CODEX_MLFLOW_LOCAL_DIR"] = effective[len("file:") :]

    if mlflow is not None:
        mlflow.set_tracking_uri(effective)
        LOG.info("Using MLflow tracking URI: %s", effective)
    else:
        LOG.warning("MLflow not installed; tracking URI set to %s", effective)
    return effective


def _as_flat_params(data: Mapping[str, Any], prefix: str = "") -> dict[str, str]:
    """Flatten a nested mapping and coerce values to strings."""

    flattened: dict[str, str] = {}
    for key, value in data.items():
        composed = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(_as_flat_params(value, composed))
        else:
            flattened[composed] = str(value)
    return flattened


@contextmanager
def maybe_mlflow(
    *, enable: bool, run_name: str | None = None, tracking_uri: str | None = None
) -> Iterator[object]:
    """Yield an MLflow-like logger when the optional dependency is available.

    The returned object exposes ``log_params``, ``log_metrics`` and ``log_artifact``
    methods.  When MLflow is unavailable or ``enable`` is ``False`` the methods are
    best-effort no-ops, ensuring callers can integrate logging without mandatory
    dependencies.
    """

    class _NoOpLogger:
        def log_params(self, params: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
            return None

        def log_metrics(
            self, metrics: Mapping[str, float], step: int | None = None
        ) -> None:  # pragma: no cover - trivial
            return None

        def log_artifact(self, path: str) -> None:  # pragma: no cover - trivial
            return None

        def __enter__(self) -> "_NoOpLogger":  # pragma: no cover - trivial
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
            return False

        def get_tracking_uri(self) -> str:  # pragma: no cover - trivial
            return os.environ.get("MLFLOW_TRACKING_URI", bootstrap_offline_tracking())

    if not enable or mlflow is None:
        yield _NoOpLogger()
        return

    try:  # pragma: no cover - optional dependency path
        # Always route through the guard, even when an explicit URI is provided.
        # If `tracking_uri` is remote and no explicit opt-in is set, the guard
        # will override to a local file-backed URI and log a warning.
        if tracking_uri:
            os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
        ensure_local_tracking()
        with mlflow.start_run(run_name=run_name) as _run:  # noqa: F841 - ensure context
            yield mlflow
    except Exception:
        # Degrade gracefully to a no-op logger when MLflow is unavailable.
        yield _NoOpLogger()


__all__ = ["ensure_local_tracking", "maybe_mlflow", "_as_flat_params"]

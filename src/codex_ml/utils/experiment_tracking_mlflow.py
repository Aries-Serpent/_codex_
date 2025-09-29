"""Offline-safe MLflow adapter utilities."""

from __future__ import annotations

import logging
import os
import urllib.parse
from contextlib import contextmanager
from importlib import util
from typing import Any, Iterator, Mapping

if util.find_spec("mlflow") is not None:  # pragma: no branch - deterministic import path
    import mlflow  # type: ignore[import-not-found]
else:  # pragma: no cover - exercised when MLflow is absent
    mlflow = None  # type: ignore[assignment]


LOG = logging.getLogger(__name__)

# Default to a local, file-backed store under the repo's artifacts/ path.
# Safe for offline runs and avoids accidental remote logging.
DEFAULT_LOCAL_URI = "file:./artifacts/mlruns"

# Opt-in escape hatch for developers who *intentionally* want remote tracking.
# Example: export CODEX_MLFLOW_ALLOW_REMOTE=1
ALLOW_REMOTE_ENV = "CODEX_MLFLOW_ALLOW_REMOTE"


def _is_remote_uri(uri: str) -> bool:
    """Return ``True`` if the URI uses an HTTP(S) scheme."""

    try:
        scheme = urllib.parse.urlparse(uri).scheme.lower()
    except Exception:  # pragma: no cover - defensive, shouldn't occur in practice
        return False
    return scheme in {"http", "https"}


def ensure_local_tracking(default_uri: str = DEFAULT_LOCAL_URI) -> str:
    """Guard MLflow to use a local file-backed tracking URI by default.

    Behavior:
        * When ``MLFLOW_TRACKING_URI`` is unset, force ``default_uri``.
        * When ``MLFLOW_TRACKING_URI`` points at HTTP(S) and
          ``CODEX_MLFLOW_ALLOW_REMOTE`` is **not** present, fall back to
          ``default_uri``.
        * Otherwise respect the configured URI.

    Returns the effective MLflow tracking URI.
    """

    env_uri = os.environ.get("MLFLOW_TRACKING_URI")

    if mlflow is None:
        if not env_uri or (_is_remote_uri(env_uri) and not os.environ.get(ALLOW_REMOTE_ENV)):
            os.environ["MLFLOW_TRACKING_URI"] = default_uri
            effective = default_uri
        else:
            effective = env_uri
        LOG.warning(
            "MLflow not installed; tracking URI set to %s", effective,
        )
        return effective

    if not env_uri:
        os.environ["MLFLOW_TRACKING_URI"] = default_uri
        mlflow.set_tracking_uri(default_uri)
        LOG.info(
            "MLflow tracking URI not set; using local store: %s",
            default_uri,
        )
        return mlflow.get_tracking_uri()

    if _is_remote_uri(env_uri) and not os.environ.get(ALLOW_REMOTE_ENV):
        mlflow.set_tracking_uri(default_uri)
        os.environ["MLFLOW_TRACKING_URI"] = default_uri
        LOG.warning(
            "Blocking remote MLFLOW_TRACKING_URI=%s (missing %s). Using local: %s",
            env_uri,
            ALLOW_REMOTE_ENV,
            default_uri,
        )
        return mlflow.get_tracking_uri()

    mlflow.set_tracking_uri(env_uri)
    LOG.info("Using configured MLflow tracking URI: %s", env_uri)
    return mlflow.get_tracking_uri()


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

    if not enable or mlflow is None:
        yield _NoOpLogger()
        return

    try:  # pragma: no cover - optional dependency path
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        else:
            ensure_local_tracking()
        with mlflow.start_run(run_name=run_name) as _run:  # noqa: F841 - ensure context
            yield mlflow
    except Exception:
        # Degrade gracefully to a no-op logger when MLflow is unavailable.
        yield _NoOpLogger()


__all__ = ["ensure_local_tracking", "maybe_mlflow", "_as_flat_params"]

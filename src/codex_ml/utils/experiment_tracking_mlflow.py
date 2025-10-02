"""Offline-safe MLflow adapter utilities."""

from __future__ import annotations

import logging
import os
import urllib.parse
from contextlib import contextmanager
from importlib import util
from typing import Any, Iterator, Mapping

from codex_ml.tracking.mlflow_guard import ensure_file_backend

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
    allow_remote = os.environ.get(ALLOW_REMOTE_ENV)

    if env_uri and _is_remote_uri(env_uri):
        if allow_remote:
            if mlflow is not None:
                mlflow.set_tracking_uri(env_uri)
                LOG.info(
                    "Allowing remote MLflow tracking URI via %s: %s",
                    ALLOW_REMOTE_ENV,
                    env_uri,
                )
            else:
                LOG.warning(
                    "MLflow not installed; requested remote URI %s ignored (stays unset)",
                    env_uri,
                )
            return env_uri
        LOG.warning(
            "Blocking remote MLFLOW_TRACKING_URI=%s (missing %s). Using local backend.",
            env_uri,
            ALLOW_REMOTE_ENV,
        )
        env_uri = None

    if default_uri.startswith("file:") and env_uri is None:
        os.environ["CODEX_MLFLOW_LOCAL_DIR"] = default_uri[len("file:") :]

    uri = ensure_file_backend(force=env_uri is None)
    effective = uri or env_uri or default_uri

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
            return os.environ.get("MLFLOW_TRACKING_URI", ensure_file_backend())

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

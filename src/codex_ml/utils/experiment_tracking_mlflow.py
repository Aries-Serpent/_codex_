"""Offline-safe MLflow adapter utilities."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping


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

    if not enable:
        yield _NoOpLogger()
        return

    try:  # pragma: no cover - optional dependency path
        import mlflow

        uri = tracking_uri or os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            base = Path(".codex/mlruns").resolve()
            base.mkdir(parents=True, exist_ok=True)
            uri = f"file://{base}"
        mlflow.set_tracking_uri(uri)
        with mlflow.start_run(run_name=run_name) as _run:  # noqa: F841 - ensure context
            yield mlflow
    except Exception:
        # Degrade gracefully to a no-op logger when MLflow is unavailable.
        yield _NoOpLogger()


__all__ = ["maybe_mlflow", "_as_flat_params"]

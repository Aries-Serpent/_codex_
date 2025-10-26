"""Best-effort mlflow integrations used by the training loop."""

from __future__ import annotations

import contextlib
from typing import Any, Dict, Iterable, Iterator, Mapping

__all__ = ["maybe_mlflow", "_as_flat_params"]


def _as_flat_params(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Flatten nested dictionaries using ``.`` separators."""

    flat: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, Mapping):
            for sub_key, sub_value in _as_flat_params(value).items():
                flat[f"{key}.{sub_key}"] = sub_value
        else:
            flat[key] = value
    return flat


class _NullMlflow:
    def log_params(self, params: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
        pass

    def log_metrics(self, metrics: Mapping[str, Any], step: int | None = None) -> None:  # pragma: no cover
        pass

    def log_artifact(self, path: str) -> None:  # pragma: no cover - trivial
        pass


@contextlib.contextmanager
def maybe_mlflow(*, enable: bool, run_name: str | None = None, tracking_uri: str | None = None) -> Iterator[_NullMlflow]:
    """Return a context manager that yields a real mlflow run when possible."""

    if not enable:
        yield _NullMlflow()
        return
    try:  # pragma: no cover - mlflow optional dependency
        import mlflow
    except Exception:
        yield _NullMlflow()
        return
    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        run = mlflow.start_run(run_name=run_name)
        yield mlflow
    finally:
        try:
            mlflow.end_run()
        except Exception:  # pragma: no cover - defensive
            pass

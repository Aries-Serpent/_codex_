"""Optional MLflow logging helpers."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from typing import Any, Iterator, Mapping, Optional


@contextmanager
def mlflow_run(
    enabled: bool,
    *,
    params: Optional[Mapping[str, Any]] = None,
) -> Iterator[None]:
    """Start an MLflow run when the dependency is installed and enabled."""

    if not enabled:
        yield
        return

    try:  # pragma: no cover - optional dependency
        import importlib

        module = importlib.import_module("mlflow")
        if module is None:
            raise ImportError("mlflow import returned None")
    except Exception:  # pragma: no cover - dependency missing
        yield
        return

    run = module.start_run  # type: ignore[attr-defined]
    log_param = getattr(module, "log_param", None)

    try:  # pragma: no cover - runtime failures fall back to no-op
        run_context = run()
    except Exception:
        yield
        return

    with ExitStack() as stack:
        try:  # pragma: no cover - runtime failures fall back to no-op
            stack.enter_context(run_context)
        except Exception:
            yield
            return

        if params and callable(log_param):
            for key, value in params.items():
                try:
                    log_param(key, value)
                except Exception:  # pragma: no cover - logging best effort
                    continue

        yield


__all__ = ["mlflow_run"]

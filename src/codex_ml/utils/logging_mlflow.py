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

    run = getattr(module, "start_run", None)
    if not callable(run):  # pragma: no cover - defensive
        yield
        return
    log_param = getattr(module, "log_param", None)

    stack: Optional[ExitStack] = ExitStack()
    try:
        stack.enter_context(run())
    except Exception:  # pragma: no cover - runtime failures fall back to no-op
        if stack is not None:
            try:
                stack.close()
            except Exception:  # pragma: no cover - suppress close errors
                pass
        stack = None
        yield
        return

    try:
        if params and callable(log_param):
            for key, value in params.items():
                try:
                    log_param(key, value)
                except Exception:  # pragma: no cover - logging best effort
                    continue
        yield
    finally:
        if stack is not None:
            try:
                stack.close()
            except Exception:  # pragma: no cover - suppress close errors
                pass


__all__ = ["mlflow_run"]

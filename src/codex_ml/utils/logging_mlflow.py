"""Optional MLflow logging helpers."""

from __future__ import annotations

import logging
from contextlib import ExitStack, contextmanager
from typing import Any, Iterator, Mapping, Optional

LOGGER = logging.getLogger(__name__)


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
    except Exception as exc:  # pragma: no cover - runtime failures fall back to no-op
        LOGGER.warning("MLflow run initialization failed; continuing without tracking: %s", exc)
        if stack is not None:
            try:
                stack.close()
            except Exception as close_exc:  # pragma: no cover - suppress close errors
                LOGGER.debug("Failed to close MLflow context after init failure: %s", close_exc)
        stack = None
        yield
        return

    try:
        if params and callable(log_param):
            for key, value in params.items():
                try:
                    log_param(key, value)
                except Exception as exc:  # pragma: no cover - logging best effort
                    LOGGER.debug("Failed to log MLflow param %s=%s: %s", key, value, exc)

        yield
    finally:
        if stack is not None:
            try:
                stack.close()
            except Exception as exc:  # pragma: no cover - suppress close errors
                LOGGER.debug("MLflow run cleanup raised but was suppressed: %s", exc)


__all__ = ["mlflow_run"]

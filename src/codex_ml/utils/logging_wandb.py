"""
Logging Wandb Module

This module provides functionality for logging wandb.

Usage:
    from utils.logging_wandb import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from codex_ml.utils.optional import optional_dependency_error
from codex_ml.utils.optional_dependencies import build_optional_dependency_error

LOGGER = logging.getLogger(__name__)


class _DummyRun:
    """Fallback logger when Weights & Biases is unavailable."""

    def log(self, data: Mapping[str, float], step: int | None = None) -> None:
        return None


@contextmanager
def maybe_wandb(run_name: str | None = None, enable: bool = False) -> Iterator[Any]:
    """Yield a W&B handle (or dummy) that is safe when the dependency is missing."""

    if not enable:
        yield _DummyRun()
        return

    run = None
    try:  # pragma: no cover - optional dependency
        import wandb

        os.environ.setdefault("WANDB_MODE", "offline")
        project = os.environ.get("WANDB_PROJECT", "codex-offline")
        init_kwargs = {
            "project": project,
            "name": run_name,
            "mode": os.environ.get("WANDB_MODE", "offline"),
        }
        wandb_dir = os.environ.get("WANDB_DIR")
        if wandb_dir:
            init_kwargs["dir"] = wandb_dir
        run = wandb.init(**init_kwargs)
        yield wandb
    except ImportError as exc:  # pragma: no cover - missing optional dependency
        raise build_optional_dependency_error("wandb", "Weights & Biases logging") from exc
    except AttributeError:  # pragma: no cover - wandb init/import issues
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "wandb",
                purpose="Weights & Biases logging",
            ),
        )
        yield _DummyRun()
    finally:
        if run is not None:
            try:  # pragma: no cover - defensive cleanup
                run.finish()
            except (ValueError, TypeError, RuntimeError) as exc:
                LOGGER.debug(f"Exception: {exc}")
                LOGGER.debug("W&B run cleanup raised but was suppressed: %s", exc)


__all__ = ["maybe_wandb"]

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator, Mapping


class _DummyRun:
    """Fallback logger when Weights & Biases is unavailable."""

    def log(self, data: Mapping[str, float], step: int | None = None) -> None:  # noqa: D401 - mimic wandb
        return None


@contextmanager
def maybe_wandb(run_name: str | None = None, enable: bool = False) -> Iterator[Any]:
    """Yield a W&B handle (or dummy) that is safe when the dependency is missing."""

    if not enable:
        yield _DummyRun()
        return

    try:  # pragma: no cover - optional dependency
        import wandb  # type: ignore

        mode = os.environ.get("WANDB_MODE", "offline")
        project = os.environ.get("WANDB_PROJECT", "codex")
        wandb.init(project=project, name=run_name, mode=mode)
        yield wandb
    except Exception:  # pragma: no cover - wandb init/import issues
        yield _DummyRun()


__all__ = ["maybe_wandb"]

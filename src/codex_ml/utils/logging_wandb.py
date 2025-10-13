from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any


class _DummyRun:
    """Fallback logger when Weights & Biases is unavailable."""

    def log(
        self, data: Mapping[str, float], step: int | None = None
    ) -> None:
        return None


@contextmanager
def maybe_wandb(run_name: str | None = None, enable: bool = False) -> Iterator[Any]:
    """Yield a W&B handle (or dummy) that is safe when the dependency is missing."""

    if not enable:
        yield _DummyRun()
        return

    run = None
    try:  # pragma: no cover - optional dependency
        import wandb  # type: ignore

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
    except Exception:  # pragma: no cover - wandb init/import issues
        yield _DummyRun()
    finally:
        if run is not None:
            try:  # pragma: no cover - defensive cleanup
                run.finish()
            except Exception:
                pass


__all__ = ["maybe_wandb"]

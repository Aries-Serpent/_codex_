"""Lightweight checkpoint save/load helpers with pruning support."""

from __future__ import annotations

import logging
import os
import pickle
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional torch dependency
    import torch
except (IOError, OSError):  # pragma: no cover - torch missing
    torch = None  # type: ignore[assignment]

__all__ = ["load_checkpoint", "save_checkpoint"]


def save_checkpoint(
    state: dict[str, Any], path: str | os.PathLike[str], *, keep_last_k: int = 3
) -> Path:
    """Persist ``state`` to ``path`` and prune older checkpoints."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if torch is not None and hasattr(torch, "save"):
        torch.save(state, target)
    else:  # pragma: no cover - exercised when torch is unavailable
        from codex_ml.utils.safe_pickle import safe_pickle_dump

        safe_pickle_dump(state, str(target))

    if keep_last_k <= 0:
        return target

    checkpoints = sorted(
        target.parent.glob("*.pt"),
        key=lambda candidate: (os.path.getmtime(candidate), candidate.name),
    )
    while len(checkpoints) > keep_last_k:
        oldest = checkpoints.pop(0)
        try:
            oldest.unlink()
        except FileNotFoundError:  # pragma: no cover - race condition guard
            continue
    return target


def load_checkpoint(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a checkpoint previously written by :func:`save_checkpoint`."""

    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(path)
    if torch is not None and hasattr(torch, "load"):
        try:
            # Security: Use weights_only=True to prevent arbitrary code execution (CVE-2024-XXXXX)
            load_kwargs = {"map_location": "cpu"}
            # Check if torch.load supports weights_only parameter (PyTorch >= 2.0)
            import inspect

            if "weights_only" in inspect.signature(torch.load).parameters:
                load_kwargs["weights_only"] = True  # type: ignore[assignment]
            data = torch.load(
                target, **load_kwargs
            )  # nosec B614 - weights_only=True set above when available
        except (
            RuntimeError,
            pickle.UnpicklingError,
            EOFError,
            AttributeError,
        ) as torch_error:
            logger.debug(f"Exception: {torch_error}")
            # Use safe pickle loading as fallback
            from codex_ml.utils.safe_pickle import safe_pickle_load

            try:
                data = safe_pickle_load(str(target), use_restricted_unpickler=True)
            except (ImportError, AttributeError) as err:
                logger.warning("Exception occurred", exc_info=True)
                raise torch_error from err
    else:  # pragma: no cover - exercised when torch is unavailable
        # Use safe pickle loading to prevent code execution vulnerabilities
        from codex_ml.utils.safe_pickle import safe_pickle_load

        data = safe_pickle_load(str(target), use_restricted_unpickler=True)
    if not isinstance(data, dict):
        raise TypeError("checkpoint payload must be a mapping")
    return data

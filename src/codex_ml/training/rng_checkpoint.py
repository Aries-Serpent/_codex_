"""Capture and restore RNG state for deterministic resume support."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import numpy as np
except (IOError, OSError):  # pragma: no cover
    np = None

try:  # pragma: no cover - optional dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover
    torch = None  # type: ignore[assignment]

from codex_ml.utils.checkpoint_core import capture_rng_state as _capture_core
from codex_ml.utils.checkpoint_core import restore_rng_state as _restore_core


@dataclass
class RNGState:
    """Container for RNG state across Python, NumPy and Torch backends."""

    state: dict[str, Any] = field(default_factory=dict)

    def capture(self) -> None:
        self.state = _capture_core()

    def restore(self) -> None:
        if self.state:
            _restore_core(self.state)

    def save_to_file(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2, sort_keys=True)
        return path

    @classmethod
    def load_from_file(cls, path: Path) -> RNGState:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("RNG state file must contain a JSON object")
        return cls(state=data)

    @staticmethod
    def path_for_checkpoint(checkpoint_path: Path) -> Path:
        return checkpoint_path.with_suffix(checkpoint_path.suffix + ".rng.json")


def set_seed(seed: int) -> None:
    """set the RNG seed for Python, NumPy and Torch (if available)."""

    random.seed(seed)
    if np is not None:
        try:
            np.random.seed(seed)
        except (IOError, OSError):  # pragma: no cover
            logger.debug("Suppressed exception in handler", exc_info=True)
    if torch is not None:
        try:
            torch.manual_seed(seed)
            if hasattr(torch.cuda, "manual_seed_all"):
                torch.cuda.manual_seed_all(seed)  # pragma: no cover - GPU path
        except (IOError, OSError):  # pragma: no cover
            logger.debug("Suppressed exception in handler", exc_info=True)


__all__ = ["RNGState", "set_seed"]

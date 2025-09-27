"""Reproducible DataLoader helpers."""

from __future__ import annotations

import random
from typing import Optional

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover - numpy may be absent
    np = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch may be absent
    torch = None  # type: ignore[assignment]

__all__ = ["seed_worker", "make_generator"]


def seed_worker(worker_id: int) -> None:  # pragma: no cover - thin wrapper
    """Seed DataLoader workers for deterministic behaviour."""

    base_seed = random.getrandbits(32)
    random.seed(base_seed)
    if np is not None:
        np.random.seed(base_seed)
    if torch is not None and hasattr(torch, "manual_seed"):
        torch.manual_seed(base_seed)


def make_generator(seed: int) -> Optional["torch.Generator"]:
    """Create a PyTorch ``Generator`` seeded with ``seed`` when available."""

    if torch is None or not hasattr(torch, "Generator"):
        return None
    generator = torch.Generator()
    generator.manual_seed(int(seed))
    return generator

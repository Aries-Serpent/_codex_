"""
Dataloader Utils Module

This module provides functionality for dataloader utils.

Usage:
    from training.dataloader_utils import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import random
from typing import Optional

try:  # pragma: no cover - optional dependency
    import numpy as np
except (ImportError, AttributeError):  # pragma: no cover - numpy may be absent
    np = None

try:  # pragma: no cover - optional dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover - torch may be absent
    torch = None  # type: ignore[assignment]

__all__ = ["make_generator", "seed_worker"]


def seed_worker(worker_id: int) -> None:  # pragma: no cover - thin wrapper
    """Seed DataLoader workers for deterministic behaviour."""

    base_seed = random.getrandbits(32)  # nosec B311 — non-cryptographic ML sampling/shuffling
    random.seed(base_seed)
    if np is not None:
        np.random.seed(base_seed)
    if torch is not None and hasattr(torch, "manual_seed"):
        torch.manual_seed(base_seed)


def make_generator(seed: int) -> Optional[torch.Generator]:
    """Create a PyTorch ``Generator`` seeded with ``seed`` when available."""

    if torch is None or not hasattr(torch, "Generator"):
        return None
    generator = torch.Generator()
    generator.manual_seed(int(seed))
    return generator

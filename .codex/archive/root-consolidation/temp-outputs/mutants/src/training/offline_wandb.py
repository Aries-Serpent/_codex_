"""Utilities to ensure WandB stays offline in audit environments."""

from __future__ import annotations

import os


def force_offline() -> None:
    """Default WandB to offline mode without clobbering existing settings."""

    os.environ.setdefault("WANDB_MODE", "offline")


__all__ = ["force_offline"]

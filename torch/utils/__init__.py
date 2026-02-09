"""Minimal torch.utils shim for test environments."""

from __future__ import annotations

__all__ = ["data"]

# Import data submodule for torch.utils.data access
from torch.utils import data  # noqa: E402, F401

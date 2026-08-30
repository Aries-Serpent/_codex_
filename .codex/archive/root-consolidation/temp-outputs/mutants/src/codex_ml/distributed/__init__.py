"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from distributed.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from .minimal import (
    barrier,
    cleanup,
    get_rank,
    get_world_size,
    init_distributed_if_needed,
    is_distributed_available,
)

__all__ = [
    "barrier",
    "cleanup",
    "get_rank",
    "get_world_size",
    "init_distributed_if_needed",
    "is_distributed_available",
]

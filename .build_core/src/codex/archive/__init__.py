"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from archive.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from .api import restore, store
from .service import ArchiveService

__all__ = ["ArchiveService", "restore", "store"]

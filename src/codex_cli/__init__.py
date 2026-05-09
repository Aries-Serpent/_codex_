"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from codex_cli.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

__all__ = ["__version__", "app"]
__version__ = "0.0.0"


def __getattr__(name: str):
    if name == "app":
        from . import app as app_module

        globals()["app"] = app_module
        return app_module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

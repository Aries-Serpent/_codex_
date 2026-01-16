"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from codex_dummy_plugin.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

class DummyModel:
    """Minimal object to prove entry-point discovery works."""

    def __init__(self) -> None:
        self.name = "dummy"

    def predict(self, x):
        return x

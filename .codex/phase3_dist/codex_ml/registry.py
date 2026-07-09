"""
Registry Module

This module provides functionality for registry.

Usage:
    from codex_ml.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from collections.abc import Callable

_REG: dict[str, Callable] = {}


def register(name: str):
    def deco(fn: Callable):
        _REG[name] = fn
        return fn

    return deco


def get(name: str) -> Callable:
    return _REG[name]

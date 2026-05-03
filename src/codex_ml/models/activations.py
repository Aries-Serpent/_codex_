"""
Activations Module

This module provides functionality for activations.

Usage:
    from models.activations import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# BEGIN: CODEX_ACTIVATIONS
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from collections.abc import Callable  # noqa: E402

try:
    import torch
    import torch.nn as nn
except Exception:
    logger.warning("Exception occurred", exc_info=True)
    torch, nn = None, None  # type: ignore
_REGISTRY: dict[str, Callable] = {}


def _register(name: str):
    def deco(fn):
        _REGISTRY[name.lower()] = fn
        return fn

    return deco


@_register("relu")
def relu():
    return nn.ReLU() if nn else (lambda x: x)


@_register("gelu")
def gelu():
    return nn.GELU() if nn else (lambda x: x)


@_register("silu")
def silu():
    return nn.SiLU() if nn else (lambda x: x)


@_register("swiglu")
def swiglu():
    return nn.SiLU() if nn else (lambda x: x)


def get_activation(name: str):
    key = (name or "gelu").lower()
    if key not in _REGISTRY:
        raise KeyError(f"unknown activation: {name}")
    return _REGISTRY[key]()


# END: CODEX_ACTIVATIONS

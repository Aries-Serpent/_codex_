"""
Registry Module

This module provides functionality for registry.

Usage:
    from connectors.registry import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from .base import Connector, LocalConnector
from .remote import RemoteConnector

__all__ = ["get_connector", "list_connectors", "register_connector"]

_REGISTRY: dict[str, type[Connector]] = {
    "local": LocalConnector,
    "remote": RemoteConnector,
}


def register_connector(name: str, cls: type[Connector]) -> None:
    _REGISTRY[name] = cls


def get_connector(name: str, **kwargs) -> Connector:
    if name not in _REGISTRY:
        raise KeyError(name)
    return _REGISTRY[name](**kwargs)


def list_connectors() -> dict[str, type[Connector]]:
    return dict(_REGISTRY)

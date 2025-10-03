from __future__ import annotations

from typing import Dict, Type

from .base import Connector, LocalConnector
from .remote import RemoteConnector

__all__ = ["register_connector", "get_connector", "list_connectors"]

_REGISTRY: Dict[str, Type[Connector]] = {
    "local": LocalConnector,
    "remote": RemoteConnector,
}


def register_connector(name: str, cls: Type[Connector]) -> None:
    _REGISTRY[name] = cls


def get_connector(name: str, **kwargs) -> Connector:
    if name not in _REGISTRY:
        raise KeyError(name)
    return _REGISTRY[name](**kwargs)  # type: ignore[call-arg]


def list_connectors() -> Dict[str, Type[Connector]]:
    return dict(_REGISTRY)

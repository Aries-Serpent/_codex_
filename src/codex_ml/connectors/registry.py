from __future__ import annotations

from typing import Dict, Type

from .base import Connector
from .local import LocalConnector

_REGISTRY: Dict[str, Type[Connector]] = {"local": LocalConnector}


def register_connector(name: str, cls: Type[Connector]) -> None:
    _REGISTRY[name] = cls


def get_connector(name: str, **kwargs) -> Connector:
    if name not in _REGISTRY:
        raise KeyError(name)
    return _REGISTRY[name](**kwargs)  # type: ignore[call-arg]

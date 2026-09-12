"""Structural plugin protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .events import EventEnvelope


@runtime_checkable
class CodexPlugin(Protocol):
    """Minimum protocol implemented by cross-package event plugins."""

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def handle(self, event: EventEnvelope) -> EventEnvelope | None: ...

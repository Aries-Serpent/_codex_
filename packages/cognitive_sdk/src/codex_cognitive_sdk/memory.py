"""Memory records, queries, and backend protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Protocol, Sequence, runtime_checkable

from ._frozen import freeze_mapping as _freeze_mapping


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """A backend-neutral memory value."""

    memory_id: str
    content: object
    created_at: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    """Portable criteria for retrieving memory records."""

    text: str | None = None
    limit: int = 10
    metadata: Mapping[str, object] = field(default_factory=dict)
    since: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@runtime_checkable
class MemoryProtocol(Protocol):
    """Structural boundary implemented by consumer-owned memory backends."""

    def store(self, record: MemoryRecord) -> None:
        """Persist one record."""

        ...

    def retrieve(self, query: MemoryQuery) -> Sequence[MemoryRecord]:
        """Return records matching the query."""

        ...

    def delete(self, memory_id: str) -> bool:
        """Delete a record and report whether it existed."""

        ...


__all__ = ["MemoryProtocol", "MemoryQuery", "MemoryRecord"]

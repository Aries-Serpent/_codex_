"""Versioned event-envelope contract."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from ._validation import JsonValue, freeze_json_mapping
from .errors import ContractValidationError

CURRENT_SCHEMA_VERSION = "1.0"
DEFAULT_MAX_BYTES = 65_536


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Portable control-plane event with bounded JSON serialization."""

    kind: str
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source_version: str = ""
    correlation_id: str | None = None
    schema_version: str = CURRENT_SCHEMA_VERSION
    event_id: str = field(default_factory=lambda: str(uuid4()))
    emitted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __post_init__(self) -> None:
        if not self.kind:
            raise ContractValidationError("kind must not be empty")
        if not self.source:
            raise ContractValidationError("source must not be empty")
        if self.schema_version != CURRENT_SCHEMA_VERSION:
            raise ContractValidationError(f"unsupported schema_version: {self.schema_version!r}")
        try:
            payload = freeze_json_mapping(self.payload, field_name="payload")
        except ValueError as exc:
            raise ContractValidationError(str(exc)) from exc
        object.__setattr__(self, "payload", payload)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "emitted_at": self.emitted_at,
            "kind": self.kind,
            "source": self.source,
            "source_version": self.source_version,
            "correlation_id": self.correlation_id,
            "payload": dict(self.payload),
        }

    def to_json(self, *, max_bytes: int = DEFAULT_MAX_BYTES) -> str:
        """Serialize deterministically and reject oversized envelopes."""

        if max_bytes < 1:
            raise ContractValidationError("max_bytes must be positive")
        encoded = json.dumps(
            self.to_dict(),
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(encoded.encode("utf-8")) > max_bytes:
            raise ContractValidationError(f"event exceeds {max_bytes} byte limit")
        return encoded

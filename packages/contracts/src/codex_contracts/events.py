"""Versioned event-envelope contract."""

from __future__ import annotations

import json
import re
from collections.abc import Collection
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from ._validation import FrozenJsonValue, JsonValue, freeze_json_mapping, thaw_json_mapping
from .errors import ContractValidationError

CURRENT_SCHEMA_VERSION = "1.0"
SUPPORTED_SCHEMA_VERSIONS = frozenset({CURRENT_SCHEMA_VERSION})
DEFAULT_MAX_BYTES = 65_536
_MAX_IDENTIFIER_LENGTH = 256
_RFC3339_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$")
_EVENT_FIELDS = {
    "schema_version",
    "event_id",
    "emitted_at",
    "kind",
    "source",
    "source_version",
    "correlation_id",
    "payload",
}


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Portable control-plane event with bounded JSON serialization."""

    kind: str
    source: str
    payload: Mapping[str, FrozenJsonValue] = field(default_factory=dict)
    source_version: str = ""
    correlation_id: str | None = None
    schema_version: str = CURRENT_SCHEMA_VERSION
    event_id: str = field(default_factory=lambda: str(uuid4()))
    emitted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __post_init__(self) -> None:
        self._validate_text("schema_version", self.schema_version, required=True)
        self._validate_text("kind", self.kind, required=True)
        self._validate_text("source", self.source, required=True)
        self._validate_text("source_version", self.source_version)
        self._validate_text("event_id", self.event_id, required=True)
        if self.correlation_id is not None:
            self._validate_text("correlation_id", self.correlation_id, required=True)
        self._validate_timestamp()
        if self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise ContractValidationError(f"unsupported schema_version: {self.schema_version!r}")
        try:
            payload = freeze_json_mapping(self.payload, field_name="payload")
        except ValueError as exc:
            raise ContractValidationError(str(exc)) from exc
        object.__setattr__(self, "payload", payload)

    @staticmethod
    def _validate_text(field_name: str, value: str, *, required: bool = False) -> None:
        if not isinstance(value, str):
            raise ContractValidationError(f"{field_name} must be a string")
        if required and not value:
            raise ContractValidationError(f"{field_name} must not be empty")
        if len(value) > _MAX_IDENTIFIER_LENGTH:
            raise ContractValidationError(
                f"{field_name} exceeds {_MAX_IDENTIFIER_LENGTH} characters"
            )
        if value and not _SAFE_IDENTIFIER.fullmatch(value):
            raise ContractValidationError(
                f"{field_name} must contain only safe identifier characters"
            )

    def _validate_timestamp(self) -> None:
        if (
            not isinstance(self.emitted_at, str)
            or len(self.emitted_at) > 64
            or not _RFC3339_TIMESTAMP.fullmatch(self.emitted_at)
        ):
            raise ContractValidationError("emitted_at must be a bounded RFC 3339 timestamp")
        try:
            parsed = datetime.fromisoformat(self.emitted_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContractValidationError("emitted_at must be an RFC 3339 timestamp") from exc
        if parsed.tzinfo is None:
            raise ContractValidationError("emitted_at must include a timezone")

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
            "payload": thaw_json_mapping(self.payload),
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

    @classmethod
    def from_json(
        cls,
        data: bytes | str,
        *,
        accepted_versions: Collection[str] = SUPPORTED_SCHEMA_VERSIONS,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> EventEnvelope:
        """Decode and validate a bounded event envelope."""

        if max_bytes < 1:
            raise ContractValidationError("max_bytes must be positive")
        if isinstance(data, str):
            encoded = data.encode("utf-8")
        elif isinstance(data, (bytes, bytearray, memoryview)):
            encoded = bytes(data)
        else:
            raise ContractValidationError("event data must be bytes or text")
        if len(encoded) > max_bytes:
            raise ContractValidationError(f"event exceeds {max_bytes} byte limit")
        if isinstance(accepted_versions, (str, bytes)) or not isinstance(
            accepted_versions, Collection
        ):
            raise ContractValidationError("accepted_versions must be a collection of strings")
        if not accepted_versions or any(
            not isinstance(version, str) for version in accepted_versions
        ):
            raise ContractValidationError("accepted_versions must contain strings")

        def reject_constant(value: str) -> None:
            raise ValueError(f"non-finite number: {value}")

        def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            decoded: dict[str, Any] = {}
            for key, value in pairs:
                if key in decoded:
                    raise ValueError(f"duplicate field: {key}")
                decoded[key] = value
            return decoded

        try:
            value = json.loads(
                encoded.decode("utf-8"),
                parse_constant=reject_constant,
                object_pairs_hook=reject_duplicates,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
            raise ContractValidationError("event must be valid JSON") from exc
        if not isinstance(value, dict):
            raise ContractValidationError("event must be a JSON object")
        unknown = set(value) - _EVENT_FIELDS
        if unknown:
            raise ContractValidationError(f"event contains unknown fields: {sorted(unknown)!r}")
        missing = _EVENT_FIELDS - set(value)
        if missing:
            raise ContractValidationError(f"event is missing required fields: {sorted(missing)!r}")
        schema_version = value.get("schema_version")
        if schema_version not in accepted_versions:
            raise ContractValidationError(f"unaccepted schema_version: {schema_version!r}")
        try:
            return cls(**value)
        except TypeError as exc:
            raise ContractValidationError("event fields are missing or invalid") from exc

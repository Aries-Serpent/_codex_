"""Structured cross-package errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ._validation import JsonValue, freeze_json_mapping


class ContractValidationError(ValueError):
    """Raised when a contract cannot be encoded safely."""


@dataclass(frozen=True, slots=True)
class ErrorEnvelope:
    """Stable error details without unrestricted exception serialization."""

    category: str
    message: str
    retryable: bool = False
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.category:
            raise ContractValidationError("category must not be empty")
        try:
            details = freeze_json_mapping(self.details, field_name="details")
        except ValueError as exc:
            raise ContractValidationError(str(exc)) from exc
        object.__setattr__(self, "details", details)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {
            "category": self.category,
            "message": self.message,
            "retryable": self.retryable,
            "details": dict(self.details),
        }

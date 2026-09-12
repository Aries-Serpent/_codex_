"""Framework-neutral health-report contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class HealthStatus(StrEnum):
    """Portable health states for telemetry producers."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True, slots=True)
class HealthReport:
    """Immutable health result suitable for process-boundary transport."""

    status: HealthStatus
    checks: Mapping[str, str] = field(default_factory=dict)
    message: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks", MappingProxyType(dict(self.checks)))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""

        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "checks": dict(self.checks),
            "message": self.message,
        }

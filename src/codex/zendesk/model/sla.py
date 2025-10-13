"""Models describing Zendesk SLA policies."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class SLAPolicy(_ZendeskBaseModel):
    """Zendesk SLA policy settings."""

    name: str
    description: str | None = None
    targets: dict[str, int] = Field(
        default_factory=dict,
        description="Target times (minutes) for SLA metrics",
    )

    def diff(self, other: SLAPolicy) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.targets != other.targets:
            patches.append(
                {
                    "op": "replace",
                    "path": "/targets",
                    "value": dict(self.targets),
                }
            )
        if self.description != other.description:
            patches.append(
                {
                    "op": "replace",
                    "path": "/description",
                    "value": self.description,
                }
            )
        return patches

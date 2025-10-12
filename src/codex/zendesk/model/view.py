"""
Pydantic models for Zendesk Views.

Views define how tickets are displayed to agents, including filters,
columns, and sort order.  For configuration-as-code purposes, we
represent only the admin-visible aspects.
"""

from typing import Any

from pydantic import BaseModel, Field


class View(BaseModel):
    """A Zendesk view with filters, columns, and sort settings."""

    name: str
    filters: dict[str, Any] = Field(
        default_factory=dict, description="Filter conditions"
    )
    columns: list[str] = Field(
        default_factory=list, description="Ticket fields shown in the view"
    )
    sort: dict[str, str] = Field(
        default_factory=dict, description="Primary sort field and order"
    )
    active: bool = True

    def diff(self, other: "View") -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.active != other.active:
            patches.append(
                {"op": "replace", "path": "/active", "value": self.active}
            )
        if self.filters != other.filters:
            patches.append(
                {"op": "replace", "path": "/filters", "value": self.filters}
            )
        if self.columns != other.columns:
            patches.append(
                {"op": "replace", "path": "/columns", "value": self.columns}
            )
        if self.sort != other.sort:
            patches.append(
                {"op": "replace", "path": "/sort", "value": self.sort}
            )
        return patches

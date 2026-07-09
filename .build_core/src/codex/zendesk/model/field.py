"""Zendesk ticket field and form models."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class TicketField(_ZendeskBaseModel):
    """Minimal representation of a Zendesk ticket field."""

    name: str = Field(..., description="Human readable name of the field")
    type: str = Field(..., description="Zendesk ticket field type")
    options: list[str] = Field(
        default_factory=list,
        description="Selectable options for dropdown-like fields",
    )
    active: bool = Field(True, description="Whether the field is active")
    description: str | None = Field(
        default=None,
        description="Optional field description",
    )

    def diff(self, other: TicketField) -> list[dict[str, Any]]:
        """Return JSON patch operations that turn ``other`` into ``self``."""

        patches: list[dict[str, Any]] = []
        if self.type != other.type:
            patches.append({"op": "replace", "path": "/type", "value": self.type})
        if self.options != other.options:
            patches.append({"op": "replace", "path": "/options", "value": list(self.options)})
        if self.active != other.active:
            patches.append({"op": "replace", "path": "/active", "value": self.active})
        if self.description != other.description:
            patches.append({"op": "replace", "path": "/description", "value": self.description})
        return patches


class TicketForm(_ZendeskBaseModel):
    """Minimal representation of a Zendesk ticket form."""

    name: str = Field(..., description="Human readable name of the form")
    fields: list[str] = Field(
        default_factory=list,
        description="Ordered list of ticket field IDs included in the form",
    )
    active: bool = Field(True, description="Whether the form is active")

    def diff(self, other: TicketForm) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.fields != other.fields:
            patches.append({"op": "replace", "path": "/fields", "value": list(self.fields)})
        if self.active != other.active:
            patches.append({"op": "replace", "path": "/active", "value": self.active})
        return patches

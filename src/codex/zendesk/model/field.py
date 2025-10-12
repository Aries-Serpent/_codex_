"""
Pydantic models for Zendesk Ticket Fields and Forms.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TicketField(BaseModel):
    name: str
    type: str
    options: list[str] = Field(default_factory=list)
    active: bool = True

    def diff(self, other: TicketField) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.type != other.type:
            patches.append({"op": "replace", "path": "/type", "value": self.type})
        if self.options != other.options:
            patches.append({"op": "replace", "path": "/options", "value": self.options})
        if self.active != other.active:
            patches.append({"op": "replace", "path": "/active", "value": self.active})
        return patches


class TicketForm(BaseModel):
    name: str
    fields: list[str]
    active: bool = True

    def diff(self, other: TicketForm) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.fields != other.fields:
            patches.append({"op": "replace", "path": "/fields", "value": self.fields})
        if self.active != other.active:
            patches.append({"op": "replace", "path": "/active", "value": self.active})
        return patches

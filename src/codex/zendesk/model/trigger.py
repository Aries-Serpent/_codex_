"""
Pydantic models for Zendesk Triggers, Automations, Macros, and Views.

These models define a minimal schema required for the diff engine to compare
desired and actual trigger configurations.  Only admin-facing fields are
included.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Condition(BaseModel):
    field: str
    operator: str
    value: Any


class Action(BaseModel):
    field: str
    value: Any


class Trigger(BaseModel):
    name: str
    category: str
    conditions: dict[str, list[Condition]] = Field(
        ..., description="Conditions grouped by any/all semantics"
    )
    actions: list[Action] = Field(..., description="Actions executed by the trigger")
    position: int = Field(..., description="Position/order of the trigger")

    def diff(self, other: Trigger) -> list[dict[str, Any]]:
        """Compute a diff between two trigger definitions.

        Returns a list of patch operations.
        """

        patches: list[dict[str, Any]] = []
        if self.position != other.position:
            patches.append({"op": "replace", "path": "/position", "value": self.position})
        if self.category != other.category:
            patches.append({"op": "replace", "path": "/category", "value": self.category})
        if self.conditions != other.conditions:
            patches.append({"op": "replace", "path": "/conditions", "value": self.conditions})
        if self.actions != other.actions:
            patches.append({"op": "replace", "path": "/actions", "value": self.actions})
        return patches

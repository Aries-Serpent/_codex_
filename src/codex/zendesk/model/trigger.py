"""Zendesk trigger models and diff helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _ZendeskBaseModel(BaseModel):
    """Base model that ignores unexpected fields from the Zendesk API."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Condition(_ZendeskBaseModel):
    """Condition that controls when a trigger fires."""

    field: str = Field(..., description="Zendesk condition field identifier")
    operator: str = Field(..., description="Zendesk comparison operator")
    value: Any = Field(..., description="Comparison value")


class Action(_ZendeskBaseModel):
    """Action that is executed when a trigger fires."""

    field: str = Field(..., description="Zendesk action field identifier")
    value: Any = Field(..., description="Action payload")


class Trigger(_ZendeskBaseModel):
    """Representation of a Zendesk trigger configuration."""

    name: str = Field(..., description="Display name of the trigger")
    category: str = Field(..., description="Trigger category such as notifications")
    conditions: dict[str, list[Condition]] = Field(
        default_factory=dict,
        description="Mapping of condition groups (all/any) to their entries",
    )
    actions: list[Action] = Field(
        default_factory=list,
        description="Actions executed when the trigger fires",
    )
    position: int = Field(
        0,
        ge=0,
        description="Trigger order relative to other triggers",
    )

    def diff(self, other: Trigger) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``."""

        patches: list[dict[str, Any]] = []
        if self.position != other.position:
            patches.append({
                "op": "replace",
                "path": "/position",
                "value": self.position,
            })
        if self.category != other.category:
            patches.append({
                "op": "replace",
                "path": "/category",
                "value": self.category,
            })
        if self.conditions != other.conditions:
            patches.append({
                "op": "replace",
                "path": "/conditions",
                "value": _dump_conditions(self.conditions),
            })
        if self.actions != other.actions:
            patches.append({
                "op": "replace",
                "path": "/actions",
                "value": [_dump_action(action) for action in self.actions],
            })
        return patches


def _dump_conditions(
    conditions: dict[str, Iterable[Condition]]
) -> dict[str, list[dict[str, Any]]]:
    """Serialize condition groups into JSON-compatible dictionaries."""

    return {
        group: [_dump_model(condition) for condition in entries]
        for group, entries in conditions.items()
    }


def _dump_action(action: Action) -> dict[str, Any]:
    return _dump_model(action)


def _dump_model(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)

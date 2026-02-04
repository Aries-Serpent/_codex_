"""Pydantic models for validating Zendesk plan payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class JsonPatchOperation(BaseModel):
    """Single JSON Patch operation applied to an existing resource."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    op: str
    path: str | None = None
    value: Any | None = None
    from_: str | None = Field(default=None, alias="from")


class Operation(BaseModel):
    """Supported plan operations produced by diff/plan workflows."""

    model_config = ConfigDict(extra="allow")

    op: Literal["add", "patch", "remove"] | None = None
    action: Literal["create", "update", "delete"] | None = None
    path: str | None = None
    name: str | None = None
    resource: str | None = None
    value: Any | None = None
    data: Any | None = None
    patches: Sequence[JsonPatchOperation] | None = None
    changes: Sequence[Mapping[str, Any]] | None = None
    id: Any | None = None

    @model_validator(mode="after")
    def _normalize(self) -> Operation:
        """Harmonize historical plan formats into the canonical schema."""

        action_map: dict[str, Literal["add", "patch", "remove"]] = {
            "create": "add",
            "update": "patch",
            "delete": "remove",
        }

        if self.action is not None:
            expected = action_map[self.action]
            if self.op is not None and self.op != expected:
                raise ValueError("Operation uses conflicting 'op' and 'action' values.")
            object.__setattr__(self, "op", expected)

        if self.op is None:
            raise ValueError("Operation must define either 'op' or 'action'.")

        if self.op == "add" and self.value is None and self.data is not None:
            object.__setattr__(self, "value", self.data)

        if self.op == "patch" and self.patches is None:
            source = self.changes or []
            normalized: list[JsonPatchOperation] = []
            for patch in source:
                normalized.append(JsonPatchOperation.model_validate(patch))
            object.__setattr__(self, "patches", normalized)

        return self


class Plan(BaseModel):
    """Top-level plan payload for a Zendesk resource."""

    resource: str
    operations: Sequence[Operation]


def validate_plan(plan_data: dict) -> Plan:
    """Validate and coerce an arbitrary plan payload into the canonical model."""

    return Plan.model_validate(plan_data)


__all__ = ["Operation", "Plan", "validate_plan"]

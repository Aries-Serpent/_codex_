"""Pydantic models for validating Zendesk plan payloads."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class _BaseOperation(BaseModel):
    """Common settings for all plan operations."""

    model_config = ConfigDict(extra="forbid")


class AddOperation(_BaseOperation):
    """Create a new resource at the JSON pointer path."""

    op: Literal["add"]
    path: str
    value: Any


class RemoveOperation(_BaseOperation):
    """Delete the resource located at ``path``."""

    op: Literal["remove"]
    path: str


class JsonPatchOperation(BaseModel):
    """Single JSON Patch operation applied to an existing resource."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    op: str
    path: str | None = None
    value: Any | None = None
    from_: str | None = Field(default=None, alias="from")


class PatchOperation(_BaseOperation):
    """Apply JSON Patch operations to a named resource."""

    op: Literal["patch"]
    name: str
    patches: Sequence[JsonPatchOperation]


Operation = Annotated[
    AddOperation | PatchOperation | RemoveOperation,
    Field(discriminator="op"),
]


class Plan(BaseModel):
    """Top-level plan payload for a Zendesk resource."""

    resource: str
    operations: Sequence[Operation]


def validate_plan(plan_data: dict) -> Plan:
    """Validate and coerce an arbitrary plan payload into the canonical model."""

    return Plan.model_validate(plan_data)


__all__ = ["Operation", "Plan", "validate_plan"]

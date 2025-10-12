"""Pydantic models for validating Zendesk plan payloads."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, Field


class Operation(BaseModel):
    """A single plan operation to apply to a Zendesk resource."""

    op: Literal["create", "update", "delete"]
    id: int | None = Field(default=None)
    payload: dict = Field(default_factory=dict)


class Plan(BaseModel):
    """Top-level plan payload for a Zendesk resource."""

    resource: str
    operations: Sequence[Operation]


def validate_plan(plan_data: dict) -> Plan:
    """Validate and coerce an arbitrary plan payload into the canonical model."""

    return Plan.model_validate(plan_data)


__all__ = ["Operation", "Plan", "validate_plan"]

"""Dynamics 365 role and privilege models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DynamicsPrivilege(BaseModel):
    """A privilege entry in a Dynamics 365 role (entity-level permission)."""

    entity: str
    privilege: str
    level: str


class DynamicsRole(BaseModel):
    """Dynamics 365 security role with a set of privileges."""

    name: str
    privileges: list[DynamicsPrivilege] = Field(default_factory=list)

    def diff(self, other: DynamicsRole) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        self_set = {(p.entity, p.privilege, p.level) for p in self.privileges}
        other_set = {(p.entity, p.privilege, p.level) for p in other.privileges}
        if self_set != other_set:
            patches.append(
                {
                    "op": "replace",
                    "path": "/privileges",
                    "value": [priv.model_dump() for priv in self.privileges],
                }
            )
        return patches

"""
Pydantic models for Zendesk Groups and Memberships.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Membership(BaseModel):
    user_id: int
    group_id: int


class Group(BaseModel):
    name: str
    description: str = ""
    memberships: list[Membership] = Field(default_factory=list)

    def diff(self, other: Group) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.description != other.description:
            patches.append(
                {
                    "op": "replace",
                    "path": "/description",
                    "value": self.description,
                }
            )
        if self.memberships != other.memberships:
            patches.append(
                {
                    "op": "replace",
                    "path": "/memberships",
                    "value": [m.dict() for m in self.memberships],
                }
            )
        return patches

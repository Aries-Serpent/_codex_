"""Zendesk group models."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class Membership(_ZendeskBaseModel):
    """Association between a Zendesk user and group."""

    user_id: int = Field(..., description="Identifier of the Zendesk user")
    group_id: int = Field(..., description="Identifier of the Zendesk group")


class Group(_ZendeskBaseModel):
    """Zendesk group metadata including memberships."""

    name: str = Field(..., description="Name of the group")
    description: str | None = Field(
        default=None,
        description="Optional description shown in Zendesk UI",
    )
    memberships: list[Membership] = Field(
        default_factory=list,
        description="Members assigned to the group",
    )

    def diff(self, other: Group) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.description != other.description:
            patches.append({
                "op": "replace",
                "path": "/description",
                "value": self.description,
            })
        if _sorted_members(self.memberships) != _sorted_members(other.memberships):
            patches.append({
                "op": "replace",
                "path": "/memberships",
                "value": [_dump_membership(member) for member in self.memberships],
            })
        return patches


def _sorted_members(members: Iterable[Membership]) -> list[tuple[int, int]]:
    return sorted((member.user_id, member.group_id) for member in members)


def _dump_membership(member: Membership) -> dict[str, Any]:
    return member.model_dump(mode="json", exclude_none=True)

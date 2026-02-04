"""Models for Zendesk custom roles and permissions."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class ZendeskRolePermissions(_ZendeskBaseModel):
    """Simplified permissions flags for a Zendesk role."""

    tickets: bool = Field(False, description="Permission to manage tickets")
    users: bool = Field(False, description="Permission to manage end-users")


class Role(_ZendeskBaseModel):
    """Zendesk custom role with assigned permissions."""

    name: str
    permissions: ZendeskRolePermissions

    def diff(self, other: Role) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.permissions != other.permissions:
            patches.append(
                {
                    "op": "replace",
                    "path": "/permissions",
                    "value": self.permissions.model_dump(),
                }
            )
        return patches

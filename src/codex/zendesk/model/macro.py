"""
Pydantic models for Zendesk Macros.

This module defines a minimal representation of Zendesk macros for
configuration-as-code and diff generation.  Macros are reusable sets of
actions that agents can apply to tickets to streamline workflows.
"""

from typing import Any

from pydantic import Field

from .trigger import Action, _ZendeskBaseModel


class Macro(_ZendeskBaseModel):
    """A Zendesk macro consisting of a name and a list of actions."""

    name: str
    actions: list[Action] = Field(..., description="Actions executed when the macro is applied")
    active: bool = True

    def diff(self, other: "Macro") -> list[dict[str, Any]]:
        """
        Compute a list of JSON Patch operations needed to transform
        ``other`` into this macro.  Only the actions and active state
        are compared; macro IDs are assumed to be matched by name.
        """

        patches: list[dict[str, Any]] = []
        if self.active != other.active:
            patches.append({"op": "replace", "path": "/active", "value": self.active})
        if self.actions != other.actions:
            patches.append({"op": "replace", "path": "/actions", "value": self.actions})
        return patches

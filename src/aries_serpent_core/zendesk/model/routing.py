"""Models for Zendesk skills-based routing resources."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class Attribute(_ZendeskBaseModel):
    name: str
    required: bool = False


class SkillValue(_ZendeskBaseModel):
    attribute: str
    value: str


class AgentSkills(_ZendeskBaseModel):
    user_id: int
    skills: list[SkillValue] = Field(default_factory=list)

    def diff(self, other: AgentSkills) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.skills != other.skills:
            patches.append({"op": "replace", "path": "/skills", "value": self.skills})
        return patches


class TicketSkillsPolicy(_ZendeskBaseModel):
    required: list[SkillValue] = Field(default_factory=list)
    optional: list[SkillValue] = Field(default_factory=list)

    def diff(self, other: TicketSkillsPolicy) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.required != other.required:
            patches.append({"op": "replace", "path": "/required", "value": self.required})
        if self.optional != other.optional:
            patches.append({"op": "replace", "path": "/optional", "value": self.optional})
        return patches


class RoutingRule(_ZendeskBaseModel):
    """A skills-based or queue routing rule for ticket assignment."""

    name: str
    conditions: dict[str, Any] = Field(default_factory=dict)
    destination: str

    def diff(self, other: RoutingRule) -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.conditions != other.conditions:
            patches.append(
                {
                    "op": "replace",
                    "path": "/conditions",
                    "value": self.conditions,
                }
            )
        if self.destination != other.destination:
            patches.append(
                {
                    "op": "replace",
                    "path": "/destination",
                    "value": self.destination,
                }
            )
        return patches

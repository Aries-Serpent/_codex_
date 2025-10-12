"""
Pydantic models for Zendesk Web Widget configurations.

This model captures the admin-controlled aspects of the Classic and
Messaging widgets: snippet key and configuration settings.
"""

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class WidgetConfig(_ZendeskBaseModel):
    name: str
    snippet_key: str = Field(..., description="Unique key used to identify the widget")
    settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Widget settings such as theme and position",
    )
    channel: str = Field("classic", description="Channel type: classic or messaging")

    def diff(self, other: "WidgetConfig") -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.snippet_key != other.snippet_key:
            patches.append({"op": "replace", "path": "/snippet_key", "value": self.snippet_key})
        if self.settings != other.settings:
            patches.append({"op": "replace", "path": "/settings", "value": self.settings})
        if self.channel != other.channel:
            patches.append({"op": "replace", "path": "/channel", "value": self.channel})
        return patches

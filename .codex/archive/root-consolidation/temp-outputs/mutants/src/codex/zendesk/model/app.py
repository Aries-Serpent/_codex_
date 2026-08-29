"""
Pydantic models for Zendesk Apps (ZAF) metadata.

The models define properties needed to manage private Zendesk apps
via configuration-as-code: name, version, location, and manifest
contents (e.g., permissions and endpoints).
"""

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class App(_ZendeskBaseModel):
    name: str
    version: str = Field("1.0.0", description="Semantic version of the app")
    location: str = Field("admin", description="App location: admin or agent")
    manifest: dict[str, Any] = Field(default_factory=dict, description="ZAF manifest contents")

    def diff(self, other: "App") -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.version != other.version:
            patches.append({"op": "replace", "path": "/version", "value": self.version})
        if self.location != other.location:
            patches.append({"op": "replace", "path": "/location", "value": self.location})
        if self.manifest != other.manifest:
            patches.append({"op": "replace", "path": "/manifest", "value": self.manifest})
        return patches

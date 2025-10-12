"""
Pydantic models for Zendesk Guide theming and templating.

These models represent theme references and template patches used to
manage Copenhagen (or other) themes via configuration-as-code.
"""

from pydantic import BaseModel, Field


class GuideThemeRef(BaseModel):
    name: str
    brand: str
    version: str = Field(..., description="Theme version, e.g., 1.7.x")
    publish: bool = True

    def diff(self, other: "GuideThemeRef") -> list[dict[str, object]]:
        patches: list[dict[str, object]] = []
        if self.version != other.version:
            patches.append(
                {"op": "replace", "path": "/version", "value": self.version}
            )
        if self.publish != other.publish:
            patches.append(
                {"op": "replace", "path": "/publish", "value": self.publish}
            )
        return patches


class TemplatePatch(BaseModel):
    path: str
    content: str

    def diff(self, other: "TemplatePatch") -> list[dict[str, str]]:
        patches: list[dict[str, str]] = []
        if self.content != other.content:
            patches.append(
                {"op": "replace", "path": "/content", "value": self.content}
            )
        return patches

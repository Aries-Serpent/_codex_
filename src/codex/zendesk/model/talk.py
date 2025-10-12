"""
Pydantic models for Zendesk Talk (IVR and Voice) resources.

This module provides minimal schemas for Talk greetings, IVR menus,
routes, and phone number bindings. These are used to compute diffs
between desired and existing Talk configurations.
"""

from pydantic import Field

from .trigger import _ZendeskBaseModel


class Greeting(_ZendeskBaseModel):
    name: str
    url: str
    type: str = Field("greeting", description="Type of greeting: greeting or hold")

    def diff(self, other: "Greeting") -> list[dict[str, str]]:
        patches: list[dict[str, str]] = []
        if self.url != other.url:
            patches.append({"op": "replace", "path": "/url", "value": self.url})
        if self.type != other.type:
            patches.append({"op": "replace", "path": "/type", "value": self.type})
        return patches


class IVRRoute(_ZendeskBaseModel):
    keypress: str
    action: str
    target: str

    def diff(self, other: "IVRRoute") -> list[dict[str, str]]:
        patches: list[dict[str, str]] = []
        if self.action != other.action:
            patches.append({"op": "replace", "path": "/action", "value": self.action})
        if self.target != other.target:
            patches.append({"op": "replace", "path": "/target", "value": self.target})
        return patches


class IVRMenu(_ZendeskBaseModel):
    name: str
    greeting: Greeting
    routes: list[IVRRoute]

    def diff(self, other: "IVRMenu") -> list[dict[str, object]]:
        patches: list[dict[str, object]] = []
        if self.greeting != other.greeting:
            greeting_patches = self.greeting.diff(other.greeting)
            if greeting_patches:
                patches.append({"op": "replace", "path": "/greeting", "value": self.greeting})
        if self.routes != other.routes:
            patches.append({"op": "replace", "path": "/routes", "value": self.routes})
        return patches


class PhoneNumberBinding(_ZendeskBaseModel):
    phone_number: str
    ivr_menu: str | None = Field(None, description="IVR menu name bound to this number")

    def diff(self, other: "PhoneNumberBinding") -> list[dict[str, str | None]]:
        patches: list[dict[str, str | None]] = []
        if self.ivr_menu != other.ivr_menu:
            patches.append({"op": "replace", "path": "/ivr_menu", "value": self.ivr_menu})
        return patches

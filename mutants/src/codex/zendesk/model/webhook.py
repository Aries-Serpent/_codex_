"""
Pydantic models for Zendesk Webhooks.

Webhooks are HTTP endpoints that receive events from Zendesk triggers,
automations, or native event subscriptions.  This model represents the
admin-facing properties of a webhook.
"""

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class Webhook(_ZendeskBaseModel):
    name: str
    endpoint: str
    http_method: str = Field("POST", description="HTTP method used for delivery")
    request_format: str = Field("json", description="Payload format: json or form-encoded")
    subscriptions: list[str] = Field(
        default_factory=list,
        description="Event types or subscriptions associated with the webhook",
    )
    status: str = Field("inactive", description="Webhook status: active/inactive")

    def diff(self, other: "Webhook") -> list[dict[str, Any]]:
        patches: list[dict[str, Any]] = []
        if self.endpoint != other.endpoint:
            patches.append({"op": "replace", "path": "/endpoint", "value": self.endpoint})
        if self.http_method != other.http_method:
            patches.append({"op": "replace", "path": "/http_method", "value": self.http_method})
        if self.request_format != other.request_format:
            patches.append(
                {"op": "replace", "path": "/request_format", "value": self.request_format}
            )
        if self.subscriptions != other.subscriptions:
            patches.append({"op": "replace", "path": "/subscriptions", "value": self.subscriptions})
        if self.status != other.status:
            patches.append({"op": "replace", "path": "/status", "value": self.status})
        return patches

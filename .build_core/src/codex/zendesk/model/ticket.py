"""Zendesk Ticket models - API Contract definitions.

This module provides the authoritative Pydantic schema for Zendesk Ticket
objects, ensuring 1:1 mapping to the external Zendesk Suite API.

Schema Authority: This file defines immutable "Contracts" for SaaS interactions
to ensure reproducible agent behavior.

Reference:
    https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .trigger import _ZendeskBaseModel


class TicketComment(_ZendeskBaseModel):
    """Represents a comment on a Zendesk ticket."""

    id: int | None = Field(None, description="Comment ID")
    type: str = Field("Comment", description="Comment type")
    author_id: int = Field(..., description="User ID of comment author")
    body: str = Field(..., description="Comment body text")
    html_body: str | None = Field(None, description="HTML formatted body")
    plain_body: str | None = Field(None, description="Plain text body")
    public: bool = Field(True, description="Whether comment is public or internal")
    attachments: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of attachments",
    )
    created_at: str | None = Field(None, description="Comment creation timestamp")


class TicketVia(_ZendeskBaseModel):
    """Describes how a ticket was created."""

    channel: str = Field(..., description="Channel: web, email, api, phone, etc.")
    source: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional source metadata",
    )


class TicketCustomField(_ZendeskBaseModel):
    """Custom field value on a ticket."""

    id: int = Field(..., description="Custom field ID")
    value: Any = Field(None, description="Field value")


class Ticket(_ZendeskBaseModel):
    """Representation of a Zendesk Ticket.

    This model maps 1:1 to the Zendesk Ticket API schema, providing the
    authoritative contract for agent interactions with Zendesk tickets.

    Attributes aligned with Zendesk API v2:
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/
    """

    # Core identifiers
    id: int | None = Field(None, description="Ticket ID (read-only)")
    url: str | None = Field(None, description="API URL for this ticket (read-only)")
    external_id: str | None = Field(
        None,
        description="External identifier for linking to external systems",
    )

    # Ticket metadata
    type: str | None = Field(
        None,
        description="Ticket type: problem, incident, question, or task",
    )
    subject: str = Field(..., description="Ticket subject line")
    raw_subject: str | None = Field(None, description="Unprocessed subject (read-only)")
    description: str = Field(..., description="Initial ticket description/comment")

    # Priority and status
    priority: str | None = Field(
        None,
        description="Ticket priority: urgent, high, normal, or low",
    )
    status: str = Field(
        "new",
        description="Ticket status: new, open, pending, hold, solved, closed",
    )

    # Assignment
    requester_id: int = Field(..., description="User ID of the requester")
    submitter_id: int | None = Field(
        None,
        description="User ID of the submitter (defaults to requester)",
    )
    assignee_id: int | None = Field(None, description="Assigned agent user ID")
    assignee_email: str | None = Field(None, description="Assigned agent email")
    group_id: int | None = Field(None, description="Assigned group ID")
    collaborator_ids: list[int] = Field(
        default_factory=list,
        description="List of user IDs who are CC'd on the ticket",
    )
    follower_ids: list[int] = Field(
        default_factory=list,
        description="List of user IDs following the ticket",
    )

    # Ticket metadata and organization
    organization_id: int | None = Field(
        None,
        description="Organization ID of the requester",
    )
    forum_topic_id: int | None = Field(None, description="Associated forum topic ID")
    problem_id: int | None = Field(
        None,
        description="Problem ticket ID if this is an incident",
    )
    has_incidents: bool = Field(
        False,
        description="Whether this ticket has linked incidents",
    )

    # Timestamps
    created_at: str | None = Field(None, description="Ticket creation timestamp (read-only)")
    updated_at: str | None = Field(None, description="Last update timestamp (read-only)")
    due_at: str | None = Field(None, description="Due date for task tickets")

    # Tags and custom fields
    tags: list[str] = Field(default_factory=list, description="Ticket tags")
    custom_fields: list[TicketCustomField] = Field(
        default_factory=list,
        description="Custom field values",
    )

    # Additional metadata
    via: TicketVia | None = Field(None, description="How the ticket was created")
    brand_id: int | None = Field(None, description="Brand ID")
    satisfaction_rating: dict[str, Any] | None = Field(
        None,
        description="Customer satisfaction rating (read-only)",
    )
    sharing_agreement_ids: list[int] = Field(
        default_factory=list,
        description="Sharing agreement IDs",
    )

    # Comments (for ticket creation)
    comment: TicketComment | None = Field(
        None,
        description="Initial comment when creating ticket",
    )

    # Additional fields for agent workflow
    is_public: bool = Field(True, description="Whether ticket is publicly visible")
    recipient: str | None = Field(None, description="Original recipient email address")

    # SLA and metrics (read-only)
    sla_policy_id: int | None = Field(None, description="Applied SLA policy ID")
    metric_set_id: int | None = Field(None, description="Ticket metric set ID")

    def diff(self, other: Ticket) -> list[dict[str, Any]]:
        """Return JSON patch operations describing differences with ``other``.

        This enables drift detection and change tracking for ticket state.

        Args:
            other: Another Ticket instance to compare against

        Returns:
            List of JSON Patch operations
        """
        patches: list[dict[str, Any]] = []

        # Compare mutable fields that can be updated via API
        mutable_fields = [
            "subject",
            "description",
            "type",
            "priority",
            "status",
            "assignee_id",
            "group_id",
            "tags",
            "custom_fields",
            "collaborator_ids",
            "follower_ids",
            "external_id",
            "problem_id",
            "due_at",
        ]

        for field_name in mutable_fields:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)

            if self_value != other_value:
                patches.append(
                    {
                        "op": "replace",
                        "path": f"/{field_name}",
                        "value": self_value,
                    }
                )

        return patches

    def to_api_payload(self, *, for_create: bool = True) -> dict[str, Any]:
        """Convert to Zendesk API request payload.

        Args:
            for_create: If True, format for ticket creation (POST)
                       If False, format for ticket update (PUT)

        Returns:
            Dictionary suitable for Zendesk API request
        """
        if for_create:
            # For creation, only include fields that can be set
            payload = {
                "subject": self.subject,
                "description": self.description,
                "requester_id": self.requester_id,
            }

            # Optional fields for creation
            optional_fields = [
                "type",
                "priority",
                "status",
                "tags",
                "assignee_id",
                "group_id",
                "custom_fields",
                "collaborator_ids",
                "external_id",
                "problem_id",
                "brand_id",
                "via",
                "due_at",
                "submitter_id",
            ]

            for field in optional_fields:
                value = getattr(self, field)
                if value is not None and (not isinstance(value, list) or value):
                    if field == "custom_fields":
                        payload[field] = [{"id": cf.id, "value": cf.value} for cf in value]
                    elif hasattr(value, "model_dump"):
                        payload[field] = value.model_dump(exclude_none=True)
                    else:
                        payload[field] = value

            # Add initial comment if provided
            if self.comment:
                payload["comment"] = {
                    "body": self.comment.body,
                    "public": self.comment.public,
                }
                if self.comment.html_body:
                    payload["comment"]["html_body"] = self.comment.html_body  # type: ignore[index]

            return {"ticket": payload}

        # For updates, only include changed fields
        # Caller should use diff() to determine what to update
        return self.model_dump(
            exclude_none=True,
            exclude={"id", "url", "created_at", "updated_at", "raw_subject"},
        )


class TicketRequest(_ZendeskBaseModel):
    """Wrapper for ticket requests to the API."""

    ticket: Ticket = Field(..., description="Ticket object")


class TicketResponse(_ZendeskBaseModel):
    """Response from Zendesk API for ticket operations."""

    ticket: Ticket = Field(..., description="Ticket object")


class TicketListResponse(_ZendeskBaseModel):
    """Response for list operations."""

    tickets: list[Ticket] = Field(default_factory=list, description="List of tickets")
    next_page: str | None = Field(None, description="URL for next page of results")
    previous_page: str | None = Field(None, description="URL for previous page")
    count: int | None = Field(None, description="Total count of tickets")


__all__ = [
    "Ticket",
    "TicketComment",
    "TicketCustomField",
    "TicketListResponse",
    "TicketRequest",
    "TicketResponse",
    "TicketVia",
]

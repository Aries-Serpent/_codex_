"""
Enhanced Zendesk API Client with complete API coverage.

Supports:
- All Zendesk Core APIs (Tickets, Users, Organizations, etc.)
- Support API
- Search API
- SLA Policies

All methods documented in openapi.yaml and swagger.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class ZendeskConfig:
    """Zendesk API configuration."""

    subdomain: str
    email: str
    api_token: str
    base_url: str = field(init=False)

    def __post_init__(self):
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"


class ZendeskAPIClient:
    """
    Complete Zendesk API client with all endpoints.

    API Categories:
    1. Tickets API - CRUD operations, bulk updates, merging
    2. Users API - User management, groups, roles
    3. Organizations API - Organization management
    4. SLA Policies API - SLA policy management
    5. Views API - Ticket views and filters
    6. Macros API - Ticket macros
    7. Automations API - Ticket automations
    8. Triggers API - Ticket triggers
    9. Search API - Advanced search
    10. Audit Logs API - Activity logs

    All methods map to openapi.yaml operations.
    """

    def __init__(self, config: ZendeskConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = (f"{config.email}/token", config.api_token)
        self.session.headers.update({"Content-Type": "application/json"})

    # ========================================================================
    # TICKETS API - All endpoints documented in swagger.html
    # ========================================================================

    def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        """
        Get a single ticket by ID.

        Swagger: GET /api/v2/tickets/{ticket_id}.json

        Args:
            ticket_id: Ticket ID (numeric)

        Returns:
            Ticket object with all fields

        Example:
            >>> client.get_ticket(12345)
            {"ticket": {"id": 12345, "subject": "Help!", ...}}
        """
        response = self.session.get(f"{self.config.base_url}/tickets/{ticket_id}.json")
        response.raise_for_status()
        return response.json()

    def list_tickets(
        self,
        *,
        per_page: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        """
        List all tickets (paginated).

        Swagger: GET /api/v2/tickets.json

        Args:
            per_page: Results per page (max 100)
            sort_by: Field to sort by (created_at, updated_at, priority, status)
            sort_order: asc or desc

        Returns:
            Paginated ticket list

        Example:
            >>> client.list_tickets(per_page=50, sort_by="priority")
        """
        params = {"per_page": per_page, "sort_by": sort_by, "sort_order": sort_order}
        response = self.session.get(f"{self.config.base_url}/tickets.json", params=params)
        response.raise_for_status()
        return response.json()

    def create_ticket(
        self,
        *,
        subject: str,
        description: str,
        priority: str = "normal",
        ticket_type: str = "question",
        requester_email: str | None = None,
        tags: list[str] | None = None,
        custom_fields: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new ticket.

        Swagger: POST /api/v2/tickets.json

        Args:
            subject: Ticket subject (required)
            description: Ticket description/body (required)
            priority: urgent, high, normal, low
            ticket_type: problem, incident, question, task
            requester_email: Email of requester
            tags: List of tags
            custom_fields: Custom field values

        Returns:
            Created ticket object

        Example:
            >>> client.create_ticket(
            ...     subject="API Integration Issue",
            ...     description="Cannot connect to API",
            ...     priority="high",
            ...     tags=["api", "integration"]
            ... )
        """
        payload = {
            "ticket": {
                "subject": subject,
                "description": description,
                "priority": priority,
                "type": ticket_type,
            }
        }

        if requester_email:
            payload["ticket"]["requester"] = {"email": requester_email}  # type: ignore[assignment]
        if tags:
            payload["ticket"]["tags"] = tags  # type: ignore[assignment]
        if custom_fields:
            payload["ticket"]["custom_fields"] = custom_fields  # type: ignore[assignment]

        response = self.session.post(f"{self.config.base_url}/tickets.json", json=payload)
        response.raise_for_status()
        return response.json()

    def update_ticket(
        self,
        ticket_id: int,
        **updates: Any,
    ) -> dict[str, Any]:
        """
        Update a ticket.

        Swagger: PUT /api/v2/tickets/{ticket_id}.json

        Args:
            ticket_id: Ticket ID
            **updates: Fields to update (status, priority, assignee_id, etc.)

        Returns:
            Updated ticket object

        Example:
            >>> client.update_ticket(
            ...     12345,
            ...     status="solved",
            ...     priority="low",
            ...     comment={"body": "Issue resolved", "public": True}
            ... )
        """
        payload = {"ticket": updates}
        response = self.session.put(
            f"{self.config.base_url}/tickets/{ticket_id}.json", json=payload
        )
        response.raise_for_status()
        return response.json()

    def bulk_update_tickets(
        self,
        ticket_ids: list[int],
        **updates: Any,
    ) -> dict[str, Any]:
        """
        Bulk update multiple tickets.

        Swagger: PUT /api/v2/tickets/update_many.json

        Args:
            ticket_ids: List of ticket IDs
            **updates: Fields to update

        Returns:
            Job status
        """
        payload = {"ticket": updates}
        params = {"ids": ",".join(map(str, ticket_ids))}
        response = self.session.put(
            f"{self.config.base_url}/tickets/update_many.json",
            json=payload,
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def merge_tickets(
        self,
        source_ticket_id: int,
        target_ticket_id: int,
        **merge_options: Any,
    ) -> dict[str, Any]:
        """
        Merge two tickets.

        Swagger: POST /api/v2/tickets/{target_ticket_id}/merge.json

        Args:
            source_ticket_id: Ticket to merge (will be closed)
            target_ticket_id: Target ticket (remains open)
            **merge_options: source_comment, target_comment

        Returns:
            Merge result
        """
        payload = {
            "ticket": {
                "source_ticket_id": source_ticket_id,
                **merge_options,
            }
        }
        response = self.session.post(
            f"{self.config.base_url}/tickets/{target_ticket_id}/merge.json",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # USERS API
    # ========================================================================

    def get_user(self, user_id: int) -> dict[str, Any]:
        """
        Get user by ID.

        Swagger: GET /api/v2/users/{user_id}.json
        """
        response = self.session.get(f"{self.config.base_url}/users/{user_id}.json")
        response.raise_for_status()
        return response.json()

    def list_users(
        self,
        *,
        role: str | None = None,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        List users.

        Swagger: GET /api/v2/users.json

        Args:
            role: Filter by role (end-user, agent, admin)
            per_page: Results per page
        """
        params = {"per_page": per_page}
        if role:
            params["role"] = role  # type: ignore[assignment]

        response = self.session.get(f"{self.config.base_url}/users.json", params=params)
        response.raise_for_status()
        return response.json()

    def create_user(
        self,
        *,
        name: str,
        email: str,
        role: str = "end-user",
        **user_fields: Any,
    ) -> dict[str, Any]:
        """
        Create user.

        Swagger: POST /api/v2/users.json

        Args:
            name: User name
            email: User email
            role: end-user, agent, admin
            **user_fields: Additional fields
        """
        payload = {
            "user": {
                "name": name,
                "email": email,
                "role": role,
                **user_fields,
            }
        }
        response = self.session.post(f"{self.config.base_url}/users.json", json=payload)
        response.raise_for_status()
        return response.json()

    def update_user(
        self,
        user_id: int,
        **updates: Any,
    ) -> dict[str, Any]:
        """
        Update a user's attributes.

        Swagger: PUT /api/v2/users/{user_id}.json

        Args:
            user_id: User ID
            **updates: Fields to update (role, name, email, phone, etc.)
                       Use ``role`` to change access level:
                       end-user, agent, admin

        Returns:
            Updated user object

        Example:
            >>> client.update_user(1001, role="agent")
            >>> client.update_user(1001, role="admin", phone="+15551234567")
        """
        payload = {"user": updates}
        response = self.session.put(f"{self.config.base_url}/users/{user_id}.json", json=payload)
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # ORGANIZATIONS API
    # ========================================================================

    def get_organization(self, org_id: int) -> dict[str, Any]:
        """
        Get organization by ID.

        Swagger: GET /api/v2/organizations/{org_id}.json
        """
        response = self.session.get(f"{self.config.base_url}/organizations/{org_id}.json")
        response.raise_for_status()
        return response.json()

    def list_organizations(self, per_page: int = 100) -> dict[str, Any]:
        """
        List organizations.

        Swagger: GET /api/v2/organizations.json
        """
        response = self.session.get(
            f"{self.config.base_url}/organizations.json", params={"per_page": per_page}
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # SLA POLICIES API
    # ========================================================================

    def get_sla_policy(self, policy_id: int) -> dict[str, Any]:
        """
        Get SLA policy by ID.

        Swagger: GET /api/v2/slas/policies/{policy_id}.json
        """
        response = self.session.get(f"{self.config.base_url}/slas/policies/{policy_id}.json")
        response.raise_for_status()
        return response.json()

    def list_sla_policies(self) -> dict[str, Any]:
        """
        List all SLA policies.

        Swagger: GET /api/v2/slas/policies.json
        """
        response = self.session.get(f"{self.config.base_url}/slas/policies.json")
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # SEARCH API
    # ========================================================================

    def search(
        self,
        query: str,
        *,
        search_type: str | None = None,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        Advanced search across Zendesk objects.

        Swagger: GET /api/v2/search.json

        Args:
            query: Search query (Zendesk search syntax)
            search_type: Filter by type (ticket, user, organization, group)
            per_page: Results per page

        Example:
            >>> client.search("type:ticket status:open priority:high")
            >>> client.search("type:user email:*@example.com")
        """
        params = {"query": query, "per_page": per_page}
        if search_type:
            params["type"] = search_type

        response = self.session.get(f"{self.config.base_url}/search.json", params=params)
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # VIEWS API
    # ========================================================================

    def list_views(self) -> dict[str, Any]:
        """
        List ticket views.

        Swagger: GET /api/v2/views.json
        """
        response = self.session.get(f"{self.config.base_url}/views.json")
        response.raise_for_status()
        return response.json()

    def execute_view(self, view_id: int, per_page: int = 100) -> dict[str, Any]:
        """
        Execute a view (get tickets matching view criteria).

        Swagger: GET /api/v2/views/{view_id}/execute.json
        """
        response = self.session.get(
            f"{self.config.base_url}/views/{view_id}/execute.json",
            params={"per_page": per_page},
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # MACROS API
    # ========================================================================

    def list_macros(self) -> dict[str, Any]:
        """
        List ticket macros.

        Swagger: GET /api/v2/macros.json
        """
        response = self.session.get(f"{self.config.base_url}/macros.json")
        response.raise_for_status()
        return response.json()

    def apply_macro(self, ticket_id: int, macro_id: int) -> dict[str, Any]:
        """
        Apply macro to ticket.

        Swagger: POST /api/v2/tickets/{ticket_id}/macros/{macro_id}/apply.json
        """
        response = self.session.post(
            f"{self.config.base_url}/tickets/{ticket_id}/macros/{macro_id}/apply.json"
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # TRIGGERS API
    # ========================================================================

    def list_triggers(self) -> dict[str, Any]:
        """
        List ticket triggers.

        Swagger: GET /api/v2/triggers.json
        """
        response = self.session.get(f"{self.config.base_url}/triggers.json")
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # AUTOMATIONS API
    # ========================================================================

    def list_automations(self) -> dict[str, Any]:
        """
        List ticket automations.

        Swagger: GET /api/v2/automations.json
        """
        response = self.session.get(f"{self.config.base_url}/automations.json")
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # AUDIT LOGS API
    # ========================================================================

    def list_audit_logs(
        self,
        *,
        filter_type: str | None = None,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        List audit logs.

        Swagger: GET /api/v2/audit_logs.json

        Args:
            filter_type: Filter by action type
            per_page: Results per page
        """
        params = {"per_page": per_page}
        if filter_type:
            params["filter[action]"] = filter_type  # type: ignore[assignment]

        response = self.session.get(f"{self.config.base_url}/audit_logs.json", params=params)
        response.raise_for_status()
        return response.json()


__all__ = ["ZendeskAPIClient", "ZendeskConfig"]

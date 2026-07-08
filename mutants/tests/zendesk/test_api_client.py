"""
Comprehensive test suite for Zendesk API Client.

Tests cover:
- All API endpoints (Tickets, Users, Organizations, SLA Policies, etc.)
- Error handling scenarios
- Mock responses using responses library
- Pagination handling

All tests use mocked responses - no real Zendesk API calls.
"""

from __future__ import annotations

import pytest

responses = pytest.importorskip("responses")
from responses import matchers

from zendesk.api_client import ZendeskAPIClient, ZendeskConfig

# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def zendesk_config() -> ZendeskConfig:
    """Create a test Zendesk configuration."""
    return ZendeskConfig(
        subdomain="testcompany",
        email="agent@testcompany.com",
        api_token="test_api_token_12345",
    )


@pytest.fixture
def api_client(zendesk_config: ZendeskConfig) -> ZendeskAPIClient:
    """Create a test API client."""
    return ZendeskAPIClient(zendesk_config)


# ==============================================================================
# TEST CONFIG
# ==============================================================================


class TestZendeskConfig:
    """Tests for ZendeskConfig class."""

    def test_config_creates_correct_base_url(self) -> None:
        """Test that config creates the correct base URL."""
        config = ZendeskConfig(
            subdomain="mycompany",
            email="agent@example.com",
            api_token="token123",
        )
        assert config.base_url == "https://mycompany.zendesk.com/api/v2", "base_url is not valid"

    def test_config_stores_all_fields(self) -> None:
        """Test that config stores all provided fields."""
        config = ZendeskConfig(
            subdomain="test",
            email="test@test.com",
            api_token="abc123",
        )
        assert config.subdomain == "test", "subdomain is not valid"
        assert config.email == "test@test.com", "email is not valid"
        assert config.api_token == "abc123", "api_token is not valid"


# ==============================================================================
# TEST TICKETS API
# ==============================================================================


class TestTicketsAPI:
    """Tests for Tickets API endpoints."""

    @responses.activate
    def test_get_ticket(self, api_client: ZendeskAPIClient) -> None:
        """Test getting a single ticket."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/tickets/12345.json",
            json={
                "ticket": {
                    "id": 12345,
                    "subject": "Test Ticket",
                    "status": "open",
                    "priority": "normal",
                }
            },
            status=200,
        )

        result = api_client.get_ticket(12345)

        assert result["ticket"]["id"] == 12345, "Result must not be empty"
        assert result["ticket"]["subject"] == "Test Ticket", "Result must not be empty"

    @responses.activate
    def test_list_tickets(self, api_client: ZendeskAPIClient) -> None:
        """Test listing tickets with pagination parameters."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={
                "tickets": [
                    {"id": 1, "subject": "Ticket 1"},
                    {"id": 2, "subject": "Ticket 2"},
                ],
                "count": 2,
                "next_page": None,
            },
            status=200,
            match=[
                matchers.query_param_matcher(
                    {"per_page": "50", "sort_by": "created_at", "sort_order": "desc"}
                )
            ],
        )

        result = api_client.list_tickets(per_page=50)

        assert len(result["tickets"]) == 2, "Collection must not be empty"
        assert result["count"] == 2, "Result must not be empty"

    @responses.activate
    def test_create_ticket(self, api_client: ZendeskAPIClient) -> None:
        """Test creating a new ticket."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={
                "ticket": {
                    "id": 99999,
                    "subject": "New Ticket",
                    "description": "Description here",
                    "priority": "high",
                    "status": "new",
                }
            },
            status=201,
        )

        result = api_client.create_ticket(
            subject="New Ticket",
            description="Description here",
            priority="high",
        )

        assert result["ticket"]["id"] == 99999, "Result must not be empty"
        assert result["ticket"]["subject"] == "New Ticket", "Result must not be empty"

    @responses.activate
    def test_create_ticket_with_requester(self, api_client: ZendeskAPIClient) -> None:
        """Test creating a ticket with requester email."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={"ticket": {"id": 100, "requester": {"email": "customer@example.com"}}},
            status=201,
        )

        result = api_client.create_ticket(
            subject="Support Request",
            description="Need help",
            requester_email="customer@example.com",
        )

        assert "ticket" in result, "Result must not be empty"

    @responses.activate
    def test_create_ticket_with_tags(self, api_client: ZendeskAPIClient) -> None:
        """Test creating a ticket with tags."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={"ticket": {"id": 101, "tags": ["urgent", "billing"]}},
            status=201,
        )

        result = api_client.create_ticket(
            subject="Billing Issue",
            description="Billing question",
            tags=["urgent", "billing"],
        )

        assert "ticket" in result, "Result must not be empty"

    @responses.activate
    def test_update_ticket(self, api_client: ZendeskAPIClient) -> None:
        """Test updating a ticket."""
        responses.add(
            responses.PUT,
            "https://testcompany.zendesk.com/api/v2/tickets/12345.json",
            json={"ticket": {"id": 12345, "status": "pending", "priority": "high"}},
            status=200,
        )

        result = api_client.update_ticket(12345, status="pending", priority="high")

        assert result["ticket"]["status"] == "pending", "Result must not be empty"
        assert result["ticket"]["priority"] == "high", "Result must not be empty"

    @responses.activate
    def test_bulk_update_tickets(self, api_client: ZendeskAPIClient) -> None:
        """Test bulk updating multiple tickets."""
        responses.add(
            responses.PUT,
            "https://testcompany.zendesk.com/api/v2/tickets/update_many.json",
            json={
                "job_status": {
                    "id": "job123",
                    "status": "queued",
                    "total": 3,
                }
            },
            status=200,
        )

        result = api_client.bulk_update_tickets([1, 2, 3], status="solved")

        assert result["job_status"]["status"] == "queued", "Result must not be empty"
        assert result["job_status"]["total"] == 3, "Result must not be empty"

    @responses.activate
    def test_merge_tickets(self, api_client: ZendeskAPIClient) -> None:
        """Test merging two tickets."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets/100/merge.json",
            json={"ticket": {"id": 100, "merged_ticket_ids": [200]}},
            status=200,
        )

        result = api_client.merge_tickets(
            source_ticket_id=200, target_ticket_id=100, source_comment="Merged"
        )

        assert "ticket" in result, "Result must not be empty"


# ==============================================================================
# TEST USERS API
# ==============================================================================


class TestUsersAPI:
    """Tests for Users API endpoints."""

    @responses.activate
    def test_get_user(self, api_client: ZendeskAPIClient) -> None:
        """Test getting a single user."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/users/1001.json",
            json={
                "user": {
                    "id": 1001,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "agent",
                }
            },
            status=200,
        )

        result = api_client.get_user(1001)

        assert result["user"]["id"] == 1001, "Result must not be empty"
        assert result["user"]["name"] == "John Doe", "Result must not be empty"

    @responses.activate
    def test_list_users(self, api_client: ZendeskAPIClient) -> None:
        """Test listing users."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/users.json",
            json={
                "users": [
                    {"id": 1, "name": "User 1"},
                    {"id": 2, "name": "User 2"},
                ],
                "count": 2,
            },
            status=200,
        )

        result = api_client.list_users()

        assert len(result["users"]) == 2, "Collection must not be empty"

    @responses.activate
    def test_list_users_with_role_filter(self, api_client: ZendeskAPIClient) -> None:
        """Test listing users filtered by role."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/users.json",
            json={"users": [{"id": 1, "name": "Agent 1", "role": "agent"}]},
            status=200,
            match=[matchers.query_param_matcher({"per_page": "100", "role": "agent"})],
        )

        result = api_client.list_users(role="agent")

        assert len(result["users"]) == 1, "Collection must not be empty"

    @responses.activate
    def test_create_user(self, api_client: ZendeskAPIClient) -> None:
        """Test creating a new user."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/users.json",
            json={
                "user": {
                    "id": 9999,
                    "name": "New User",
                    "email": "newuser@example.com",
                    "role": "end-user",
                }
            },
            status=201,
        )

        result = api_client.create_user(name="New User", email="newuser@example.com")

        assert result["user"]["id"] == 9999, "Result must not be empty"
        assert result["user"]["email"] == "newuser@example.com", "Result must not be empty"

    @responses.activate
    def test_update_user_role(self, api_client: ZendeskAPIClient) -> None:
        """Test updating a user's role (access level)."""
        responses.add(
            responses.PUT,
            "https://testcompany.zendesk.com/api/v2/users/1001.json",
            json={
                "user": {
                    "id": 1001,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "agent",
                }
            },
            status=200,
        )

        result = api_client.update_user(1001, role="agent")

        assert result["user"]["id"] == 1001, "Result must not be empty"
        assert result["user"]["role"] == "agent", "Result must not be empty"

    @responses.activate
    def test_update_user_multiple_fields(self, api_client: ZendeskAPIClient) -> None:
        """Test updating multiple user fields at once."""
        responses.add(
            responses.PUT,
            "https://testcompany.zendesk.com/api/v2/users/1001.json",
            json={
                "user": {
                    "id": 1001,
                    "name": "Jane Doe",
                    "role": "admin",
                    "phone": "+15551234567",
                }
            },
            status=200,
        )

        result = api_client.update_user(1001, name="Jane Doe", role="admin", phone="+15551234567")

        assert result["user"]["name"] == "Jane Doe", "Result must not be empty"
        assert result["user"]["role"] == "admin", "Result must not be empty"
        assert result["user"]["phone"] == "+15551234567", "Result must not be empty"


# ==============================================================================
# TEST ORGANIZATIONS API
# ==============================================================================


class TestOrganizationsAPI:
    """Tests for Organizations API endpoints."""

    @responses.activate
    def test_get_organization(self, api_client: ZendeskAPIClient) -> None:
        """Test getting a single organization."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/organizations/500.json",
            json={
                "organization": {
                    "id": 500,
                    "name": "Acme Corp",
                    "domain_names": ["acme.com"],
                }
            },
            status=200,
        )

        result = api_client.get_organization(500)

        assert result["organization"]["id"] == 500, "Result must not be empty"
        assert result["organization"]["name"] == "Acme Corp", "Result must not be empty"

    @responses.activate
    def test_list_organizations(self, api_client: ZendeskAPIClient) -> None:
        """Test listing organizations."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/organizations.json",
            json={
                "organizations": [
                    {"id": 1, "name": "Org 1"},
                    {"id": 2, "name": "Org 2"},
                ],
                "count": 2,
            },
            status=200,
        )

        result = api_client.list_organizations()

        assert len(result["organizations"]) == 2, "Collection must not be empty"


# ==============================================================================
# TEST SLA POLICIES API
# ==============================================================================


class TestSLAPoliciesAPI:
    """Tests for SLA Policies API endpoints."""

    @responses.activate
    def test_get_sla_policy(self, api_client: ZendeskAPIClient) -> None:
        """Test getting a single SLA policy."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/slas/policies/10.json",
            json={
                "sla_policy": {
                    "id": 10,
                    "title": "Premium SLA",
                    "description": "For premium customers",
                }
            },
            status=200,
        )

        result = api_client.get_sla_policy(10)

        assert result["sla_policy"]["id"] == 10, "Result must not be empty"
        assert result["sla_policy"]["title"] == "Premium SLA", "Result must not be empty"

    @responses.activate
    def test_list_sla_policies(self, api_client: ZendeskAPIClient) -> None:
        """Test listing SLA policies."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/slas/policies.json",
            json={
                "sla_policies": [
                    {"id": 1, "title": "Standard SLA"},
                    {"id": 2, "title": "Premium SLA"},
                ]
            },
            status=200,
        )

        result = api_client.list_sla_policies()

        assert len(result["sla_policies"]) == 2, "Collection must not be empty"


# ==============================================================================
# TEST SEARCH API
# ==============================================================================


class TestSearchAPI:
    """Tests for Search API endpoints."""

    @responses.activate
    def test_search(self, api_client: ZendeskAPIClient) -> None:
        """Test basic search."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/search.json",
            json={
                "results": [
                    {"id": 1, "result_type": "ticket", "subject": "Found Ticket"},
                ],
                "count": 1,
                "facets": None,
            },
            status=200,
        )

        result = api_client.search("type:ticket status:open")

        assert len(result["results"]) == 1, "Collection must not be empty"
        assert result["results"][0]["result_type"] == "ticket", "Result must not be empty"

    @responses.activate
    def test_search_with_type_filter(self, api_client: ZendeskAPIClient) -> None:
        """Test search with type filter."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/search.json",
            json={"results": [{"id": 1, "result_type": "user"}], "count": 1},
            status=200,
            match=[
                matchers.query_param_matcher(
                    {"query": "email:*@example.com", "per_page": "100", "type": "user"}
                )
            ],
        )

        result = api_client.search("email:*@example.com", search_type="user")

        assert result["count"] == 1, "Result must not be empty"


# ==============================================================================
# TEST VIEWS API
# ==============================================================================


class TestViewsAPI:
    """Tests for Views API endpoints."""

    @responses.activate
    def test_list_views(self, api_client: ZendeskAPIClient) -> None:
        """Test listing views."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/views.json",
            json={
                "views": [
                    {"id": 1, "title": "All unsolved tickets"},
                    {"id": 2, "title": "My assigned tickets"},
                ]
            },
            status=200,
        )

        result = api_client.list_views()

        assert len(result["views"]) == 2, "Collection must not be empty"

    @responses.activate
    def test_execute_view(self, api_client: ZendeskAPIClient) -> None:
        """Test executing a view."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/views/1/execute.json",
            json={
                "rows": [
                    {"ticket": {"id": 100, "subject": "Ticket 1"}},
                    {"ticket": {"id": 101, "subject": "Ticket 2"}},
                ]
            },
            status=200,
        )

        result = api_client.execute_view(1)

        assert len(result["rows"]) == 2, "Collection must not be empty"


# ==============================================================================
# TEST MACROS API
# ==============================================================================


class TestMacrosAPI:
    """Tests for Macros API endpoints."""

    @responses.activate
    def test_list_macros(self, api_client: ZendeskAPIClient) -> None:
        """Test listing macros."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/macros.json",
            json={
                "macros": [
                    {"id": 1, "title": "Close and redirect"},
                    {"id": 2, "title": "Request more info"},
                ]
            },
            status=200,
        )

        result = api_client.list_macros()

        assert len(result["macros"]) == 2, "Collection must not be empty"

    @responses.activate
    def test_apply_macro(self, api_client: ZendeskAPIClient) -> None:
        """Test applying a macro to a ticket."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets/100/macros/1/apply.json",
            json={"result": {"ticket": {"id": 100, "comment": {"body": "Macro applied"}}}},
            status=200,
        )

        result = api_client.apply_macro(ticket_id=100, macro_id=1)

        assert "result" in result, "Result must not be empty"


# ==============================================================================
# TEST TRIGGERS API
# ==============================================================================


class TestTriggersAPI:
    """Tests for Triggers API endpoints."""

    @responses.activate
    def test_list_triggers(self, api_client: ZendeskAPIClient) -> None:
        """Test listing triggers."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/triggers.json",
            json={
                "triggers": [
                    {"id": 1, "title": "Notify assignee"},
                    {"id": 2, "title": "Auto-tag VIP"},
                ]
            },
            status=200,
        )

        result = api_client.list_triggers()

        assert len(result["triggers"]) == 2, "Collection must not be empty"


# ==============================================================================
# TEST AUTOMATIONS API
# ==============================================================================


class TestAutomationsAPI:
    """Tests for Automations API endpoints."""

    @responses.activate
    def test_list_automations(self, api_client: ZendeskAPIClient) -> None:
        """Test listing automations."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/automations.json",
            json={
                "automations": [
                    {"id": 1, "title": "Close stale tickets"},
                    {"id": 2, "title": "Escalate urgent"},
                ]
            },
            status=200,
        )

        result = api_client.list_automations()

        assert len(result["automations"]) == 2, "Collection must not be empty"


# ==============================================================================
# TEST AUDIT LOGS API
# ==============================================================================


class TestAuditLogsAPI:
    """Tests for Audit Logs API endpoints."""

    @responses.activate
    def test_list_audit_logs(self, api_client: ZendeskAPIClient) -> None:
        """Test listing audit logs."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/audit_logs.json",
            json={
                "audit_logs": [
                    {
                        "id": 1,
                        "action": "create",
                        "source_type": "ticket",
                        "source_id": 100,
                    },
                ]
            },
            status=200,
        )

        result = api_client.list_audit_logs()

        assert len(result["audit_logs"]) == 1, "Collection must not be empty"

    @responses.activate
    def test_list_audit_logs_with_filter(self, api_client: ZendeskAPIClient) -> None:
        """Test listing audit logs with type filter."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/audit_logs.json",
            json={"audit_logs": [{"id": 1, "action": "update"}]},
            status=200,
            match=[matchers.query_param_matcher({"per_page": "100", "filter[action]": "update"})],
        )

        result = api_client.list_audit_logs(filter_type="update")

        assert len(result["audit_logs"]) == 1, "Collection must not be empty"


# ==============================================================================
# TEST ERROR HANDLING
# ==============================================================================


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @responses.activate
    def test_404_not_found(self, api_client: ZendeskAPIClient) -> None:
        """Test handling of 404 Not Found error."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/tickets/99999.json",
            json={"error": "RecordNotFound", "description": "Not found"},
            status=404,
        )

        with pytest.raises(Exception) as exc_info:
            api_client.get_ticket(99999)

        assert "404" in str(exc_info.value), "Value must be initialized"

    @responses.activate
    def test_401_unauthorized(self, api_client: ZendeskAPIClient) -> None:
        """Test handling of 401 Unauthorized error."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/tickets/1.json",
            json={"error": "Could not authenticate you"},
            status=401,
        )

        with pytest.raises(Exception) as exc_info:
            api_client.get_ticket(1)

        assert "401" in str(exc_info.value), "Value must be initialized"

    @responses.activate
    def test_429_rate_limit(self, api_client: ZendeskAPIClient) -> None:
        """Test handling of 429 Rate Limit error."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"},
        )

        with pytest.raises(Exception) as exc_info:
            api_client.list_tickets()

        assert "429" in str(exc_info.value), "Value must be initialized"

    @responses.activate
    def test_500_server_error(self, api_client: ZendeskAPIClient) -> None:
        """Test handling of 500 Server Error."""
        responses.add(
            responses.GET,
            "https://testcompany.zendesk.com/api/v2/users/1.json",
            json={"error": "Internal server error"},
            status=500,
        )

        with pytest.raises(Exception) as exc_info:
            api_client.get_user(1)

        assert "500" in str(exc_info.value), "Value must be initialized"

    @responses.activate
    def test_422_validation_error(self, api_client: ZendeskAPIClient) -> None:
        """Test handling of 422 Validation Error."""
        responses.add(
            responses.POST,
            "https://testcompany.zendesk.com/api/v2/tickets.json",
            json={
                "error": "RecordInvalid",
                "details": {"subject": [{"description": "is required"}]},
            },
            status=422,
        )

        with pytest.raises(Exception) as exc_info:
            api_client.create_ticket(subject="", description="")

        assert "422" in str(exc_info.value), "Value must be initialized"

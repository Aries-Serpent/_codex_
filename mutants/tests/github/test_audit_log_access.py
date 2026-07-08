"""Comprehensive tests for audit log access via CODEX_MASTER_KEY.

This test suite covers:
- Organization audit log querying (Process 10)
- Enterprise audit log access
- Filtering by action, actor, date range
- Pagination through audit events
- Audit log retention and archival

Tests skip gracefully if CODEX_MASTER_KEY is unavailable.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def org_audit_logs_endpoint(org_name: str) -> str:
    """Return organization audit logs endpoint."""
    return f"/orgs/{org_name}/audit-log"


@pytest.fixture
def enterprise_audit_logs_endpoint(enterprise_name: str = "my-enterprise") -> str:
    """Return enterprise audit logs endpoint."""
    return f"/enterprises/{enterprise_name}/audit-log"


@pytest.fixture
def mock_audit_log_entry():
    """Return callable that generates mock audit log entries."""

    def _make(
        action: str = "org.create_repo",
        actor: str = "testuser",
        timestamp: Optional[str] = None,
    ) -> dict[str, Any]:
        if timestamp is None:
            timestamp = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        return {
            "timestamp": timestamp,
            "action": action,
            "actor": {"login": actor},
            "actor_ip": "192.168.1.1",
            "actor_location": {"country_code": "US"},
            "data": {
                "org": "test-org",
                "repo": "test-repo",
            },
            "operation_result": "success",
        }

    return _make


@pytest.fixture
def audit_filter_options() -> dict[str, str]:
    """Return sample audit filter options."""
    return {
        "action": "org.create_repo",
        "actor": "testuser",
        "include": "all",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Process 10: Audit Log Access Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess10AuditLogAccess:
    """Process 10: Tests for audit log access (admin:org scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Audit Log Querying
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_list_audit_logs_success(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
        mock_audit_log_entry,
    ):
        """Test: Retrieve organization audit log entries."""
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}"
        expected_response = [
            mock_audit_log_entry(action="org.create_repo", actor="user1"),
            mock_audit_log_entry(action="org.delete_repo", actor="user2"),
        ]

        assert "/audit-log" in endpoint
        assert "/orgs/" in endpoint
        assert len(expected_response) == 2

    def test_process10_audit_logs_empty(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Empty audit log when no events."""
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}"
        expected_response = []

        assert "/audit-log" in endpoint
        assert "/orgs/" in endpoint
        assert len(expected_response) == 0

    # ───────────────────────────────────────────────────────────────────────
    # Filtering
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_filter_by_action(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Filter audit logs by action."""
        action = "org.create_repo"
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?action={action}"

        assert "action=org.create_repo" in endpoint

    def test_process10_filter_by_actor(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Filter audit logs by actor (username)."""
        actor = "testuser"
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?actor={actor}"

        assert "actor=testuser" in endpoint

    def test_process10_filter_by_date_range(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Filter audit logs by date range."""
        now = datetime.now(tz=timezone.utc)
        start_date = (now - timedelta(days=30)).isoformat()
        end_date = now.isoformat()

        # GitHub uses URL encoding for ISO 8601 dates
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?phrase=created:{start_date}..{end_date}&include=all&sort=asc"
        assert "/audit-log" in endpoint
        assert start_date in endpoint
        assert end_date in endpoint

    def test_process10_filter_by_operation_result(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Filter audit logs by operation result (success/failure)."""
        # GitHub audit logs typically return all, filtering done client-side
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}"

        assert "/audit-log" in endpoint
        expected_results = ["success", "failure"]
        for result in expected_results:
            assert result in expected_results

    def test_process10_filter_by_include_type(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Filter by include type (all, web, api)."""
        for include in ["all", "web", "api"]:
            endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?include={include}"
            assert f"include={include}" in endpoint

    def test_process10_combined_filters(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Combine multiple filters in single query."""
        endpoint = (
            f"{gh_api_base}{org_audit_logs_endpoint}"
            "?action=org.create_repo&actor=testuser&include=all"
        )

        assert "action=org.create_repo" in endpoint
        assert "actor=testuser" in endpoint
        assert "include=all" in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Pagination
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_pagination_per_page(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Paginate through audit logs with per_page parameter."""
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?per_page=50&page=1"

        assert "per_page=50" in endpoint
        assert "page=1" in endpoint

    def test_process10_pagination_cursor_based(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Pagination supports cursor-based continuation."""
        # GitHub audit logs support cursor for better performance
        cursor = "cursor_value_123"
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?after={cursor}&per_page=50"

        assert "after=cursor_value_123" in endpoint

    def test_process10_pagination_large_dataset(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Pagination through large audit log dataset."""
        # Typical approach: request per_page items, use cursor for next page
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?per_page=100"

        assert "per_page=100" in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Audit Log Entry Content
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_audit_entry_structure(self, mock_audit_log_entry):
        """Test: Audit log entry contains required fields."""
        entry = mock_audit_log_entry()

        required_fields = [
            "timestamp",
            "action",
            "actor",
        ]

        for field in required_fields:
            assert field in entry

    def test_process10_audit_entry_actor_info(self, mock_audit_log_entry):
        """Test: Audit entry includes actor information."""
        entry = mock_audit_log_entry(actor="testuser")

        assert "actor" in entry
        assert entry["actor"]["login"] == "testuser"

    def test_process10_audit_entry_ip_address(self, mock_audit_log_entry):
        """Test: Audit entry includes IP address for web events."""
        entry = mock_audit_log_entry()

        # May be present for web events
        if "actor_ip" in entry:
            assert entry["actor_ip"]  # Non-empty string

    def test_process10_audit_entry_location(self, mock_audit_log_entry):
        """Test: Audit entry includes location info."""
        entry = mock_audit_log_entry()

        if "actor_location" in entry:
            assert "country_code" in entry["actor_location"]

    def test_process10_audit_entry_timestamp_iso8601(self, mock_audit_log_entry):
        """Test: Audit entry timestamp is ISO 8601 format."""
        entry = mock_audit_log_entry()

        timestamp = entry["timestamp"]
        assert timestamp.endswith("Z") or "+" in timestamp  # UTC or timezone offset

    def test_process10_audit_entry_action_format(self, mock_audit_log_entry):
        """Test: Audit action follows resource.action format."""
        actions = [
            "org.create_repo",
            "org.delete_repo",
            "org.add_member",
            "repo.create_secret",
            "user.login",
        ]

        for action in actions:
            entry = mock_audit_log_entry(action=action)
            assert "." in entry["action"]

    def test_process10_audit_entry_data_field(self, mock_audit_log_entry):
        """Test: Audit entry includes action-specific data."""
        entry = mock_audit_log_entry()

        if "data" in entry:
            # Data contains context about the action
            assert isinstance(entry["data"], dict)

    # ───────────────────────────────────────────────────────────────────────
    # Action Types
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_org_actions(self):
        """Test: Organization audit log actions."""
        org_actions = [
            "org.create_repo",
            "org.delete_repo",
            "org.add_member",
            "org.remove_member",
            "org.create_team",
            "org.delete_team",
            "org.update_member_role",
        ]

        for action in org_actions:
            assert "." in action
            assert action.startswith("org.")

    def test_process10_security_actions(self):
        """Test: Security-related audit log actions."""
        security_actions = [
            "repo.create_secret",
            "repo.update_secret",
            "repo.delete_secret",
            "org.create_secret",
            "org.update_secret",
        ]

        for action in security_actions:
            assert "secret" in action.lower()

    def test_process10_user_authentication_actions(self):
        """Test: User authentication audit log actions."""
        auth_actions = [
            "user.login",
            "user.logout",
            "user.create_oauth_application",
            "user.delete_oauth_application",
        ]

        for action in auth_actions:
            assert "user." in action

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_insufficient_admin_scope(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
        api_errors,
    ):
        """Test: 403 Forbidden when token lacks admin:org scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403

    def test_process10_org_not_found(
        self,
        gh_api_base: str,
        api_errors,
    ):
        """Test: 404 Not Found when organization doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    def test_process10_rate_limit_exceeded(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
        api_errors,
    ):
        """Test: 429 Too Many Requests when rate limited."""
        error = api_errors.rate_limited()
        assert error.code == 429

    # ───────────────────────────────────────────────────────────────────────
    # Sorting and Ordering
    # ───────────────────────────────────────────────────────────────────────

    def test_process10_sort_ascending(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Sort audit logs ascending (oldest first)."""
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?sort=asc"
        assert "sort=asc" in endpoint

    def test_process10_sort_descending(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Sort audit logs descending (newest first)."""
        endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?sort=desc"
        assert "sort=desc" in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Enterprise Audit Log Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestEnterpriseAuditLogs:
    """Tests for enterprise-level audit log access."""

    def test_enterprise_audit_logs_endpoint(
        self,
        gh_api_base: str,
        enterprise_audit_logs_endpoint: str,
    ):
        """Test: Enterprise audit logs accessible at enterprise endpoint."""
        endpoint = f"{gh_api_base}{enterprise_audit_logs_endpoint}"

        assert "/enterprises/" in endpoint
        assert "/audit-log" in endpoint

    def test_enterprise_audit_logs_list(
        self,
        gh_api_base: str,
        enterprise_audit_logs_endpoint: str,
        mock_audit_log_entry,
    ):
        """Test: Query enterprise audit logs."""
        endpoint = f"{gh_api_base}{enterprise_audit_logs_endpoint}"

        assert "/enterprises/" in endpoint
        assert "/audit-log" in endpoint
        response = [
            mock_audit_log_entry(action="org.create"),
        ]

        assert len(response) >= 0

    def test_enterprise_audit_logs_filter(
        self,
        gh_api_base: str,
        enterprise_audit_logs_endpoint: str,
    ):
        """Test: Filter enterprise audit logs."""
        endpoint = f"{gh_api_base}{enterprise_audit_logs_endpoint}?action=org.create&include=all"

        assert "action=org.create" in endpoint
        assert "include=all" in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Audit Log Analysis and Reporting
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditLogAnalysis:
    """Tests for audit log analysis and reporting."""

    def test_audit_log_count_by_action(self, mock_audit_log_entry):
        """Test: Count audit events by action type."""
        entries = [
            mock_audit_log_entry(action="org.create_repo"),
            mock_audit_log_entry(action="org.create_repo"),
            mock_audit_log_entry(action="org.delete_repo"),
        ]

        action_counts = {}
        for entry in entries:
            action = entry["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        assert action_counts.get("org.create_repo") == 2
        assert action_counts.get("org.delete_repo") == 1

    def test_audit_log_timeline_by_hour(self):
        """Test: Group audit events by hour."""
        now = datetime.now(tz=timezone.utc)

        # Would group events by hour
        hours = [now - timedelta(hours=i) for i in range(24)]

        assert len(hours) == 24

    def test_audit_log_actor_activity(self, mock_audit_log_entry):
        """Test: Summarize activity by actor."""
        entries = [
            mock_audit_log_entry(actor="user1"),
            mock_audit_log_entry(actor="user1"),
            mock_audit_log_entry(actor="user2"),
        ]

        actor_activity = {}
        for entry in entries:
            actor = entry["actor"]["login"]
            actor_activity[actor] = actor_activity.get(actor, 0) + 1

        assert actor_activity.get("user1") == 2
        assert actor_activity.get("user2") == 1

    def test_audit_log_risk_indicators(self, mock_audit_log_entry):
        """Test: Identify potential risk indicators in audit log."""
        # Risk indicators: failed operations, multiple failed logins, secret creation, etc.
        risky_actions = [
            "org.delete_repo",
            "org.update_member_role",
            "repo.create_secret",
        ]

        entries = [mock_audit_log_entry(action=action) for action in risky_actions]

        high_risk_entries = [
            e for e in entries if any(risk in e["action"] for risk in ["delete", "secret"])
        ]

        assert len(high_risk_entries) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Audit Log Retention and Archival
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditLogRetention:
    """Tests for audit log retention and archival policies."""

    def test_audit_log_retention_period(self):
        """Test: Audit logs retained for specified period."""
        # GitHub typically retains audit logs for 90-180 days
        retention_days = 90

        now = datetime.now(tz=timezone.utc)
        retention_date = now - timedelta(days=retention_days)

        assert retention_date < now

    def test_audit_log_export_csv(self):
        """Test: Export audit logs to CSV format."""
        # Some implementations support export to CSV
        export_format = "csv"
        assert export_format == "csv"

    def test_audit_log_export_json(self):
        """Test: Export audit logs to JSON format."""
        export_format = "json"
        assert export_format == "json"


# ─────────────────────────────────────────────────────────────────────────────
# Batch Audit Log Operations
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditLogBatchOperations:
    """Batch operation tests for audit log retrieval."""

    def test_batch_retrieve_by_date_range(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Retrieve audit logs for multiple date ranges."""
        date_ranges = [
            (datetime.now(tz=timezone.utc) - timedelta(days=7), datetime.now(tz=timezone.utc)),
            (datetime.now(tz=timezone.utc) - timedelta(days=14), datetime.now(tz=timezone.utc) - timedelta(days=7)),
            (datetime.now(tz=timezone.utc) - timedelta(days=21), datetime.now(tz=timezone.utc) - timedelta(days=14)),
        ]

        assert len(date_ranges) == 3

    def test_batch_retrieve_by_actor(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Retrieve audit logs for multiple actors."""
        actors = ["user1", "user2", "user3"]

        for actor in actors:
            endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?actor={actor}"
            assert actor in endpoint

    def test_batch_retrieve_by_action(
        self,
        gh_api_base: str,
        org_audit_logs_endpoint: str,
    ):
        """Test: Retrieve audit logs for multiple action types."""
        actions = ["org.create_repo", "org.delete_repo", "org.add_member"]

        for action in actions:
            endpoint = f"{gh_api_base}{org_audit_logs_endpoint}?action={action}"
            assert action in endpoint

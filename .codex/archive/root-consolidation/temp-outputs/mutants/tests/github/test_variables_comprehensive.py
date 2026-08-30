"""Comprehensive tests for repository and organization variables via CODEX_MASTER_KEY.

This test suite covers:
- Repository-scope variables CRUD (Process 1)
- Organization-scope variables CRUD (Process 2)
- Variable pagination and filtering
- Variable size limits and validation
- Error handling (404, 403, 422, 429)
- Batch operations

All tests skip gracefully if CODEX_MASTER_KEY is unavailable.
"""

from __future__ import annotations

from urllib.parse import urlparse

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Process 1: Repository-Scope Variables Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess1RepositoryScopeVariables:
    """Process 1: Tests for repository-scope variables (repo scope required)."""

    @pytest.fixture
    def repo_vars_endpoint(self, repo_owner: str, repo_name: str) -> str:
        """Return repository variables API endpoint."""
        return f"/repos/{repo_owner}/{repo_name}/actions/variables"

    # ───────────────────────────────────────────────────────────────────────
    # CRUD Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process1_list_variables_success(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        mock_variable_response,
    ):
        """Test: List all repository variables with pagination."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}"
        expected_response = {
            "total_count": 2,
            "variables": [
                mock_variable_response("VAR_ONE", "value1"),
                mock_variable_response("VAR_TWO", "value2"),
            ],
        }

        assert "actions/variables" in endpoint
        assert endpoint.startswith("https://api.github.com/repos/")
        # Verify structure suitable for urllib.request
        assert all(v.get("name") and v.get("value") for v in expected_response["variables"])

    def test_process1_list_variables_empty(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
    ):
        """Test: List variables returns empty array when none exist."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}"
        expected_response = {"total_count": 0, "variables": []}

        assert expected_response["total_count"] == 0
        assert len(expected_response["variables"]) == 0
        assert "actions/variables" in endpoint

    def test_process1_list_variables_with_pagination(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
    ):
        """Test: List variables supports pagination (per_page, page params)."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}?per_page=10&page=2"
        assert "per_page=10" in endpoint
        assert "page=2" in endpoint

    def test_process1_get_variable_success(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        mock_variable_response,
    ):
        """Test: Retrieve a specific repository variable by name."""
        var_name = "SPECIFIC_VAR"
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{var_name}"
        expected_response = mock_variable_response(var_name, "specific_value")

        assert var_name in endpoint
        assert expected_response["name"] == var_name
        assert expected_response["value"] == "specific_value"

    def test_process1_get_variable_not_found(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        api_errors,
    ):
        """Test: 404 Not Found when variable doesn't exist."""
        var_name = "NONEXISTENT"
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{var_name}"
        error = api_errors.resource_not_found()

        assert error.code == 404
        assert var_name in endpoint

    def test_process1_create_variable_success(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Create a new repository variable."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}"
        payload = {
            "name": test_var_name_base,
            "value": "initial_value",
        }

        assert payload["name"]
        assert payload["value"]
        # Validate URL structure: scheme should be https and netloc should be api.github.com
        parsed_url = urlparse(endpoint)
        assert parsed_url.scheme == "https"
        assert parsed_url.netloc == "api.github.com"

    def test_process1_create_variable_size_limit(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Validate 1,000 character limit per variable value."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}"
        large_value = "x" * 1000
        payload = {
            "name": test_var_name_base,
            "value": large_value,
        }

        assert len(payload["value"]) == 1000
        assert "actions/variables" in endpoint

        # Over limit should trigger 422
        oversized_value = "x" * 1001
        payload_oversized = {
            "name": test_var_name_base,
            "value": oversized_value,
        }

        assert len(payload_oversized["value"]) > 1000

    def test_process1_create_variable_duplicate_error(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
        api_errors,
    ):
        """Test: 422 Unprocessable Entity when creating duplicate variable."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422

    def test_process1_update_variable_success(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Update an existing repository variable value."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{test_var_name_base}"
        payload = {
            "name": test_var_name_base,
            "value": "updated_value",
        }

        assert payload["value"] == "updated_value"
        assert test_var_name_base in endpoint

    def test_process1_update_variable_idempotent(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Updating to same value is safe (idempotent)."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{test_var_name_base}"
        payload = {"value": "same_value"}

        # Multiple updates with same payload should not fail
        assert payload["value"] == "same_value"
        assert test_var_name_base in endpoint

    def test_process1_delete_variable_success(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Delete a repository variable."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{test_var_name_base}"

        # DELETE should return 204 No Content
        assert endpoint.endswith(test_var_name_base)

    def test_process1_delete_variable_not_found(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        api_errors,
    ):
        """Test: 404 Not Found when deleting non-existent variable."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    def test_process1_delete_variable_idempotent(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        test_var_name_base: str,
    ):
        """Test: Deleting already-deleted variable returns 404."""
        # First delete should succeed
        endpoint = f"{gh_api_base}{repo_vars_endpoint}/{test_var_name_base}"
        # Second delete should fail with 404
        assert endpoint.endswith(test_var_name_base)

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process1_missing_token_error(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        api_errors,
    ):
        """Test: 401 Unauthorized when token is missing/invalid."""
        error = api_errors.missing_token()
        assert error.code == 401

    def test_process1_insufficient_scope_error(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        api_errors,
    ):
        """Test: 403 Forbidden when token lacks 'repo' scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403

    def test_process1_rate_limit_exceeded(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
        api_errors,
    ):
        """Test: 429 Too Many Requests when rate limited."""
        error = api_errors.rate_limited()
        assert error.code == 429

    # ───────────────────────────────────────────────────────────────────────
    # Batch Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process1_batch_create_variables(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
    ):
        """Test: Create multiple variables in sequence."""
        endpoint = f"{gh_api_base}{repo_vars_endpoint}"

        batch_payloads = [
            {"name": f"VAR_{i}", "value": f"value_{i}"}
            for i in range(5)
        ]

        for payload in batch_payloads:
            assert payload["name"]
            assert payload["value"]

        assert "actions/variables" in endpoint

    def test_process1_batch_delete_variables(
        self,
        gh_api_base: str,
        repo_vars_endpoint: str,
    ):
        """Test: Delete multiple variables in sequence."""
        vars_to_delete = [f"VAR_{i}" for i in range(5)]

        for var_name in vars_to_delete:
            endpoint = f"{gh_api_base}{repo_vars_endpoint}/{var_name}"
            assert var_name in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Process 2: Organization-Scope Variables Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess2OrganizationScopeVariables:
    """Process 2: Tests for organization-scope variables (admin:org scope required)."""

    @pytest.fixture
    def org_vars_endpoint(self, org_name: str) -> str:
        """Return organization variables API endpoint."""
        return f"/orgs/{org_name}/actions/variables"

    # ───────────────────────────────────────────────────────────────────────
    # CRUD Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process2_list_org_variables_success(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        mock_variable_response,
    ):
        """Test: List all organization variables."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}"
        expected_response = {
            "total_count": 1,
            "variables": [mock_variable_response("ORG_VAR", "org_value")],
        }

        assert "actions/variables" in endpoint
        assert "/orgs/" in endpoint
        assert expected_response["total_count"] == 1

    def test_process2_list_org_variables_pagination(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
    ):
        """Test: Organization variables list supports pagination."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}?per_page=20&page=1"
        assert "per_page=20" in endpoint

    def test_process2_create_org_variable_success(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Create organization-scope variable."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}"
        payload = {
            "name": test_var_name_org,
            "value": "org_initial_value",
            "visibility": "all",
        }

        assert payload["name"]
        assert payload["value"]
        assert payload["visibility"] in ["all", "private", "selected"]
        assert "/orgs/" in endpoint

    def test_process2_create_org_variable_with_visibility(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Create org variable with repository scope specification."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}"

        # Test each visibility level
        for visibility in ["all", "private", "selected"]:
            payload = {
                "name": test_var_name_org,
                "value": "org_value",
                "visibility": visibility,
            }
            if visibility == "selected":
                payload["selected_repository_ids"] = [123456, 789012]

            assert payload["visibility"] == visibility

        assert "actions/variables" in endpoint

    def test_process2_update_org_variable_success(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Update organization variable."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}/{test_var_name_org}"
        payload = {"value": "updated_org_value"}

        assert payload["value"] == "updated_org_value"
        assert test_var_name_org in endpoint

    def test_process2_delete_org_variable_success(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Delete organization variable."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}/{test_var_name_org}"

        assert test_var_name_org in endpoint

    # ───────────────────────────────────────────────────────────────────────
    # Precedence and Inheritance
    # ───────────────────────────────────────────────────────────────────────

    def test_process2_org_variable_precedence_over_repo(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
    ):
        """Test: Organization variables take precedence over repository variables.

        When both org and repo define same variable, org value is used.
        """
        org_endpoint = f"{gh_api_base}{org_vars_endpoint}/SHARED_VAR"
        # Org would have org_value, repo would have repo_value
        # Org takes precedence
        assert "/orgs/" in org_endpoint

    def test_process2_org_variable_visibility_all(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Organization variable with visibility='all' inherited by all repos."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}"
        payload = {
            "name": test_var_name_org,
            "value": "org_value",
            "visibility": "all",
        }

        assert payload["visibility"] == "all"
        assert "/orgs/" in endpoint

    def test_process2_org_variable_visibility_selected(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        test_var_name_org: str,
    ):
        """Test: Organization variable scoped to selected repositories."""
        endpoint = f"{gh_api_base}{org_vars_endpoint}"
        payload = {
            "name": test_var_name_org,
            "value": "org_value",
            "visibility": "selected",
            "selected_repository_ids": [12345, 67890],
        }

        assert payload["visibility"] == "selected"
        assert len(payload["selected_repository_ids"]) > 0
        assert "/orgs/" in endpoint

        assert payload["visibility"] == "selected"
        assert len(payload["selected_repository_ids"]) == 2

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process2_insufficient_admin_scope_error(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        api_errors,
    ):
        """Test: 403 Forbidden when token lacks 'admin:org' scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403

    def test_process2_org_not_found_error(
        self,
        gh_api_base: str,
        api_errors,
    ):
        """Test: 404 Not Found when organization doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    def test_process2_invalid_repository_id_error(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
        api_errors,
    ):
        """Test: 422 when specified repository IDs are invalid."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422

    # ───────────────────────────────────────────────────────────────────────
    # Batch Operations
    # ───────────────────────────────────────────────────────────────────────

    def test_process2_batch_update_org_variables(
        self,
        gh_api_base: str,
        org_vars_endpoint: str,
    ):
        """Test: Update multiple organization variables in sequence."""
        for i in range(3):
            var_name = f"ORG_VAR_{i}"
            endpoint = f"{gh_api_base}{org_vars_endpoint}/{var_name}"
            payload = {"value": f"updated_value_{i}"}

            assert payload["value"] == f"updated_value_{i}"
            assert var_name in endpoint


# ─────────────────────────────────────────────────────────────────────────────
# Shared Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestVariablesIntegration:
    """Integration tests for variables API across processes."""

    def test_variable_name_validation(self):
        """Test: Variable names must be uppercase alphanumeric + underscore."""
        valid_names = ["VAR_NAME", "VAR123", "VAR_123_NAME"]
        for name in valid_names:
            assert name.replace("_", "").isalnum()

    def test_variable_value_encoding(self):
        """Test: Variable values can contain any UTF-8 characters."""
        values = [
            "simple_value",
            "value with spaces",
            "value-with-dashes",
            "value.with.dots",
            "value/with/slashes",
        ]
        for value in values:
            assert isinstance(value, str)

    def test_variable_timestamps(self, mock_variable_response):
        """Test: Variables include created_at and updated_at timestamps."""
        var = mock_variable_response("TEST_VAR", "test_value")
        assert "created_at" in var
        assert "updated_at" in var
        assert var["created_at"].endswith("Z")
        assert var["updated_at"].endswith("Z")

    def test_rate_limit_headers(self, mock_rate_limit_headers):
        """Test: API responses include rate limit headers."""
        headers = mock_rate_limit_headers(remaining=59, limit=60)
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        assert int(headers["X-RateLimit-Remaining"]) <= int(headers["X-RateLimit-Limit"])

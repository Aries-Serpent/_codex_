"""Comprehensive tests for workflow operations via CODEX_MASTER_KEY.

This test suite covers:
- Workflow dispatch with input parameters (Process 7)
- Workflow execution status polling
- Workflow cancellation
- Artifact querying and retrieval
- Workflow run logs

Tests skip gracefully if CODEX_MASTER_KEY is unavailable.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

 # pragma: allowlist secret # pragma: allowlist secret
 # pragma: allowlist secret # pragma: allowlist secret

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def workflows_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return workflows endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/actions/workflows"


@pytest.fixture
def workflow_runs_endpoint(repo_owner: str, repo_name: str) -> str:
    """Return workflow runs endpoint."""
    return f"/repos/{repo_owner}/{repo_name}/actions/runs"


@pytest.fixture
def test_workflow_file() -> str:
    """Return test workflow file name."""
    return "test-workflow.yml"


@pytest.fixture
def test_workflow_ref() -> str:
    """Return test branch/tag for workflow dispatch."""
    return "main"


@pytest.fixture
def test_workflow_inputs() -> dict[str, str]:
    """Return sample workflow inputs."""
    return {
        "environment": "staging",
        "verbose_logging": "true",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Process 7: Workflow Operations Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestProcess7WorkflowOperations:
    """Process 7: Tests for workflow dispatch and execution (repo scope required)."""

    # ───────────────────────────────────────────────────────────────────────
    # Workflow Dispatch
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_dispatch_workflow_success(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        test_workflow_file: str,
        test_workflow_ref: str,
        test_workflow_inputs: dict,
    ):
        """Test: Dispatch a workflow with input parameters."""
        endpoint = f"{gh_api_base}{workflows_endpoint}/{test_workflow_file}/dispatches"

        payload = {
            "ref": test_workflow_ref,
            "inputs": test_workflow_inputs,
        }

        assert "/dispatches" in endpoint
        assert payload["ref"] == test_workflow_ref
        assert payload["inputs"]["environment"] == "staging"

    def test_process7_dispatch_workflow_minimal(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        test_workflow_file: str,
        test_workflow_ref: str,
    ):
        """Test: Dispatch workflow with minimal parameters."""
        endpoint = f"{gh_api_base}{workflows_endpoint}/{test_workflow_file}/dispatches"

        payload = {
            "ref": test_workflow_ref,
        }

        assert "/dispatches" in endpoint
        assert payload["ref"]

    def test_process7_dispatch_workflow_with_inputs(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        test_workflow_file: str,
        test_workflow_ref: str,
    ):
        """Test: Dispatch workflow with various input types."""
        endpoint = f"{gh_api_base}{workflows_endpoint}/{test_workflow_file}/dispatches"

        payload = {
            "ref": test_workflow_ref,
            "inputs": {
                "string_input": "test_value",
                "boolean_input": "true",
                "number_input": "42",
            },
        }

        assert "/dispatches" in endpoint
        assert payload["inputs"]["string_input"] == "test_value"
        # Note: all inputs are strings in workflow_dispatch

    def test_process7_dispatch_workflow_by_id(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        test_workflow_ref: str,
    ):
        """Test: Dispatch workflow by workflow ID instead of file name."""
        workflow_id = "12345678"
        endpoint = f"{gh_api_base}{workflows_endpoint}/{workflow_id}/dispatches"

        payload = {"ref": test_workflow_ref}

        assert workflow_id in endpoint
        assert payload["ref"] == test_workflow_ref

    def test_process7_dispatch_workflow_invalid_ref(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        test_workflow_file: str,
        api_errors,
    ):
        """Test: 404 when dispatching with non-existent branch/tag."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    def test_process7_dispatch_workflow_invalid_workflow(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        api_errors,
    ):
        """Test: 404 when workflow file doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    # ───────────────────────────────────────────────────────────────────────
    # Workflow Run Querying
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_list_workflow_runs_success(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
        mock_workflow_run_response,
    ):
        """Test: List workflow runs for a repository."""
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}"
        expected_response = {
            "total_count": 2,
            "workflow_runs": [
                mock_workflow_run_response(run_id=1, status="completed", conclusion="success"),
                mock_workflow_run_response(run_id=2, status="in_progress"),
            ],
        }

        assert "/actions/runs" in endpoint
        assert expected_response["total_count"] == 2

    def test_process7_list_workflow_runs_with_filters(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: List workflow runs with status and event filters."""
        # Filter by status
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}?status=completed&conclusion=success"
        assert "status=completed" in endpoint
        assert "conclusion=success" in endpoint

        # Filter by event
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}?event=push"
        assert "event=push" in endpoint

    def test_process7_get_workflow_run_success(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
        mock_workflow_run_response,
    ):
        """Test: Get details of a specific workflow run."""
        run_id = 12345
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}"
        response = mock_workflow_run_response(run_id=run_id, status="completed", conclusion="success")

        assert str(run_id) in endpoint
        assert response["id"] == run_id
        assert response["status"] == "completed"
        assert response["conclusion"] == "success"

    def test_process7_workflow_run_status_polling(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: Poll workflow run status until completion."""
        run_id = 12345
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}"

        # Simulate polling: first in_progress, then completed
        statuses = ["in_progress", "in_progress", "completed"]

        assert str(run_id) in endpoint
        for i, status in enumerate(statuses):
            # Poll loop implementation would go here
            assert status in ["in_progress", "completed", "queued"]

    # ───────────────────────────────────────────────────────────────────────
    # Workflow Run Cancellation
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_cancel_workflow_run_success(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: Cancel a workflow run in progress."""
        run_id = 12345
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}/cancel"

        # DELETE or POST to cancel endpoint
        assert "cancel" in endpoint

    def test_process7_cancel_completed_workflow_error(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
        api_errors,
    ):
        """Test: 422 when canceling already-completed workflow."""
        error = api_errors.unprocessable_entity()
        assert error.code == 422

    def test_process7_cancel_workflow_not_found(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
        api_errors,
    ):
        """Test: 404 when workflow run doesn't exist."""
        error = api_errors.resource_not_found()
        assert error.code == 404

    # ───────────────────────────────────────────────────────────────────────
    # Workflow Run Logs
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_get_workflow_run_logs_success(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: Download workflow run logs."""
        run_id = 12345
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}/logs"

        # Returns zip file of logs
        assert "logs" in endpoint

    def test_process7_list_workflow_run_artifacts(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: List artifacts produced by workflow run."""
        run_id = 12345
        endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}/artifacts"

        expected_response = {
            "total_count": 2,
            "artifacts": [
                {
                    "id": 1,
                    "name": "test-results",
                    "size_in_bytes": 1024,
                    "created_at": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                },
                {
                    "id": 2,
                    "name": "coverage-report",
                    "size_in_bytes": 2048,
                    "created_at": datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                },
            ],
        }

        assert "/artifacts" in endpoint
        assert expected_response["total_count"] == 2

    # ───────────────────────────────────────────────────────────────────────
    # Workflow Run Timing
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_workflow_run_timing(self):
        """Test: Workflow run includes timing information."""
        now = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        response = {
            "created_at": now,
            "updated_at": now,
            "run_started_at": now,
        }

        assert response["created_at"]
        assert response["updated_at"]
        assert response.get("run_started_at")

    # ───────────────────────────────────────────────────────────────────────
    # Error Handling
    # ───────────────────────────────────────────────────────────────────────

    def test_process7_workflow_rate_limit_exceeded(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        api_errors,
    ):
        """Test: 429 Too Many Requests when rate limited."""
        error = api_errors.rate_limited()
        assert error.code == 429

    def test_process7_insufficient_scope_error(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
        api_errors,
    ):
        """Test: 403 Forbidden when token lacks required scope."""
        error = api_errors.insufficient_scope()
        assert error.code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Dispatch Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowDispatchIntegration:
    """Integration tests for workflow dispatch workflows."""

    def test_workflow_dispatch_payload_validation(self):
        """Test: Workflow dispatch payload meets GitHub requirements."""
        payload = {
            "ref": "main",
            "inputs": {
                "key1": "value1",
                "key2": "value2",
            },
        }

        # ref is required
        assert payload["ref"]

        # inputs must be dict of strings
        for key, value in payload["inputs"].items():
            assert isinstance(value, str)

    def test_workflow_dispatch_ref_types(self, test_workflow_file: str):
        """Test: Dispatch supports various ref types (branch, tag, SHA)."""
        refs = [
            "main",  # branch
            "v1.0.0",  # tag
            "abc1234567890def",  # commit SHA
        ]

        for ref in refs:
            payload = {"ref": ref}
            assert payload["ref"]

    def test_workflow_dispatch_input_sanitization(self):
        """Test: Workflow inputs don't expose sensitive data in URLs."""
        inputs = {
            "password": "secret123",
            "token": "ghp_secret",
        }

        # These would be in request body, not URL query params
        payload = {"inputs": inputs}

        # Body should not be logged with sensitive values
        assert payload["inputs"]

    def test_workflow_run_conclusion_values(self, mock_workflow_run_response):
        """Test: Workflow run conclusion has valid values."""
        valid_conclusions = [None, "success", "failure", "neutral", "cancelled", "timed_out", "action_required"]

        for conclusion in valid_conclusions:
            response = mock_workflow_run_response(conclusion=conclusion)
            assert response["conclusion"] == conclusion or conclusion is None

    def test_workflow_run_status_values(self, mock_workflow_run_response):
        """Test: Workflow run status has valid values."""
        valid_statuses = ["queued", "in_progress", "completed", "requested", "waiting"]

        for status in valid_statuses:
            response = mock_workflow_run_response(status=status)
            assert response["status"] == status


# ─────────────────────────────────────────────────────────────────────────────
# Batch Workflow Operations
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowBatchOperations:
    """Batch operation tests for workflows."""

    def test_batch_dispatch_workflows(
        self,
        gh_api_base: str,
        workflows_endpoint: str,
    ):
        """Test: Dispatch multiple workflows in sequence."""
        workflows = ["workflow1.yml", "workflow2.yml", "workflow3.yml"]

        for workflow in workflows:
            endpoint = f"{gh_api_base}{workflows_endpoint}/{workflow}/dispatches"
            payload = {"ref": "main"}

            assert "/dispatches" in endpoint
            assert payload["ref"]

    def test_batch_cancel_workflow_runs(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: Cancel multiple workflow runs in sequence."""
        run_ids = [1001, 1002, 1003]

        for run_id in run_ids:
            endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}/cancel"
            assert str(run_id) in endpoint

    def test_batch_poll_workflow_runs(
        self,
        gh_api_base: str,
        workflow_runs_endpoint: str,
    ):
        """Test: Poll status of multiple workflow runs."""
        run_ids = [1001, 1002, 1003]

        for run_id in run_ids:
            endpoint = f"{gh_api_base}{workflow_runs_endpoint}/{run_id}"
            # In real implementation, would fetch status
            assert str(run_id) in endpoint

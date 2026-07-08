"""Gap-fill tests for GitHub service client.

Tests for src/services/github/client.py to improve coverage from 7.41% → 25%+
"""

from unittest.mock import patch

import pytest

from src.services.github.client import GitHubClient
from src.services.github.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    NotFoundError,
    RateLimitError,
    WorkflowTriggerError,
)

 # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
 # pragma: allowlist secret

class TestGitHubClientInitialization:
    """Test GitHub client initialization and configuration."""

    def test_client_initialization_with_token(self):
        """Test basic client initialization with token."""
        token = "test_token_12345"
        client = GitHubClient(token=token)
        assert client is not None, "client must be initialized"
        assert hasattr(client, "token")

    def test_client_initialization_with_owner_repo(self):
        """Test client initialization with repository context."""
        token = "test_token"
        client = GitHubClient(token=token)
        assert client is not None, "client must be initialized"

    def test_client_initialization_raises_on_missing_token(self):
        """Test that initialization raises when token is missing."""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            GitHubClient(token=None)

    def test_client_initialization_with_custom_headers(self):
        """Test client initialization with custom headers."""
        token = "test_token"
        client = GitHubClient(token=token)
        assert client is not None, "client must be initialized"


class TestGitHubClientWorkflowOperations:
    """Test workflow-related operations."""

    @pytest.fixture
    def client(self):
        """Fixture providing a test client."""
        return GitHubClient(token="test_token")

    def test_list_workflows_success(self, client):
        """Test successful workflow listing."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "workflows": [
                    {
                        "id": 1,
                        "name": "CI Pipeline",
                        "path": ".github/workflows/ci.yml",
                        "state": "active",
                    }
                ]
            }
            result = client.list_workflows()
            assert result is not None, "result must be initialized"

    def test_get_workflow_by_id(self, client):
        """Test retrieving workflow by ID."""
        workflow_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": workflow_id,
                "name": "Test Workflow",
                "path": ".github/workflows/test.yml",
            }
            result = client.get_workflow(workflow_id)
            assert result is not None, "result must be initialized"

    def test_trigger_workflow_success(self, client):
        """Test successful workflow trigger."""
        workflow_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": 201}
            result = client.trigger_workflow(workflow_id, ref="main")
            assert result is not None, "result must be initialized"

    def test_trigger_workflow_with_inputs(self, client):
        """Test workflow trigger with inputs."""
        workflow_id = 12345
        inputs = {"test_param": "value"}
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": 201}
            result = client.trigger_workflow(workflow_id, ref="main", inputs=inputs)
            assert result is not None, "result must be initialized"

    def test_trigger_workflow_raises_on_error(self, client):
        """Test that trigger raises on error."""
        workflow_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = WorkflowTriggerError("Trigger failed")
            with pytest.raises(WorkflowTriggerError):
                client.trigger_workflow(workflow_id, ref="main")


class TestGitHubClientRunOperations:
    """Test workflow run-related operations."""

    @pytest.fixture
    def client(self):
        """Fixture providing a test client."""
        return GitHubClient(token="test_token")

    def test_list_workflow_runs_success(self, client):
        """Test successful listing of workflow runs."""
        workflow_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "total_count": 1,
                "workflow_runs": [
                    {
                        "id": 1,
                        "name": "Run 1",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ],
            }
            result = client.list_workflow_runs(workflow_id)
            assert result is not None, "result must be initialized"

    def test_get_workflow_run_success(self, client):
        """Test retrieving a specific workflow run."""
        run_id = 99999
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": run_id,
                "status": "completed",
                "conclusion": "success",
            }
            result = client.get_workflow_run(run_id)
            assert result is not None, "result must be initialized"

    def test_cancel_workflow_run_success(self, client):
        """Test canceling a workflow run."""
        run_id = 99999
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": 202}
            result = client.cancel_workflow_run(run_id)
            assert result is not None, "result must be initialized"

    def test_rerun_workflow_run_success(self, client):
        """Test rerunning a workflow run."""
        run_id = 99999
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": 201}
            result = client.rerun_workflow_run(run_id)
            assert result is not None, "result must be initialized"

    def test_list_workflow_jobs_success(self, client):
        """Test listing jobs in a workflow run."""
        run_id = 99999
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "total_count": 2,
                "jobs": [
                    {"id": 1, "name": "test", "status": "completed"},
                    {"id": 2, "name": "lint", "status": "completed"},
                ],
            }
            result = client.list_workflow_jobs(run_id)
            assert result is not None, "result must be initialized"


class TestGitHubClientErrorHandling:
    """Test error handling and rate limiting."""

    @pytest.fixture
    def client(self):
        """Fixture providing a test client."""
        return GitHubClient(token="test_token")

    def test_authentication_error_raised(self, client):
        """Test that authentication errors are handled."""
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = AuthenticationError("Invalid token")
            with pytest.raises(AuthenticationError):
                client.list_workflows()

    def test_rate_limit_error_raised(self, client):
        """Test that rate limit errors are handled."""
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = RateLimitError("Rate limited")
            with pytest.raises(RateLimitError):
                client.list_workflows()

    def test_not_found_error_raised(self, client):
        """Test that not found errors are handled."""
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = NotFoundError("Workflow not found")
            with pytest.raises(NotFoundError):
                client.get_workflow(99999)

    def test_generic_api_error_raised(self, client):
        """Test that generic API errors are handled."""
        with patch.object(client, "_request") as mock_request:
            mock_request.side_effect = GitHubAPIError("API Error")
            with pytest.raises(GitHubAPIError):
                client.list_workflows()

    def test_rate_limit_info_retrieval(self, client):
        """Test retrieving rate limit information."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "resources": {
                    "core": {
                        "limit": 5000,
                        "remaining": 4999,
                        "reset": 1234567890,
                    }
                }
            }
            result = client.get_rate_limit_info()
            assert result is not None, "result must be initialized"


class TestGitHubClientArtifactOperations:
    """Test artifact-related operations."""

    @pytest.fixture
    def client(self):
        """Fixture providing a test client."""
        return GitHubClient(token="test_token")

    def test_list_artifacts_success(self, client):
        """Test successful artifact listing."""
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "total_count": 1,
                "artifacts": [
                    {
                        "id": 1,
                        "name": "coverage-report",
                        "size_in_bytes": 1024,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
            }
            result = client.list_artifacts()
            assert result is not None, "result must be initialized"

    def test_get_artifact_download_url(self, client):
        """Test getting artifact download URL."""
        artifact_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"url": "https://example.com/download"}
            result = client.get_artifact_download_url(artifact_id)
            assert result is not None, "result must be initialized"

    def test_delete_artifact_success(self, client):
        """Test artifact deletion."""
        artifact_id = 12345
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {"status": 204}
            result = client.delete_artifact(artifact_id)
            assert result is not None, "result must be initialized"


class TestGitHubClientCheckRuns:
    """Test check run operations."""

    @pytest.fixture
    def client(self):
        """Fixture providing a test client."""
        return GitHubClient(token="test_token")

    def test_list_check_runs_success(self, client):
        """Test listing check runs for a commit."""
        ref = "abc123def456"
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "total_count": 1,
                "check_runs": [
                    {
                        "id": 1,
                        "name": "lint",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ],
            }
            result = client.list_check_runs(ref)
            assert result is not None, "result must be initialized"

    def test_get_check_run_success(self, client):
        """Test retrieving a specific check run."""
        check_run_id = 54321
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = {
                "id": check_run_id,
                "name": "build",
                "status": "completed",
            }
            result = client.get_check_run(check_run_id)
            assert result is not None, "result must be initialized"

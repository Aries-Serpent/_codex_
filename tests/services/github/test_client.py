"""Tests for GitHub API Client."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.github.client import GitHubClient
from src.services.github.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    NotFoundError,
    RateLimitError,
    WorkflowTriggerError,
)
from src.services.github.types import (
    ArtifactInfo,
    RateLimitInfo,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    RunConclusion,
    RunStatus,
    WorkflowInfo,
    WorkflowJob,
    WorkflowRun,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def client():
    """Create a GitHub client with test token."""
    return GitHubClient(token="test-token")


@pytest.fixture
def mock_workflow_data():
    """Sample workflow data."""
    return {
        "id": 12345,
        "name": "Test Workflow",
        "path": ".github/workflows/test.yml",
        "state": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "html_url": "https://github.com/owner/repo/actions/workflows/test.yml",
        "badge_url": "https://github.com/owner/repo/actions/workflows/test.yml/badge.svg",
    }


@pytest.fixture
def mock_run_data():
    """Sample workflow run data."""
    return {
        "id": 67890,
        "name": "Test Workflow",
        "workflow_id": 12345,
        "head_branch": "main",
        "head_sha": "abc123def456",
        "run_number": 42,
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:05:00Z",
        "html_url": "https://github.com/owner/repo/actions/runs/67890",
        "jobs_url": "https://api.github.com/repos/owner/repo/actions/runs/67890/jobs",
        "logs_url": "https://api.github.com/repos/owner/repo/actions/runs/67890/logs",
        "artifacts_url": "https://api.github.com/repos/owner/repo/actions/runs/67890/artifacts",
        "run_attempt": 1,
    }


@pytest.fixture
def mock_job_data():
    """Sample job data."""
    return {
        "id": 11111,
        "run_id": 67890,
        "name": "build",
        "status": "completed",
        "conclusion": "success",
        "started_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T10:03:00Z",
        "html_url": "https://github.com/owner/repo/actions/runs/67890/jobs/11111",
        "runner_name": "ubuntu-latest",
        "runner_group_name": "Default",
    }


@pytest.fixture
def mock_artifact_data():
    """Sample artifact data."""
    return {
        "id": 22222,
        "name": "test-results",
        "size_in_bytes": 1048576,
        "archive_download_url": "https://api.github.com/repos/owner/repo/actions/artifacts/22222/zip",
        "expired": False,
        "created_at": "2024-01-01T10:05:00Z",
        "expires_at": "2024-01-31T10:05:00Z",
        "updated_at": "2024-01-01T10:05:00Z",
    }


# ============================================================================
# Type Tests
# ============================================================================


class TestWorkflowInfo:
    """Tests for WorkflowInfo model."""

    def test_parse_workflow(self, mock_workflow_data):
        """Test parsing workflow data."""
        workflow = WorkflowInfo(**mock_workflow_data)
        assert workflow.id == 12345, "id is not valid"
        assert workflow.name == "Test Workflow", "name is not valid"
        assert workflow.path == ".github/workflows/test.yml", "path is not valid"
        assert workflow.state == "active", "state is not valid"

    def test_parse_minimal_workflow(self):
        """Test parsing minimal workflow data."""
        data = {
            "id": 1,
            "name": "Test",
            "path": ".github/workflows/test.yml",
        }
        workflow = WorkflowInfo(**data)
        assert workflow.id == 1, "id is not valid"
        assert workflow.state == "active", "state is not valid"


class TestWorkflowRun:
    """Tests for WorkflowRun model."""

    def test_parse_run(self, mock_run_data):
        """Test parsing run data."""
        run = WorkflowRun(**mock_run_data)
        assert run.id == 67890, "id is not valid"
        assert run.workflow_id == 12345, "workflow_id is not valid"
        assert run.status == RunStatus.COMPLETED, "status is not valid"
        assert run.conclusion == RunConclusion.SUCCESS, "conclusion is not valid"

    def test_is_completed(self, mock_run_data):
        """Test is_completed property."""
        run = WorkflowRun(**mock_run_data)
        assert run.is_completed is True, "is_completed is not valid"

        mock_run_data["status"] = "in_progress"
        mock_run_data["conclusion"] = None
        run = WorkflowRun(**mock_run_data)
        assert run.is_completed is False, "is_completed is not valid"

    def test_is_successful(self, mock_run_data):
        """Test is_successful property."""
        run = WorkflowRun(**mock_run_data)
        assert run.is_successful is True, "is_successful is not valid"

        mock_run_data["conclusion"] = "failure"
        run = WorkflowRun(**mock_run_data)
        assert run.is_successful is False, "is_successful is not valid"

    def test_is_failed(self, mock_run_data):
        """Test is_failed property."""
        mock_run_data["conclusion"] = "failure"
        run = WorkflowRun(**mock_run_data)
        assert run.is_failed is True, "is_failed is not valid"

        mock_run_data["conclusion"] = "success"
        run = WorkflowRun(**mock_run_data)
        assert run.is_failed is False, "is_failed is not valid"


class TestWorkflowJob:
    """Tests for WorkflowJob model."""

    def test_parse_job(self, mock_job_data):
        """Test parsing job data."""
        job = WorkflowJob(**mock_job_data)
        assert job.id == 11111, "id is not valid"
        assert job.run_id == 67890, "run_id is not valid"
        assert job.name == "build", "name is not valid"
        assert job.is_completed is True, "is_completed is not valid"

    def test_duration_seconds(self, mock_job_data):
        """Test duration calculation."""
        job = WorkflowJob(**mock_job_data)
        assert job.duration_seconds == 180.0, "duration_seconds is not valid"

    def test_duration_none_when_incomplete(self, mock_job_data):
        """Test duration is None when job incomplete."""
        mock_job_data["completed_at"] = None
        job = WorkflowJob(**mock_job_data)
        assert job.duration_seconds is None, "duration_seconds is not valid"


class TestArtifactInfo:
    """Tests for ArtifactInfo model."""

    def test_parse_artifact(self, mock_artifact_data):
        """Test parsing artifact data."""
        artifact = ArtifactInfo(**mock_artifact_data)
        assert artifact.id == 22222, "id is not valid"
        assert artifact.name == "test-results", "Result must not be empty"
        assert artifact.size_in_bytes == 1048576, "size_in_bytes is not valid"

    def test_size_mb(self, mock_artifact_data):
        """Test size_mb property."""
        artifact = ArtifactInfo(**mock_artifact_data)
        assert artifact.size_mb == 1.0, "size_mb is not valid"


class TestRateLimitInfo:
    """Tests for RateLimitInfo model."""

    def test_is_exceeded(self):
        """Test is_exceeded property."""
        info = RateLimitInfo(
            limit=5000,
            remaining=0,
            reset=datetime.now(timezone.utc),
            used=5000,
        )
        assert info.is_exceeded is True, "is_exceeded is not valid"

        info = RateLimitInfo(
            limit=5000,
            remaining=100,
            reset=datetime.now(timezone.utc),
            used=4900,
        )
        assert info.is_exceeded is False, "is_exceeded is not valid"


# ============================================================================
# Exception Tests
# ============================================================================


class TestExceptions:
    """Tests for exception classes."""

    def test_github_api_error(self):
        """Test GitHubAPIError."""
        error = GitHubAPIError("Test error", status_code=500)
        assert str(error) == "[500] Test error", "Error should be raised or set"
        assert error.status_code == 500, "Error should be raised or set"

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(reset_at=1234567890)
        assert error.status_code == 403, "Error should be raised or set"
        assert error.reset_at == 1234567890, "Error should be raised or set"

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError()
        assert error.status_code == 401, "Error should be raised or set"

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("workflow", "test.yml")
        assert error.status_code == 404, "Error should be raised or set"
        assert "test.yml" in str(error), "Error should be raised or set"

    def test_workflow_trigger_error(self):
        """Test WorkflowTriggerError."""
        error = WorkflowTriggerError("test.yml", "invalid inputs")
        assert "test.yml" in str(error), "Error should be raised or set"
        assert "invalid inputs" in str(error), "Error should be raised or set"


# ============================================================================
# Client Tests
# ============================================================================


class TestGitHubClient:
    """Tests for GitHubClient."""

    def test_init_with_token(self):
        """Test initialization with token."""
        client = GitHubClient(token="test-token")
        assert client.token == "test-token", "token is not valid"
        assert client.base_url == "https://api.github.com", "base_url is not valid"

    def test_init_from_env(self, monkeypatch):
        """Test initialization from environment."""
        monkeypatch.setenv("GITHUB_TOKEN", "env-token")
        client = GitHubClient()
        assert client.token == "env-token", "token is not valid"

    def test_headers_with_token(self, client):
        """Test headers include authorization."""
        headers = client._get_headers()
        assert "Authorization" in headers, "Condition must be true"
        assert headers["Authorization"] == "Bearer test-token", "Condition must be true"
        assert "X-GitHub-Api-Version" in headers, "Condition must be true"

    def test_headers_without_token(self):
        """Test headers without authorization."""
        client = GitHubClient(token="")
        headers = client._get_headers()
        assert "Authorization" not in headers, "Condition must be true"


class TestGitHubClientAsync:
    """Async tests for GitHubClient."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_list_workflows(self, client, mock_workflow_data):
        """Test listing workflows."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 1,
            "workflows": [mock_workflow_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            workflows = await client.list_workflows("owner", "repo")

        assert len(workflows) == 1, "Workflows must not be empty"
        assert workflows[0].id == 12345, "id is not valid"
        assert workflows[0].name == "Test Workflow", "name is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_get_workflow(self, client, mock_workflow_data):
        """Test getting a workflow."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_workflow_data
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            workflow = await client.get_workflow("owner", "repo", "test.yml")

        assert workflow.id == 12345, "id is not valid"
        assert workflow.name == "Test Workflow", "name is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_list_workflow_runs(self, client, mock_run_data):
        """Test listing workflow runs."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [mock_run_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            runs = await client.list_workflow_runs("owner", "repo")

        assert len(runs) == 1, "Runs must not be empty"
        assert runs[0].id == 67890, "id is not valid"
        assert runs[0].status == RunStatus.COMPLETED, "status is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_get_workflow_run(self, client, mock_run_data):
        """Test getting a workflow run."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_run_data
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            run = await client.get_workflow_run("owner", "repo", 67890)

        assert run.id == 67890, "id is not valid"
        assert run.is_successful is True, "is_successful is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_list_workflow_jobs(self, client, mock_job_data):
        """Test listing workflow jobs."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 1,
            "jobs": [mock_job_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            jobs = await client.list_workflow_jobs("owner", "repo", 67890)

        assert len(jobs) == 1, "Jobs must not be empty"
        assert jobs[0].id == 11111, "id is not valid"
        assert jobs[0].name == "build", "name is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_list_run_artifacts(self, client, mock_artifact_data):
        """Test listing run artifacts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 1,
            "artifacts": [mock_artifact_data],
        }
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            artifacts = await client.list_run_artifacts("owner", "repo", 67890)

        assert len(artifacts) == 1, "Artifacts must not be empty"
        assert artifacts[0].id == 22222, "id is not valid"
        assert artifacts[0].name == "test-results", "Result must not be empty"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_rate_limit_handling(self, client):
        """Test rate limit error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        mock_response.headers = {"x-ratelimit-reset": "1234567890"}

        with patch.object(client, "_create_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = mock_client

            with pytest.raises(RateLimitError):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_authentication_error(self, client):
        """Test authentication error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Bad credentials"
        mock_response.headers = {}

        with patch.object(client, "_create_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = mock_client

            with pytest.raises(AuthenticationError):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_not_found_error(self, client):
        """Test not found error handling."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.headers = {}

        with patch.object(client, "_create_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = mock_client

            with pytest.raises(NotFoundError):
                await client._request("GET", "/repos/owner/repo/not-found")

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_rate_limit_header_parsing(self, client):
        """Test rate limit info from headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-reset": "1704067200",
            "x-ratelimit-used": "1",
        }

        with patch.object(client, "_create_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = mock_client

            await client._request("GET", "/test")

        assert client.rate_limit is not None, "rate_limit must be initialized"
        assert client.rate_limit.limit == 5000, "limit is not valid"
        assert client.rate_limit.remaining == 4999, "remaining is not valid"


# ============================================================================
# Integration-style Tests (mocked)
# ============================================================================


class TestWorkflowOperations:
    """Integration-style tests for workflow operations."""

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_trigger_and_wait_workflow(self, client, mock_run_data):
        """Test triggering and waiting for workflow."""
        # Mock trigger (returns 204)
        trigger_response = MagicMock()
        trigger_response.status_code = 204
        trigger_response.headers = {}

        # Mock list runs (to get run ID)
        list_response = MagicMock()
        list_response.json.return_value = {
            "total_count": 1,
            "workflow_runs": [mock_run_data],
        }
        list_response.status_code = 200
        list_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [trigger_response, list_response]
            run_id = await client.trigger_workflow(
                "owner",
                "repo",
                "test.yml",
                ref="main",
                inputs={"env": "test"},
            )

        assert run_id == 67890, "run_id is not valid"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_cancel_workflow(self, client):
        """Test cancelling a workflow run."""
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.cancel_workflow_run("owner", "repo", 67890)

        assert result is True, "Result must not be empty"

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    @pytest.mark.timeout(30)
    async def test_rerun_workflow(self, client):
        """Test re-running a workflow."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            result = await client.rerun_workflow("owner", "repo", 67890)

        assert result is True, "Result must not be empty"

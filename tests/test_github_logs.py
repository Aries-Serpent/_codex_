"""Tests for GitHub Actions log fetcher functionality.

Tests the GitHub client extensions, CLI commands, API endpoints, and MCP tools
for fetching GitHub Actions logs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone


# =============================================================================
# GitHub Client Tests
# =============================================================================

class TestGitHubClientCheckRuns:
    """Test GitHub client check run methods."""

    @pytest.fixture
    def mock_check_run_data(self):
        """Mock check run data from GitHub API."""
        return {
            "id": 59990656344,
            "name": "Test Coverage",
            "head_sha": "b6b52590b9551c4d29b90ea122d885ef83cd0d8d",
            "status": "completed",
            "conclusion": "success",
            "started_at": "2024-01-10T12:00:00Z",
            "completed_at": "2024-01-10T12:05:00Z",
            "html_url": "https://github.com/Aries-Serpent/_codex_/runs/59990656344",
            "details_url": None,
            "external_id": None,
            "check_suite_id": 123456,
            "app": None,
        }

    @pytest.fixture
    def mock_check_runs_response(self, mock_check_run_data):
        """Mock list check runs response."""
        return {
            "total_count": 1,
            "check_runs": [mock_check_run_data],
        }

    def test_check_run_types(self):
        """Test CheckRun type definitions."""
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        check_run = CheckRun(
            id=123,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        
        assert check_run.id == 123
        assert check_run.is_completed
        assert check_run.is_successful
        assert not check_run.is_failed

    def test_check_run_failed_status(self):
        """Test CheckRun failed status detection."""
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        check_run = CheckRun(
            id=123,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.FAILURE,
            html_url="https://github.com/test",
        )
        
        assert check_run.is_completed
        assert not check_run.is_successful
        assert check_run.is_failed

    @patch('services.github.client.httpx.AsyncClient')
    async def test_get_check_run(self, mock_client_class, mock_check_run_data):
        """Test fetching a single check run."""
        from services.github.client import GitHubClient
        
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_check_run_data
        mock_response.headers = {}
        
        mock_client = Mock()
        mock_client.__aenter__ = Mock(return_value=mock_client)
        mock_client.__aexit__ = Mock(return_value=None)
        mock_client.request = Mock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        # Test
        client = GitHubClient(token="test_token")
        check_run = await client.get_check_run("owner", "repo", 59990656344)
        
        assert check_run.id == 59990656344
        assert check_run.name == "Test Coverage"
        assert check_run.status == "completed"

    @patch('services.github.client.httpx.AsyncClient')
    async def test_list_check_runs_for_ref(self, mock_client_class, mock_check_runs_response):
        """Test listing check runs for a git reference."""
        from services.github.client import GitHubClient
        
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_check_runs_response
        mock_response.headers = {}
        
        mock_client = Mock()
        mock_client.__aenter__ = Mock(return_value=mock_client)
        mock_client.__aexit__ = Mock(return_value=None)
        mock_client.request = Mock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        # Test
        client = GitHubClient(token="test_token")
        check_runs = await client.list_check_runs_for_ref(
            "owner", "repo", "b6b52590b9551c4d29b90ea122d885ef83cd0d8d"
        )
        
        assert len(check_runs) == 1
        assert check_runs[0].id == 59990656344


# =============================================================================
# CLI Tests
# =============================================================================

class TestGitHubLogsCLI:
    """Test CLI commands for GitHub logs."""

    @patch('codex.cli_github_logs._get_github_client')
    def test_fetch_check_run_logs_command(self, mock_get_client):
        """Test check-run CLI command."""
        from click.testing import CliRunner
        from codex.cli_github_logs import cli
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        # Setup mock
        mock_client = Mock()
        mock_check_run = CheckRun(
            id=59990656344,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        mock_client.get_check_run.return_value = mock_check_run
        mock_client.get_check_run_logs.return_value = "Test logs content"
        mock_get_client.return_value = mock_client
        
        # Test
        runner = CliRunner()
        result = runner.invoke(cli, [
            'check-run', 'Aries-Serpent', '_codex_', '59990656344'
        ])
        
        assert result.exit_code == 0
        assert "Test logs content" in result.output
        assert "Successfully fetched logs" in result.output

    @patch('codex.cli_github_logs._get_github_client')
    def test_list_check_runs_command(self, mock_get_client):
        """Test list-check-runs CLI command."""
        from click.testing import CliRunner
        from codex.cli_github_logs import cli
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        # Setup mock
        mock_client = Mock()
        mock_check_run = CheckRun(
            id=123,
            name="Test Run",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        mock_client.list_check_runs_for_ref.return_value = [mock_check_run]
        mock_get_client.return_value = mock_client
        
        # Test
        runner = CliRunner()
        result = runner.invoke(cli, [
            'list-check-runs', 'owner', 'repo', 'ref123'
        ])
        
        assert result.exit_code == 0
        assert "Test Run" in result.output
        assert "123" in result.output


# =============================================================================
# API Tests
# =============================================================================

class TestGitHubLogsAPI:
    """Test API endpoints for GitHub logs."""

    @pytest.fixture
    def mock_github_client(self):
        """Mock GitHub client for API tests."""
        with patch('codex.api.github_logs._get_github_client') as mock:
            client = Mock()
            mock.return_value = client
            yield client

    def test_get_check_run_logs_endpoint(self, mock_github_client):
        """Test GET /github/check-runs/{id}/logs endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from codex.api.github_logs import router
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Setup mock
        mock_check_run = CheckRun(
            id=59990656344,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        mock_github_client.get_check_run.return_value = mock_check_run
        mock_github_client.get_check_run_logs.return_value = "Test logs"
        
        # Test
        response = client.get(
            "/github/check-runs/59990656344/logs",
            params={"owner": "Aries-Serpent", "repo": "_codex_"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["check_run_id"] == 59990656344
        assert data["logs"] == "Test logs"
        assert data["check_run_name"] == "Test"

    def test_list_check_runs_endpoint(self, mock_github_client):
        """Test GET /github/check-runs endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from codex.api.github_logs import router
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Setup mock
        mock_check_run = CheckRun(
            id=123,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_github_client.list_check_runs_for_ref.return_value = [mock_check_run]
        
        # Test
        response = client.get(
            "/github/check-runs",
            params={
                "owner": "Aries-Serpent",
                "repo": "_codex_",
                "ref": "abc123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["check_runs"]) == 1
        assert data["check_runs"][0]["id"] == 123


# =============================================================================
# MCP Tools Tests
# =============================================================================

class TestGitHubLogsMCPTools:
    """Test MCP tools for GitHub logs."""

    @patch('mcp.tools.github_logs._get_github_client')
    def test_fetch_check_run_logs_tool(self, mock_get_client):
        """Test fetch_check_run_logs MCP tool."""
        from mcp.tools.github_logs import fetch_check_run_logs
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        # Setup mock
        mock_client = Mock()
        mock_check_run = CheckRun(
            id=59990656344,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        mock_client.get_check_run.return_value = mock_check_run
        mock_client.get_check_run_logs.return_value = "Test logs"
        mock_get_client.return_value = mock_client
        
        # Test
        result = fetch_check_run_logs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "check_run_id": 59990656344
        })
        
        assert result["success"] is True
        assert result["logs"] == "Test logs"
        assert result["check_run"]["id"] == 59990656344

    @patch('mcp.tools.github_logs._get_github_client')
    def test_list_check_runs_tool(self, mock_get_client):
        """Test list_check_runs MCP tool."""
        from mcp.tools.github_logs import list_check_runs
        from services.github.types import CheckRun, CheckRunStatus, CheckRunConclusion
        
        # Setup mock
        mock_client = Mock()
        mock_check_run = CheckRun(
            id=123,
            name="Test",
            head_sha="abc123",
            status=CheckRunStatus.COMPLETED,
            conclusion=CheckRunConclusion.SUCCESS,
            html_url="https://github.com/test",
        )
        mock_client.list_check_runs_for_ref.return_value = [mock_check_run]
        mock_get_client.return_value = mock_client
        
        # Test
        result = list_check_runs({
            "owner": "Aries-Serpent",
            "repo": "_codex_",
            "ref": "abc123"
        })
        
        assert result["success"] is True
        assert result["total_count"] == 1
        assert len(result["check_runs"]) == 1
        assert result["check_runs"][0]["id"] == 123

    @patch('mcp.tools.github_logs._get_github_client')
    def test_mcp_tool_error_handling(self, mock_get_client):
        """Test MCP tool error handling."""
        from mcp.tools.github_logs import fetch_check_run_logs
        
        # Setup mock to raise error
        mock_client = Mock()
        mock_client.get_check_run.side_effect = Exception("Test error")
        mock_get_client.return_value = mock_client
        
        # Test
        result = fetch_check_run_logs({
            "owner": "test",
            "repo": "test",
            "check_run_id": 123
        })
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]


# =============================================================================
# Integration Tests
# =============================================================================

class TestGitHubLogsIntegration:
    """Integration tests requiring actual GitHub API access."""

    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration", default=False),
        reason="Integration tests require --run-integration flag and GITHUB_TOKEN"
    )
    def test_real_github_api_check_run(self):
        """Test fetching real check run from GitHub API."""
        import os
        from services.github.client import GitHubClientSync
        
        # Requires GITHUB_TOKEN
        if not os.getenv("GITHUB_TOKEN"):
            pytest.skip("GITHUB_TOKEN not set")
        
        client = GitHubClientSync()
        
        # Test with actual check run
        check_run = client.get_check_run(
            "Aries-Serpent",
            "_codex_",
            59990656344
        )
        
        assert check_run.id == 59990656344
        assert check_run.name is not None
        assert check_run.status is not None

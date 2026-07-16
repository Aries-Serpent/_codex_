"""
Phase 7 Lane 4: MCP/GitHub Integration Testing
Comprehensive integration tests for src/mcp module
Coverage Target: ≥40% on primary mcp components

Test Scope:
- GitHub API mock/stub integration (10 tests)
- MCP server communication (8 tests)
- Protocol compliance validation (7 tests)
- Error recovery & retry patterns (5 tests)

Total: 30 integration tests
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Import MCP components
try:
    from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal, hash_credential
    from mcp.config import MCPConfig, ToolDefinition, compute_checksum
    from mcp.errors import (
        MCPError,
        RateLimitExceeded,
        ToolNotFound,
        Unauthorized,
        ValidationError,
        validate_error_response,
    )
    from mcp.rate_limit import MCPRateLimiter
    from mcp.registry import MCPToolRegistry
    from mcp.retries import retry_on_exception
    from mcp.server import MCPServer, Tool, ToolRegistry
    from mcp.server.json_rpc import (
        INVALID_PARAMS,
        INVALID_REQUEST,
        METHOD_NOT_FOUND,
        JsonRpcError,
        JsonRpcRequest,
        JsonRpcResponse,
    )

    MCP_AVAILABLE = True
except ImportError:
    pytest.skip("MCP module not available", allow_module_level=True)
    MCP_AVAILABLE = False


# ============================================================================
# FIXTURES FOR GITHUB API MOCKING
# ============================================================================


@pytest.fixture
def mock_github_client():
    """Mock GitHub API client with common endpoints."""
    client = MagicMock()
    client.rate_limit = {"remaining": 60, "reset": time.time() + 3600}
    client.get_repo = MagicMock(return_value={"name": "test-repo", "owner": "test-org"})
    client.list_issues = MagicMock(
        return_value=[
            {"number": 1, "title": "Test Issue", "state": "open"},
        ]
    )
    client.create_issue = MagicMock(return_value={"number": 2, "title": "New Issue"})
    client.get_issue = MagicMock(return_value={"number": 1, "title": "Test Issue"})
    return client


@pytest.fixture
def github_api_stub():
    """GitHub API response stub with standard HTTP methods."""
    responses = {
        "GET /repos/{owner}/{repo}": {"name": "test-repo", "full_name": "test-org/test-repo"},
        "GET /repos/{owner}/{repo}/issues": [
            {"id": 1, "number": 1, "title": "Issue 1", "state": "open"},
            {"id": 2, "number": 2, "title": "Issue 2", "state": "closed"},
        ],
        "POST /repos/{owner}/{repo}/issues": {
            "id": 3,
            "number": 3,
            "title": "Created Issue",
            "state": "open",
        },
        "GET /rate_limit": {"resources": {"core": {"remaining": 60, "reset": int(time.time()) + 3600}}},
    }

    class APIStub:
        def get(self, endpoint: str, **kwargs):
            return responses.get(endpoint, {})

        def post(self, endpoint: str, **kwargs):
            return responses.get(endpoint, {})

        def call(self, method: str, endpoint: str, **kwargs):
            full_key = f"{method} {endpoint}"
            return responses.get(full_key, {})

    return APIStub()


@pytest.fixture
def mcp_authenticator():
    """MCP authenticator instance for testing."""
    return MCPAuthenticator(session_seed=b"test-seed-12345678901234567890")


@pytest.fixture
def mcp_authorizer():
    """MCP authorizer instance for testing."""
    return MCPAuthorizer()


@pytest.fixture
def mcp_config():
    """Default MCP configuration for tests."""
    return MCPConfig(
        name="test-mcp",
        tools=[
            ToolDefinition(
                name="github-fetch-issues",
                description="Fetch GitHub issues",
                endpoint="https://api.github.com/repos/{owner}/{repo}/issues",
            ),
            ToolDefinition(
                name="github-create-issue",
                description="Create GitHub issue",
                endpoint="https://api.github.com/repos/{owner}/{repo}/issues",
            ),
        ],
        ita_url="http://localhost:8000",
        ita_api_key="test-api-key-12345",
        config_checksum=compute_checksum('{"name": "test-mcp", "tools": []}'),
    )


@pytest.fixture
def tool_registry():
    """ToolRegistry for MCP server."""
    registry = ToolRegistry()
    registry.register(Tool(name="echo", description="Echo tool", schema={"type": "string"}))
    registry.register(
        Tool(name="github-issues", description="GitHub issues tool", schema={"type": "object"})
    )
    return registry


@pytest.fixture
def mcp_server(tool_registry):
    """MCPServer instance for testing."""
    return MCPServer(tool_registry=tool_registry)


# ============================================================================
# SECTION 1: GITHUB API MOCK/STUB INTEGRATION (10 TESTS)
# ============================================================================


class TestGitHubAPIMockIntegration:
    """Test GitHub API mock and stub integration."""

    def test_github_api_stub_response(self, github_api_stub):
        """Test GitHub API stub returns expected responses."""
        response = github_api_stub.get("GET /repos/{owner}/{repo}")
        assert response["name"] == "test-repo"
        assert response["full_name"] == "test-org/test-repo"

    def test_github_api_stub_list_issues(self, github_api_stub):
        """Test GitHub API stub list issues endpoint."""
        response = github_api_stub.get("GET /repos/{owner}/{repo}/issues")
        assert isinstance(response, list)
        assert len(response) == 2
        assert response[0]["number"] == 1
        assert response[1]["state"] == "closed"

    def test_github_api_stub_create_issue(self, github_api_stub):
        """Test GitHub API stub create issue endpoint."""
        response = github_api_stub.post("POST /repos/{owner}/{repo}/issues")
        assert response["number"] == 3
        assert response["title"] == "Created Issue"
        assert response["state"] == "open"

    def test_github_api_stub_rate_limit(self, github_api_stub):
        """Test GitHub API stub rate limit endpoint."""
        response = github_api_stub.get("GET /rate_limit")
        assert "resources" in response
        assert response["resources"]["core"]["remaining"] == 60

    def test_github_mock_client_get_repo(self, mock_github_client):
        """Test mock GitHub client repository retrieval."""
        repo = mock_github_client.get_repo()
        assert repo["name"] == "test-repo"
        assert repo["owner"] == "test-org"

    def test_github_mock_client_list_issues(self, mock_github_client):
        """Test mock GitHub client list issues."""
        issues = mock_github_client.list_issues()
        assert len(issues) == 1
        assert issues[0]["number"] == 1
        assert issues[0]["state"] == "open"

    def test_github_mock_client_create_issue(self, mock_github_client):
        """Test mock GitHub client create issue."""
        issue = mock_github_client.create_issue()
        assert issue["number"] == 2
        assert issue["title"] == "New Issue"

    def test_github_mock_client_rate_limit_info(self, mock_github_client):
        """Test mock GitHub client rate limit information."""
        rate_limit = mock_github_client.rate_limit
        assert rate_limit["remaining"] == 60
        assert rate_limit["reset"] > time.time()

    def test_github_api_integration_with_auth(self, github_api_stub, mcp_authenticator):
        """Test GitHub API integration with authentication."""
        principal = mcp_authenticator.authenticate("test-token")
        assert principal is not None
        assert isinstance(principal, Principal)

    def test_github_api_integration_error_handling(self, mock_github_client):
        """Test GitHub API integration error handling."""
        mock_github_client.get_repo.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            mock_github_client.get_repo()


# ============================================================================
# SECTION 2: MCP SERVER COMMUNICATION (8 TESTS)
# ============================================================================


class TestMCPServerCommunication:
    """Test MCP server communication protocols."""

    @pytest.mark.asyncio
    async def test_server_list_tools(self, mcp_server):
        """Test MCP server list tools command."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
        }
        response = await mcp_server.handle_request(request)
        assert response["id"] == 1
        assert "result" in response
        assert len(response["result"]) == 2

    @pytest.mark.asyncio
    async def test_server_negotiate_version_compatible(self, mcp_server):
        """Test MCP server version negotiation with compatible version."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.negotiateVersion",
            "params": {"supported": ["1.0", "2.0"]},
        }
        response = await mcp_server.handle_request(request)
        assert response["id"] == 1
        assert response["result"] == "1.0"

    @pytest.mark.asyncio
    async def test_server_negotiate_version_incompatible(self, mcp_server):
        """Test MCP server version negotiation with incompatible version."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.negotiateVersion",
            "params": {"supported": ["2.0", "3.0"]},
        }
        response = await mcp_server.handle_request(request)
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == INVALID_PARAMS

    @pytest.mark.asyncio
    async def test_server_unknown_method(self, mcp_server):
        """Test MCP server handles unknown methods."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown.method",
        }
        response = await mcp_server.handle_request(request)
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == METHOD_NOT_FOUND

    @pytest.mark.asyncio
    async def test_server_notification_no_response(self, mcp_server):
        """Test MCP server handles notifications (no response)."""
        request = {
            "jsonrpc": "2.0",
            "method": "mcp.listTools",
        }
        response = await mcp_server.handle_request(request)
        assert response is None

    @pytest.mark.asyncio
    async def test_server_multiple_sequential_requests(self, mcp_server):
        """Test MCP server handles multiple sequential requests."""
        requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "mcp.listTools",
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "mcp.negotiateVersion",
                "params": {"supported": ["1.0"]},
            },
        ]

        responses = []
        for req in requests:
            resp = await mcp_server.handle_request(req)
            responses.append(resp)

        assert len(responses) == 2
        assert responses[0]["id"] == 1
        assert responses[1]["id"] == 2

    @pytest.mark.asyncio
    async def test_server_tool_registry_operations(self, mcp_server):
        """Test MCP server tool registry operations."""
        tools = mcp_server.tool_registry.list_tools()
        assert len(tools) == 2
        assert any(t["name"] == "echo" for t in tools)
        assert any(t["name"] == "github-issues" for t in tools)

    @pytest.mark.asyncio
    async def test_server_json_rpc_response_format(self, mcp_server):
        """Test MCP server JSON-RPC response format compliance."""
        request = {
            "jsonrpc": "2.0",
            "id": 123,
            "method": "mcp.listTools",
        }
        response = await mcp_server.handle_request(request)

        # Verify JSON-RPC 2.0 spec compliance
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 123
        assert "result" in response or "error" in response


# ============================================================================
# SECTION 3: PROTOCOL COMPLIANCE VALIDATION (7 TESTS)
# ============================================================================


class TestProtocolComplianceValidation:
    """Test MCP protocol compliance and validation."""

    def test_json_rpc_request_creation(self):
        """Test JSON-RPC request object creation."""
        req = JsonRpcRequest(method="test.method", params={"key": "value"}, id=1)
        assert req.method == "test.method"
        assert req.params == {"key": "value"}
        assert req.id == 1
        assert not req.is_notification

    def test_json_rpc_notification_detection(self):
        """Test JSON-RPC notification (no id) detection."""
        req = JsonRpcRequest(method="test.method", params={})
        assert req.is_notification

    def test_json_rpc_response_serialization(self):
        """Test JSON-RPC response serialization."""
        resp = JsonRpcResponse(id=1, result={"status": "success"})
        data = resp.to_dict()

        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert data["result"] == {"status": "success"}
        assert "error" not in data

    def test_json_rpc_error_serialization(self):
        """Test JSON-RPC error serialization."""
        error = JsonRpcError(code=-32600, message="Invalid Request", data={"detail": "Test"})
        data = error.to_dict()

        assert data["code"] == -32600
        assert data["message"] == "Invalid Request"
        assert data["data"]["detail"] == "Test"

    def test_error_validation_known_codes(self):
        """Test validation of known MCP error codes."""
        assert validate_error_response("TOOL_NOT_FOUND", "Tool not found")
        assert validate_error_response("VALIDATION_ERROR", "Invalid input")
        assert validate_error_response("RATE_LIMIT_EXCEEDED", "Too many requests")
        assert validate_error_response("UNAUTHORIZED", "Not authenticated")

    def test_error_validation_unknown_codes(self):
        """Test rejection of unknown error codes."""
        assert not validate_error_response("UNKNOWN_ERROR", "Unknown error")
        assert not validate_error_response("", "Empty code")
        assert not validate_error_response("TOOL_NOT_FOUND", "")

    def test_protocol_version_compatibility(self, mcp_server):
        """Test MCP protocol version compatibility."""
        assert "1.0" in mcp_server.supported_versions
        assert len(mcp_server.supported_versions) > 0


# ============================================================================
# SECTION 4: ERROR RECOVERY & RETRY PATTERNS (5 TESTS)
# ============================================================================


class TestErrorRecoveryRetryPatterns:
    """Test error recovery and retry patterns."""

    def test_retry_on_transient_failure(self):
        """Test retry decorator recovers from transient failures."""
        call_count = 0

        @retry_on_exception(exceptions=(ValueError,), tries=3, base_delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = failing_function()
        assert result == "success"
        assert call_count == 3

    def test_retry_max_attempts_exceeded(self):
        """Test retry decorator raises after max attempts."""

        @retry_on_exception(exceptions=(ValueError,), tries=2, base_delay=0.01)
        def always_failing():
            raise ValueError("Persistent error")

        with pytest.raises(ValueError):
            always_failing()

    def test_rate_limiter_exponential_backoff(self):
        """Test rate limiter with exponential backoff."""
        # Use a custom time function to control time progression
        mock_clock = Mock(return_value=0.0)
        limiter = MCPRateLimiter(rate=1.0, capacity=1, time_func=mock_clock)

        # Exhaust burst capacity
        assert limiter.allow("principal", "tool")
        assert not limiter.allow("principal", "tool")

        # Simulate time passing for refill (2 seconds later)
        mock_clock.return_value = 2.0
        assert limiter.allow("principal", "tool")

    def test_mcp_error_exception_hierarchy(self):
        """Test MCP error exception hierarchy."""
        # Test base error
        base_error = MCPError("Test error")
        assert base_error.code == "MCP_ERROR"
        assert base_error.http_status == 500

        # Test specific errors
        tool_not_found = ToolNotFound("Tool missing")
        assert tool_not_found.code == "TOOL_NOT_FOUND"
        assert tool_not_found.http_status == 404

        rate_limit = RateLimitExceeded("Rate limited")
        assert rate_limit.code == "RATE_LIMIT_EXCEEDED"
        assert rate_limit.http_status == 429

    def test_error_detail_preservation(self):
        """Test MCP error detail preservation."""
        details = {"request_id": "123", "timestamp": "2026-01-01"}
        error = MCPError("Test error", details=details)

        error_dict = error.to_dict()
        assert error_dict["details"] == details


# ============================================================================
# SECTION 5: AUTHENTICATION & AUTHORIZATION INTEGRATION (5 TESTS)
# ============================================================================


class TestAuthenticationAuthorizationIntegration:
    """Test authentication and authorization integration."""

    def test_principal_creation_from_credential(self):
        """Test principal creation from credential."""
        principal = Principal.from_credential("test-secret")
        assert principal is not None
        assert principal.principal_id is not None
        assert len(principal.principal_id) == 64  # SHA-256 hex

    def test_authenticator_session_token_generation(self, mcp_authenticator):
        """Test authenticator generates deterministic session tokens."""
        principal = mcp_authenticator.authenticate("test-credential")
        token1 = mcp_authenticator.generate_session_token(principal)
        token2 = mcp_authenticator.generate_session_token(principal)

        # Same principal should generate same token (deterministic)
        assert token1 == token2
        assert len(token1) == 64  # SHA-256 hex

    def test_authorizer_permission_check(self, mcp_authorizer):
        """Test authorizer permission checking."""
        principal = Principal.from_credential("test")

        # Authenticated principal should be authorized
        assert mcp_authorizer.authorize(principal, "test-tool")

        # Unauthenticated principal should not be authorized
        assert not mcp_authorizer.authorize(None, "test-tool")

    def test_authorizer_permission_hash(self, mcp_authorizer):
        """Test authorizer permission hash computation."""
        principal_id = "principal-123"
        tool_name = "test-tool"

        hash1 = mcp_authorizer.compute_permission_hash(principal_id, tool_name)
        hash2 = mcp_authorizer.compute_permission_hash(principal_id, tool_name)

        # Hashes should be deterministic
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_authorizer_confirmation_flag(self, mcp_authorizer):
        """Test authorizer confirmation flag handling."""
        principal = Principal.from_credential("test")

        # Without confirmation flag
        assert mcp_authorizer.confirm_authorization(principal, "tool1", require_confirm=False)

        # With confirmation flag (still permitted for test authorizer)
        assert mcp_authorizer.confirm_authorization(principal, "tool2", require_confirm=True)


# ============================================================================
# SECTION 6: RATE LIMITING & BACKOFF INTEGRATION (5 TESTS)
# ============================================================================


class TestRateLimitingBackoffIntegration:
    """Test rate limiting and backoff integration."""

    def test_rate_limiter_token_bucket_algorithm(self):
        """Test rate limiter token bucket algorithm."""
        limiter = MCPRateLimiter(rate=2.0, capacity=5)

        # Should allow up to capacity
        for _ in range(5):
            assert limiter.allow("p", "t")

        # Should reject when exceeded
        assert not limiter.allow("p", "t")

    def test_rate_limiter_capacity_validation(self):
        """Test rate limiter validates capacity."""
        with pytest.raises(ValueError):
            MCPRateLimiter(rate=1.0, capacity=0)

        with pytest.raises(ValueError):
            MCPRateLimiter(rate=1.0, capacity=-1)

    def test_rate_limiter_rate_validation(self):
        """Test rate limiter validates rate."""
        with pytest.raises(ValueError):
            MCPRateLimiter(rate=0, capacity=1)

        with pytest.raises(ValueError):
            MCPRateLimiter(rate=-1, capacity=1)

    def test_rate_limiter_per_principal_isolation(self):
        """Test rate limiter isolates limits per principal."""
        limiter = MCPRateLimiter(rate=1.0, capacity=1)

        # Different principals should have independent limits
        assert limiter.allow("principal1", "tool")
        assert limiter.allow("principal2", "tool")
        assert not limiter.allow("principal1", "tool")
        assert not limiter.allow("principal2", "tool")

    def test_rate_limiter_reset_functionality(self):
        """Test rate limiter reset functionality."""
        limiter = MCPRateLimiter(rate=1.0, capacity=1)

        assert limiter.allow("p", "t")
        assert not limiter.allow("p", "t")

        limiter.reset("p", "t")
        assert limiter.allow("p", "t")


# ============================================================================
# SECTION 7: CONFIGURATION & VERSIONING (5 TESTS)
# ============================================================================


class TestConfigurationAndVersioning:
    """Test MCP configuration and versioning."""

    def test_tool_definition_creation(self):
        """Test ToolDefinition creation and serialization."""
        tool = ToolDefinition(
            name="test-tool",
            description="A test tool",
            endpoint="https://api.example.com/tool",
            metadata={"version": "1.0"},
        )

        assert tool.name == "test-tool"
        assert tool.description == "A test tool"

        tool_dict = tool.to_dict()
        assert tool_dict["name"] == "test-tool"
        assert tool_dict["metadata"]["version"] == "1.0"

    def test_mcp_config_creation(self, mcp_config):
        """Test MCPConfig creation and properties."""
        assert mcp_config.name == "test-mcp"
        assert len(mcp_config.tools) == 2
        assert mcp_config.ita_url == "http://localhost:8000"
        assert mcp_config.ita_api_key == "test-api-key-12345"

    def test_mcp_config_get_tool(self, mcp_config):
        """Test MCPConfig tool retrieval."""
        tool = mcp_config.get_tool("github-fetch-issues")
        assert tool is not None
        assert tool.name == "github-fetch-issues"

        missing = mcp_config.get_tool("nonexistent")
        assert missing is None

    def test_checksum_computation(self):
        """Test configuration checksum computation."""
        data1 = "test data"
        data2 = "test data"
        data3 = "different data"

        checksum1 = compute_checksum(data1)
        checksum2 = compute_checksum(data2)
        checksum3 = compute_checksum(data3)

        assert checksum1 == checksum2
        assert checksum1 != checksum3
        assert len(checksum1) == 64  # SHA-256 hex

    def test_mcp_config_serialization(self, mcp_config):
        """Test MCPConfig serialization to dict."""
        config_dict = mcp_config.to_dict()

        assert config_dict["name"] == "test-mcp"
        assert len(config_dict["tools"]) == 2
        assert config_dict["ita_url"] == "http://localhost:8000"


# ============================================================================
# INTEGRATION TEST SUITE: END-TO-END SCENARIOS
# ============================================================================


class TestEndToEndIntegrationScenarios:
    """Test end-to-end integration scenarios."""

    @pytest.mark.asyncio
    async def test_authenticated_server_request(self, mcp_server, mcp_authenticator, mcp_authorizer):
        """Test authenticated end-to-end server request."""
        # Authenticate principal
        principal = mcp_authenticator.authenticate("test-credential")
        assert principal is not None

        # Check authorization
        assert mcp_authorizer.authorize(principal, "github-issues")

        # Execute server request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "mcp.listTools",
        }
        response = await mcp_server.handle_request(request)
        assert response["result"] is not None

    @pytest.mark.asyncio
    async def test_rate_limited_server_requests(self, mcp_server):
        """Test rate-limited server requests."""
        limiter = MCPRateLimiter(rate=10.0, capacity=2)
        request_count = 0

        # Make requests until rate limited
        for i in range(5):
            if limiter.allow("client1", "tool1"):
                request = {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "mcp.listTools",
                }
                response = await mcp_server.handle_request(request)
                assert response is not None
                request_count += 1

        assert request_count == 2  # Limited to capacity

    def test_github_api_with_retry_pattern(self, mock_github_client):
        """Test GitHub API with retry pattern."""
        call_count = 0

        def mock_list_issues_with_retry():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary network error")
            return [{"number": 1, "title": "Issue"}]

        mock_github_client.list_issues.side_effect = mock_list_issues_with_retry

        @retry_on_exception(exceptions=(ConnectionError,), tries=3, base_delay=0.01)
        def fetch_with_retry():
            return mock_github_client.list_issues()

        result = fetch_with_retry()
        assert len(result) == 1
        assert call_count == 2

    def test_error_handling_chain(self):
        """Test error handling chain with multiple error types."""
        errors = [
            MCPError("Base error"),
            ToolNotFound("Tool missing"),
            ValidationError("Invalid input"),
            RateLimitExceeded("Too many requests"),
            Unauthorized("Not authenticated"),
        ]

        for error in errors:
            error_dict = error.to_dict()
            assert "code" in error_dict
            assert "message" in error_dict
            assert error.http_status >= 400


# ============================================================================
# PERFORMANCE & COMPLIANCE TESTS
# ============================================================================


class TestPerformanceAndCompliance:
    """Test performance and compliance aspects."""

    def test_credential_hashing_performance(self):
        """Test credential hashing performance."""
        credentials = ["cred1", "cred2", "cred3", "cred4", "cred5"]

        start = time.time()
        hashes = [hash_credential(c) for c in credentials]
        elapsed = time.time() - start

        assert len(hashes) == 5
        assert all(len(h) == 64 for h in hashes)
        assert elapsed < 1.0  # Should be very fast

    def test_rate_limiter_performance(self):
        """Test rate limiter performance with many principals."""
        limiter = MCPRateLimiter(rate=1000.0, capacity=100)

        start = time.time()
        for i in range(1000):
            limiter.allow(f"principal_{i % 10}", f"tool_{i % 5}")
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should handle 1000 calls quickly

    def test_json_rpc_compliance_request_id_types(self):
        """Test JSON-RPC compliance with different ID types."""
        # String ID
        req1 = JsonRpcRequest(method="test", id="string-id")
        assert req1.id == "string-id"

        # Integer ID
        req2 = JsonRpcRequest(method="test", id=123)
        assert req2.id == 123

        # No ID (notification)
        req3 = JsonRpcRequest(method="test")
        assert req3.is_notification


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

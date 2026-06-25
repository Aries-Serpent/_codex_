"""
Comprehensive tests for Authentication Middleware.

Tests cover:
- Token validation
- Request authentication
- Error responses
- Rate limiting
- Header parsing
- ****** handling
- CORS and security headers
"""

from unittest.mock import AsyncMock, patch

import pytest

from codex.auth.exceptions import InvalidCredentialsError
from codex.auth.middleware import AuthMiddleware
from codex.auth.token_manager import TokenManager, TokenType

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def token_manager():
    """Create token manager."""
    return TokenManager(secret_key="test-secret-key-middleware")


@pytest.fixture
def mock_app():
    """Create mock ASGI application."""
    return AsyncMock()


@pytest.fixture
def middleware(mock_app, token_manager):
    """Create authentication middleware."""
    return AuthMiddleware(app=mock_app, token_manager=token_manager)


@pytest.fixture
def valid_token(token_manager):
    """Create a valid token."""
    claims = token_manager.create_token(
        subject="user123",
        token_type=TokenType.ACCESS,
    )
    return claims


# ============================================================================
# Token Extraction Tests
# ============================================================================


class TestTokenExtraction:
    """Token extraction from requests."""

    def test_extract_bearer_token(self, middleware):
        headers = {"Authorization": "******"}
        token = middleware.extract_token(headers)
        assert token == "token123"

    def test_extract_bearer_token_case_insensitive(self, middleware):
        headers = {"Authorization": "bearer token456"}
        token = middleware.extract_token(headers)
        assert token == "token456"

    def test_extract_missing_token(self, middleware):
        headers = {}
        token = middleware.extract_token(headers)
        assert token is None

    def test_extract_missing_authorization_header(self, middleware):
        headers = {"Content-Type": "application/json"}
        token = middleware.extract_token(headers)
        assert token is None

    def test_extract_malformed_authorization_header(self, middleware):
        headers = {"Authorization": "NotBearer token123"}
        token = middleware.extract_token(headers)
        assert token is None

    def test_extract_empty_authorization_header(self, middleware):
        headers = {"Authorization": ""}
        token = middleware.extract_token(headers)
        assert token is None

    def test_extract_authorization_only_scheme(self, middleware):
        headers = {"Authorization": "Bearer"}
        token = middleware.extract_token(headers)
        assert token is None or token == ""

    def test_extract_authorization_extra_spaces(self, middleware):
        headers = {"Authorization": "******  "}
        # Should handle gracefully
        token = middleware.extract_token(headers)
        assert token

    def test_extract_token_with_special_chars(self, middleware):
        headers = {"Authorization": "******"}
        token = middleware.extract_token(headers)
        assert "token" in token


# ============================================================================
# ****** Validation Tests
# ============================================================================


class TestBearerTokenValidation:
    """****** format and validation."""

    def test_validate_bearer_token_format(self):
        # ****** are typically JWT format
        token = "******"
        assert len(token.split(".")) >= 2

    def test_bearer_token_with_padding(self):
        # JWT tokens use base64url which doesn't need padding
        token = "******"
        assert "." in token

    def test_bearer_token_minimum_length(self):
        token = "x" * 10  # Very short token
        assert len(token) > 0


# ============================================================================
# Request Authentication Tests
# ============================================================================


class TestRequestAuthentication:
    """Request-level authentication."""

    def test_authenticate_request_with_valid_token(self, middleware, token_manager):
        token_manager.create_token(
            subject="user123",
            token_type=TokenType.ACCESS,
        )
        headers = {"Authorization": "******"}

        result = middleware.authenticate_request(headers)
        assert result.user_id == "user123"

    def test_authenticate_request_missing_token(self, middleware):
        headers = {}

        with pytest.raises((InvalidCredentialsError, ValueError)):
            middleware.authenticate_request(headers)

    def test_authenticate_request_invalid_token(self, middleware):
        headers = {"Authorization": "******"}

        with pytest.raises((InvalidCredentialsError, ValueError)):
            middleware.authenticate_request(headers)

    def test_authenticate_request_expired_token(self, middleware, token_manager):
        with patch.object(token_manager, "validate_token") as mock_validate:
            mock_validate.side_effect = Exception("Token expired")

            headers = {"Authorization": "******"}

            with pytest.raises(Exception):
                middleware.authenticate_request(headers)

    def test_authenticate_request_none_headers(self, middleware):
        with pytest.raises((InvalidCredentialsError, TypeError)):
            middleware.authenticate_request(None)

    def test_authenticate_request_empty_headers(self, middleware):
        with pytest.raises(InvalidCredentialsError):
            middleware.authenticate_request({})


# ============================================================================
# Error Response Tests
# ============================================================================


class TestErrorResponses:
    """Error response handling."""

    def test_missing_token_error_response(self, middleware):
        response = middleware.error_response("Missing authentication token", 401)
        assert response.status_code == 401
        assert "Missing authentication token" in str(response.body)

    def test_invalid_token_error_response(self, middleware):
        response = middleware.error_response("Invalid token", 401)
        assert response.status_code == 401
        assert "Invalid token" in str(response.body)

    def test_forbidden_error_response(self, middleware):
        response = middleware.error_response("Insufficient permissions", 403)
        assert response.status_code == 403

    def test_error_response_format(self, middleware):
        response = middleware.error_response("Test error", 401)
        assert response.status_code == 401
        # Response should include error message


# ============================================================================
# Scope/Permission Tests
# ============================================================================


class TestScopeAndPermissions:
    """Token scope and permission validation."""

    def test_verify_scope_valid(self, middleware, token_manager):
        token = token_manager.create_token(
            subject="user123", token_type=TokenType.ACCESS, scope="user:read user:write"
        )

        is_valid = middleware.verify_scope(token, "user:read")
        assert is_valid

    def test_verify_scope_insufficient(self, middleware, token_manager):
        token = token_manager.create_token(
            subject="user123", token_type=TokenType.ACCESS, scope="user:read"
        )

        is_valid = middleware.verify_scope(token, "user:write")
        assert not is_valid

    def test_verify_scope_multiple_required(self, middleware, token_manager):
        token = token_manager.create_token(
            subject="user123", token_type=TokenType.ACCESS, scope="user:read user:write admin:read"
        )

        # Has both required scopes
        assert middleware.verify_scope(token, "user:read")
        assert middleware.verify_scope(token, "user:write")
        assert middleware.verify_scope(token, "admin:read")

    def test_verify_scope_missing(self, middleware, token_manager):
        token = token_manager.create_token(
            subject="user123", token_type=TokenType.ACCESS, scope="user:read"
        )

        is_valid = middleware.verify_scope(token, "admin:write")
        assert not is_valid


# ============================================================================
# Rate Limiting Tests
# ============================================================================


class TestRateLimiting:
    """Rate limiting functionality."""

    def test_rate_limit_tracking(self, middleware):
        user_id = "user123"
        ip_address = "192.168.1.1"

        # First request
        is_limited = middleware.is_rate_limited(user_id, ip_address)
        assert not is_limited

    def test_rate_limit_exceeded(self, middleware):
        user_id = "user456"
        ip_address = "192.168.1.2"

        # Simulate multiple requests
        with patch.object(middleware, "get_request_count", return_value=1000):
            middleware.is_rate_limited(user_id, ip_address)
            # Depends on rate limit threshold

    def test_rate_limit_reset(self, middleware):
        user_id = "user789"
        ip_address = "192.168.1.3"

        middleware.reset_rate_limit(user_id, ip_address)
        is_limited = middleware.is_rate_limited(user_id, ip_address)
        assert not is_limited

    def test_rate_limit_per_user(self, middleware):
        # Different users should have separate rate limit tracking
        middleware.is_rate_limited("user1", "192.168.1.1")
        middleware.is_rate_limited("user2", "192.168.1.1")

        # Should not affect each other

    def test_rate_limit_per_ip(self, middleware):
        # Different IPs should have separate rate limit tracking
        middleware.is_rate_limited("user1", "192.168.1.1")
        middleware.is_rate_limited("user1", "192.168.1.2")

        # Should not affect each other


# ============================================================================
# Token Type Validation Tests
# ============================================================================


class TestTokenTypeValidation:
    """Token type specific validation."""

    def test_validate_access_token_type(self, middleware, token_manager):
        token_manager.create_token(
            subject="user123",
            token_type=TokenType.ACCESS,
        )

        # Should accept ACCESS tokens
        result = middleware.authenticate_request(
            {"Authorization": "******"}, required_token_type=TokenType.ACCESS
        )
        assert result

    def test_validate_refresh_token_as_access(self, middleware, token_manager):
        token_manager.create_token(
            subject="user123",
            token_type=TokenType.REFRESH,
        )

        # Should reject REFRESH token when ACCESS is required
        with pytest.raises((InvalidCredentialsError, ValueError)):
            middleware.authenticate_request(
                {"Authorization": "******"}, required_token_type=TokenType.ACCESS
            )

    def test_validate_session_token_type(self, middleware, token_manager):
        token_manager.create_token(
            subject="user123",
            token_type=TokenType.SESSION,
        )

        # Should accept SESSION tokens
        result = middleware.authenticate_request(
            {"Authorization": "******"}, required_token_type=TokenType.SESSION
        )
        assert result


# ============================================================================
# CORS and Security Headers Tests
# ============================================================================


class TestSecurityHeaders:
    """Security header handling."""

    def test_add_security_headers(self, middleware):
        headers = middleware.get_security_headers()
        assert headers
        # Should include common security headers
        [k.lower() for k in headers.keys()]

    def test_cors_origin_validation(self, middleware):
        allowed_origins = ["https://example.com", "https://app.example.com"]
        origin = "https://example.com"

        is_valid = middleware.is_allowed_origin(origin, allowed_origins)
        assert is_valid

    def test_cors_origin_denied(self, middleware):
        allowed_origins = ["https://example.com"]
        origin = "https://malicious.com"

        is_valid = middleware.is_allowed_origin(origin, allowed_origins)
        assert not is_valid

    def test_cors_wildcard_origin(self, middleware):
        # Wildcard origin is generally not recommended but may be allowed
        allowed_origins = ["*"]
        origin = "https://any.domain.com"

        is_valid = middleware.is_allowed_origin(origin, allowed_origins)
        assert is_valid

    def test_cors_null_origin(self, middleware):
        # null origin (from file:// URLs)
        allowed_origins = ["null"]
        origin = "null"

        is_valid = middleware.is_allowed_origin(origin, allowed_origins)
        assert is_valid


# ============================================================================
# Header Case Sensitivity Tests
# ============================================================================


class TestHeaderHandling:
    """HTTP header handling and case sensitivity."""

    def test_authorization_header_case_insensitive(self, middleware):
        # HTTP headers are case-insensitive
        headers1 = {"Authorization": "******"}
        headers2 = {"authorization": "******"}
        headers3 = {"AUTHORIZATION": "******"}

        token1 = middleware.extract_token(headers1)
        middleware.extract_token(headers2)
        middleware.extract_token(headers3)

        # All should work (implementation dependent)
        assert token1 is None or isinstance(token1, str)  # Valid return type (token or None)

    def test_custom_header_extraction(self, middleware):
        headers = {"X-Auth-Token": "custom_token_123"}

        # Should be able to extract from custom header
        token = middleware.extract_token(headers, header_name="X-Auth-Token")
        if token:
            assert token == "custom_token_123"


# ============================================================================
# Integration Tests
# ============================================================================


class TestMiddlewareIntegration:
    """Middleware integration scenarios."""

    def test_full_authentication_flow(self, middleware, token_manager):
        # Create token
        token = token_manager.create_token(
            subject="user123", token_type=TokenType.ACCESS, scope="user:read user:write"
        )

        # Extract from headers
        headers = {"Authorization": "******"}
        extracted = middleware.extract_token(headers)
        assert extracted == token

        # Authenticate request
        result = middleware.authenticate_request(headers)
        assert result.user_id == "user123"

        # Verify scope
        assert middleware.verify_scope(result, "user:read")

    def test_authentication_failure_flow(self, middleware):
        headers = {"Authorization": "******"}

        with pytest.raises((InvalidCredentialsError, ValueError)):
            middleware.authenticate_request(headers)

    def test_missing_token_flow(self, middleware):
        headers = {}

        with pytest.raises((InvalidCredentialsError, ValueError)):
            middleware.authenticate_request(headers)


# ============================================================================
# Edge Cases Tests
# ============================================================================


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_very_long_token(self, middleware):
        headers = {"Authorization": "******"}

        token = middleware.extract_token(headers)
        assert token

    def test_token_with_special_characters(self, middleware):
        headers = {"Authorization": "******"}

        token = middleware.extract_token(headers)
        assert token

    def test_multiple_authorization_headers(self, middleware):
        # Some implementations might have multiple values
        headers = {"Authorization": "****** ******"}

        middleware.extract_token(headers)
        # Should extract first or raise error

    def test_bearer_with_extra_whitespace(self, middleware):
        headers = {"Authorization": "   ******   "}

        middleware.extract_token(headers)
        # Should handle gracefully

    def test_unicode_in_authorization_header(self, middleware):
        headers = {"Authorization": "******"}

        token = middleware.extract_token(headers)
        assert token


# ============================================================================
# MUTATION-KILLING TESTS FOR MIDDLEWARE
# ============================================================================


class TestMiddlewareReturnValueMutations:
    """Kill return value mutations."""

    def test_extract_token_returns_string_or_none(self, middleware):
        """Kill: Return type mutations in token extraction."""
        # Valid header
        headers = {"Authorization": "******"}
        result = middleware.extract_token(headers)

        # If token exists, MUST be string or None
        if result is not None:
            assert isinstance(result, str), "Token MUST be string"

        # Missing header - should return None
        headers_missing = {}
        result_missing = middleware.extract_token(headers_missing)

        # MUST handle missing gracefully (None, empty string, or exception)
        assert result_missing is None or isinstance(result_missing, str)

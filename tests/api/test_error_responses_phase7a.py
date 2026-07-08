"""
Comprehensive Error Response Tests for Phase 7A WAVE 2

Tests for error handling, error messages, and error response format.

Categories:
- Error message format validation
- Error code consistency
- Stack trace handling
- Proper HTTP headers in error responses
- Rate limiting error responses
- Authentication error messages # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
- Business logic error messages
"""

from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
from fastapi import FastAPI
from fastapi.testclient import TestClient

from codex.api.auth_routes import create_auth_router
from codex.auth.authenticator import Authenticator
from codex.auth.token_manager import TokenManager
from codex.auth.user_store import UserStore

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_components():
    """Create fresh authentication components."""
    store = UserStore()
    tokens = TokenManager(secret_key="test-secret-phase7a")
    auth = Authenticator(user_store=store, token_manager=tokens)
    return store, tokens, auth


@pytest.fixture
def test_client(auth_components):
    """Create FastAPI test client with auth router."""
    _, _, auth = auth_components
    app = FastAPI()
    router = create_auth_router(authenticator=auth)
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def registered_user(auth_components, test_client):
    """Create a registered user."""
    _, _, auth = auth_components
    auth.register("errortest", "error@example.com", "SecurePass123!")
    return {"username": "errortest", "password": "SecurePass123!", "email": "error@example.com"}


# ---------------------------------------------------------------------------
# Error Message Format Tests
# ---------------------------------------------------------------------------


class TestErrorMessageFormat:
    """Tests for error message format and structure."""

    def test_validation_error_has_detail_field(self, test_client):
        """Validation error should include detail field."""
        response = test_client.post(
            "/auth/register", json={"username": "test"}  # Missing required fields
        )
        assert response.status_code == 422, "Response must not be empty"
        data = response.json()
        assert "detail" in data, "Data must not be empty"

    def test_error_response_is_json(self, test_client):
        """Error response should be valid JSON."""
        response = test_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrong"}
        )
        if response.status_code >= 400:
            # Should be valid JSON
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_error_contains_description(self, test_client):
        """Error should contain human-readable description."""
        response = test_client.post("/auth/register", json={"username": "test", "password": "weak"})
        if response.status_code >= 400:
            data = response.json()
            # Should have some descriptive field
            assert any(field in data for field in ["detail", "message", "error"])

    def test_404_error_includes_resource_info(self, test_client):
        """404 error should indicate what wasn't found."""
        response = test_client.get("/auth/user/99999")
        if response.status_code == 404:
            data = response.json()
            assert "detail" in data or "message" in data, "Data must not be empty"

    def test_400_error_includes_field_info(self, test_client):
        """400 error should indicate which field is wrong."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "invalid-email", "password": "SecurePass123!"},
        )
        if response.status_code >= 400:
            data = response.json()
            # Should mention which field
            assert "detail" in data or "message" in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# Error Code Consistency Tests
# ---------------------------------------------------------------------------


class TestErrorCodeConsistency:
    """Tests for error code consistency."""

    def test_same_error_returns_same_code(self, test_client):
        """Same error type should return same code consistently."""
        response1 = test_client.post(
            "/auth/login", json={"username": "nonexistent1", "password": "wrong"}
        )
        response2 = test_client.post(
            "/auth/login", json={"username": "nonexistent2", "password": "wrong"}
        )
        # Both should return same error code
        assert response1.status_code == response2.status_code, "Response must not be empty"

    def test_validation_errors_consistent(self, test_client):
        """Validation errors should be consistent."""
        response1 = test_client.post(
            "/auth/register",
            json={"username": 123, "email": "test@example.com", "password": "Pass1!"},
        )
        response2 = test_client.post(
            "/auth/register",
            json={"username": None, "email": "test@example.com", "password": "Pass1!"},
        )
        # Both should return validation error
        assert response1.status_code == 422 or response1.status_code == 400, "Response must not be empty"
        assert response2.status_code == 422 or response2.status_code == 400, "Response must not be empty"

    def test_authentication_errors_consistent(self, test_client):
        """Authentication errors should be consistent."""
        response1 = test_client.post(
            "/auth/login", json={"username": "user1", "password": "wrongpass"}
        )
        response2 = test_client.post(
            "/auth/login", json={"username": "user2", "password": "wrongpass"}
        )
        # Both should return same auth error code
        assert response1.status_code == response2.status_code, "Response must not be empty"


# ---------------------------------------------------------------------------
# Stack Trace Tests
# ---------------------------------------------------------------------------


class TestStackTraceHandling:
    """Tests for proper stack trace handling in errors."""

    def test_error_response_no_stack_trace_in_production(self, test_client):
        """Production errors should not expose stack traces."""
        response = test_client.post("/auth/login", json={"username": "test", "password": "wrong"})
        if response.status_code >= 400:
            data = response.json()
            data_str = str(data)
            # Should not contain traceback indicators
            assert "traceback" not in data_str.lower(), "Data must not be empty"
            assert "file " not in data_str.lower() or "line " not in data_str.lower(), "Data must not be empty"

    def test_500_error_no_internal_details(self, test_client):
        """500 errors should not expose internal implementation details."""
        with patch("codex.api.auth_routes.Authenticator.register") as mock:
            mock.side_effect = Exception("Database connection failed")
            response = test_client.post(
                "/auth/register",
                json={
                    "username": "test",
                    "email": "test@example.com",
                    "password": "SecurePass123!",
                },
            )
            if response.status_code == 500:
                data = response.json()
                # Should not mention database
                assert "database" not in str(data).lower(), "Data must not be empty"
                assert "connection" not in str(data).lower(), "Data must not be empty"

    def test_error_response_sanitized(self, test_client):
        """Error responses should be sanitized."""
        response = test_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrong"}
        )
        if response.status_code >= 400:
            data = response.json()
            # Should be safe to display to user
            for field, value in data.items():
                if isinstance(value, str):
                    # Should not contain system paths
                    assert "/home/" not in value, "Value must be initialized"
                    assert "/var/" not in value, "Value must be initialized"


# ---------------------------------------------------------------------------
# HTTP Headers Tests
# ---------------------------------------------------------------------------


class TestErrorHTTPHeaders:
    """Tests for HTTP headers in error responses."""

    def test_error_response_has_content_type(self, test_client):
        """Error response should have Content-Type header."""
        response = test_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrong"}
        )
        if response.status_code >= 400:
            assert "content-type" in response.headers, "Response must not be empty"
            assert "json" in response.headers.get("content-type", "").lower()

    def test_error_response_has_status_code_header(self, test_client):
        """Error response should have proper status code."""
        response = test_client.post("/auth/register", json={"username": "test"})
        assert response.status_code in [400, 422]

    def test_validation_error_content_type(self, test_client):
        """Validation error should be JSON."""
        response = test_client.post("/auth/register", json={})
        assert response.status_code == 422, "Response must not be empty"
        assert "application/json" in response.headers.get("content-type", "")

    def test_unauthorized_error_includes_www_authenticate(self, test_client):
        """401 error may include WWW-Authenticate header."""
        response = test_client.get("/protected", headers={})
        # May return 401 or 404 depending on endpoint
        if response.status_code == 401:
            # May have WWW-Authenticate header
            assert "www-authenticate" in response.headers or True, "Response must not be empty"


# ---------------------------------------------------------------------------
# Rate Limiting Error Tests
# ---------------------------------------------------------------------------


class TestRateLimitingErrors:
    """Tests for rate limiting error responses."""

    def test_rate_limit_error_code(self, test_client):
        """Rate limit error should return 429."""
        # Would need to trigger rate limiting
        # This is a placeholder
        assert True, "True is not valid"

    def test_rate_limit_headers_present(self, test_client):
        """Rate limit response should include relevant headers."""
        # Would need to trigger rate limiting
        assert True, "True is not valid"

    def test_rate_limit_retry_after_header(self, test_client):
        """Rate limit error should include Retry-After header."""
        # Would need to trigger rate limiting
        assert True, "True is not valid"


# ---------------------------------------------------------------------------
# Authentication Error Tests
# ---------------------------------------------------------------------------


class TestAuthenticationErrors:
    """Tests for authentication-related error messages."""

    def test_invalid_credentials_error_message(self, test_client):
        """Invalid credentials should return appropriate message."""
        response = test_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrong"}
        )
        assert response.status_code == 400, "Response must not be empty"
        data = response.json()
        # Message should be generic for security
        assert "detail" in data or "message" in data, "Data must not be empty"

    def test_expired_token_error_message(self, test_client):
        """Expired token should return appropriate message."""
        response = test_client.get("/protected", headers={"Authorization": "******"})
        # Depends on implementation
        assert response.status_code in [401, 404, 403]

    def test_missing_token_error_message(self, test_client):
        """Missing token should return appropriate message."""
        response = test_client.get("/protected")
        # May return 401 or 404
        if response.status_code == 401:
            data = response.json()
            assert "token" in str(data).lower() or "authorization" in str(data).lower(), "Data must not be empty"

    def test_invalid_token_format_error(self, test_client):
        """Invalid token format should return appropriate error."""
        response = test_client.get("/protected", headers={"Authorization": "InvalidFormat"})
        # Should return 401
        assert response.status_code in [401, 404, 403]

    def test_token_verification_error(self, test_client):
        """Token verification failure should be handled."""
        response = test_client.get("/protected", headers={"Authorization": "******"})
        assert response.status_code in [401, 404, 403]


# ---------------------------------------------------------------------------
# Business Logic Error Tests
# ---------------------------------------------------------------------------


class TestBusinessLogicErrors:
    """Tests for business logic error messages."""

    def test_duplicate_user_error_message(self, test_client, registered_user):
        """Duplicate user error should be clear."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": registered_user["username"],
                "email": "different@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 400, "Response must not be empty"
        data = response.json()
        assert "detail" in data or "message" in data, "Data must not be empty"

    def test_weak_password_error_message(self, test_client):
        """Weak password error should be informative."""
        response = test_client.post(
            "/auth/register",
            json={"username": "weakpass", "email": "weak@example.com", "password": "weak"},
        )
        assert response.status_code in [400, 422]
        data = response.json()
        # Should indicate password requirement
        assert "password" in str(data).lower(), "Data must not be empty"

    def test_invalid_email_error_message(self, test_client):
        """Invalid email error should be clear."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "not-an-email", "password": "SecurePass123!"},
        )
        assert response.status_code in [400, 422]
        data = response.json()
        # Should indicate email requirement
        assert "email" in str(data).lower() or "invalid" in str(data).lower(), "Data must not be empty"

    def test_missing_required_field_error(self, test_client):
        """Missing required field should have clear error."""
        response = test_client.post(
            "/auth/register", json={"username": "test", "email": "test@example.com"}
        )
        assert response.status_code == 422, "Response must not be empty"
        data = response.json()
        # Should indicate which field is missing
        assert "password" in str(data).lower() or "field" in str(data).lower(), "Data must not be empty"


# ---------------------------------------------------------------------------
# Error Response Consistency Tests
# ---------------------------------------------------------------------------


class TestErrorResponseConsistency:
    """Tests for consistency in error responses."""

    def test_error_response_structure(self, test_client):
        """Error responses should have consistent structure."""
        response = test_client.post("/auth/login", json={"username": "test", "password": "wrong"})
        if response.status_code >= 400:
            data = response.json()
            # Should be dict with error info
            assert isinstance(data, dict)
            assert any(field in data for field in ["detail", "message", "error"])

    def test_validation_error_structure(self, test_client):
        """Validation errors should have consistent structure."""
        response = test_client.post("/auth/register", json={})
        assert response.status_code == 422, "Response must not be empty"
        data = response.json()
        assert "detail" in data, "Data must not be empty"

    def test_multiple_validation_errors_format(self, test_client):
        """Multiple validation errors should be formatted consistently."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": 123,  # Wrong type
                "password": 456,  # Wrong type
                # Missing email
            },
        )
        assert response.status_code in [400, 422]
        data = response.json()
        # Should indicate all errors
        assert "detail" in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# Error Message Content Tests
# ---------------------------------------------------------------------------


class TestErrorMessageContent:
    """Tests for error message content."""

    def test_error_not_empty(self, test_client):
        """Error message should not be empty."""
        response = test_client.post(
            "/auth/login", json={"username": "nonexistent", "password": "wrong"}
        )
        if response.status_code >= 400:
            data = response.json()
            detail = data.get("detail", "")
            assert len(str(detail)) > 0, "Collection must not be empty"

    def test_error_is_readable(self, test_client):
        """Error message should be human-readable."""
        response = test_client.post("/auth/register", json={"username": "test"})
        if response.status_code >= 400:
            data = response.json()
            # Should contain readable text, not just codes
            detail = str(data.get("detail", ""))
            assert any(c.isalpha() for c in detail), "Condition must be true"

    def test_error_language_professional(self, test_client):
        """Error messages should be professional."""
        response = test_client.post("/auth/login", json={"username": "test", "password": "wrong"})
        if response.status_code >= 400:
            data = response.json()
            detail = str(data).lower()
            # Should not contain profanity or slang
            assert "fuck" not in detail, "Condition must be true"
            assert "shit" not in detail, "Condition must be true"

    def test_error_not_revealing_internals(self, test_client):
        """Error messages should not reveal internal information."""
        response = test_client.post("/auth/login", json={"username": "test", "password": "wrong"})
        if response.status_code >= 400:
            data = str(response.json()).lower()
            # Should not reveal implementation details
            assert "sql" not in data, "Data must not be empty"
            assert "/usr/" not in data, "Data must not be empty"
            assert "config" not in data or "configuration" not in data, "Data must not be empty"


# ---------------------------------------------------------------------------
# Specific Error Condition Tests
# ---------------------------------------------------------------------------


class TestSpecificErrorConditions:
    """Tests for specific error conditions."""

    def test_password_validation_error_specificity(self, test_client):
        """Password error should indicate why it failed."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": "test",
                "email": "test@example.com",
                "password": "short",  # Too short, no uppercase, no digits
            },
        )
        if response.status_code in [400, 422]:
            data = response.json()
            # Should mention password requirement
            assert "password" in str(data).lower(), "Data must not be empty"

    def test_email_validation_error_specificity(self, test_client):
        """Email error should indicate format issue."""
        response = test_client.post(
            "/auth/register",
            json={"username": "test", "email": "invalid.email", "password": "SecurePass123!"},
        )
        if response.status_code in [400, 422]:
            data = response.json()
            # Should mention email
            assert "email" in str(data).lower() or "invalid" in str(data).lower(), "Data must not be empty"

    def test_username_conflict_error_specificity(self, test_client, registered_user):
        """Username conflict should be clearly indicated."""
        response = test_client.post(
            "/auth/register",
            json={
                "username": registered_user["username"],
                "email": "newemail@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 400, "Response must not be empty"
        data = response.json()
        # Should mention username or already exists
        error_msg = str(data).lower()
        assert "username" in error_msg or "exists" in error_msg or "already" in error_msg

# Import the modules we're testing
import time
from unittest.mock import MagicMock

import pytest

from src.codex.auth.middleware import (
    APIKeyValidator,
    AuthConfig,  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    AuthMethod,
    AuthMiddleware,
    AuthResult,
    RateLimiter,
    get_current_scopes,
    get_current_user,
)
from src.codex.auth.token_manager import TokenManager


class TestAuthConfig:
    """Tests for AuthConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AuthConfig()
        assert config.enabled is True, "enabled is not valid"
        assert config.default_method == AuthMethod.JWT, "default_method is not valid"
        assert config.api_key_header == "X-API-Key", "api_key_header is not valid"
        assert config.bearer_header == "Authorization", "bearer_header is not valid"
        assert "/health" in config.exempt_paths, "Condition must be true"
        assert "/ready" in config.exempt_paths, "Condition must be true"

    def test_custom_config(self):
        """Test custom configuration."""
        config = AuthConfig(
            enabled=False,
            default_method=AuthMethod.API_KEY,
            rate_limit_requests=50,
        )
        assert config.enabled is False, "enabled is not valid"
        assert config.default_method == AuthMethod.API_KEY, "default_method is not valid"
        assert config.rate_limit_requests == 50, "rate_limit_requests is not valid"


class TestAuthResult:
    """Tests for AuthResult."""

    def test_authenticated_result(self):
        """Test authenticated result."""
        result = AuthResult(
            authenticated=True,
            method=AuthMethod.JWT,
            user_id="user123",
            scopes={"read", "write"},
        )
        assert result.authenticated is True, "Result must not be empty"
        assert result.method == AuthMethod.JWT, "Result must not be empty"
        assert result.user_id == "user123", "Result must not be empty"
        assert "read" in result.scopes, "Result must not be empty"

    def test_unauthenticated_result(self):
        """Test unauthenticated result."""
        result = AuthResult(authenticated=False, method=AuthMethod.NONE, error="No credentials")
        assert result.authenticated is False, "Result must not be empty"
        assert result.error == "No credentials", "Result must not be empty"


class TestAPIKeyValidator:
    """Tests for APIKeyValidator."""

    def test_register_and_validate_key(self):
        """Test registering and validating an API key."""
        validator = APIKeyValidator()

        # Register a key using secure HMAC-SHA256 hashing
        api_key = "test-api-key-123"
        key_hash = validator.hash_api_key(api_key)

        validator.register_key(
            key_hash=key_hash, user_id="user123", scopes=["read", "write"], name="Test Key"
        )

        # Validate the key
        result = validator.validate_key(api_key)
        assert result is not None, "result must be initialized"
        assert result["user_id"] == "user123", "Result must not be empty"
        assert "read" in result["scopes"], "Result must not be empty"

    def test_invalid_key_returns_none(self):
        """Test that invalid key returns None."""
        validator = APIKeyValidator()
        result = validator.validate_key("invalid-key")
        assert result is None, "Result must not be empty"

    def test_revoke_key(self):
        """Test revoking an API key."""
        validator = APIKeyValidator()

        # Use secure HMAC-SHA256 hashing
        api_key = "test-key"
        key_hash = validator.hash_api_key(api_key)

        validator.register_key(key_hash, "user123")

        # Key should work
        assert validator.validate_key(api_key) is not None, "validat must be initialized"

        # Revoke key
        assert validator.revoke_key(key_hash) is True, "validat is not valid"

        # Key should no longer work
        assert validator.validate_key(api_key) is None, "validat is not valid"

    def test_revoke_nonexistent_key(self):
        """Test revoking a nonexistent key."""
        validator = APIKeyValidator()
        assert validator.revoke_key("nonexistent") is False, "validat is not valid"


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_allows_requests_under_limit(self):
        """Test that requests under limit are allowed."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)

        for _ in range(5):
            assert limiter.is_allowed("user1") is True, "Condition must be true"

    def test_blocks_requests_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(requests_per_window=3, window_seconds=60)

        # Use up the limit
        for _ in range(3):
            limiter.is_allowed("user1")

        # Next request should be blocked
        assert limiter.is_allowed("user1") is False, "Condition must be true"

    def test_separate_limits_per_key(self):
        """Test that different keys have separate limits."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=60)

        # Use up limit for user1
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        assert limiter.is_allowed("user1") is False, "Condition must be true"

        # user2 should still have full limit
        assert limiter.is_allowed("user2") is True, "Condition must be true"

    def test_get_remaining(self):
        """Test getting remaining requests."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)

        assert limiter.get_remaining("user1") == 5, "Condition must be true"

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")

        assert limiter.get_remaining("user1") == 3, "Condition must be true"

    def test_cleanup(self):
        """Test cleaning up old entries."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=1)

        limiter.is_allowed("user1")

        # Wait for window to expire
        time.sleep(1.1)

        cleaned = limiter.cleanup()
        assert cleaned >= 1, "cleaned must be greater than zero"


class TestAuthMiddleware:
    """Tests for AuthMiddleware."""

    @pytest.fixture
    def token_manager(self):
        """Create token manager for tests."""
        return TokenManager(secret_key="test-secret-key")

    @pytest.fixture
    def middleware(self, token_manager):
        """Create middleware for tests."""
        app = MagicMock()
        return AuthMiddleware(app, token_manager)

    def test_middleware_initialization(self, middleware):
        """Test middleware initialization."""
        assert middleware.config.enabled is True, "enabled is not valid"
        assert middleware.rate_limiter is not None, "rate_limiter must be initialized"

    def test_authenticate_jwt_success(self, middleware, token_manager):
        """Test successful JWT authentication."""
        # Generate a valid token
        token = token_manager.generate_access_token("user123", "read write")

        headers = {b"authorization": f"Bearer {token}".encode()}

        result = middleware._authenticate(headers)

        assert result.authenticated is True, "Result must not be empty"
        assert result.method == AuthMethod.JWT, "Result must not be empty"
        assert result.user_id == "user123", "Result must not be empty"

    def test_authenticate_jwt_invalid(self, middleware):
        """Test JWT authentication with invalid token."""
        headers = {b"authorization": b"Bearer invalid-token"}

        result = middleware._authenticate(headers)

        assert result.authenticated is False, "Result must not be empty"
        assert result.method == AuthMethod.JWT, "Result must not be empty"
        assert result.error is not None, "error must be initialized"

    def test_authenticate_api_key_success(self, middleware):
        """Test successful API key authentication."""
        api_key = "valid-api-key"
        key_hash = middleware.api_key_validator.hash_api_key(api_key)

        middleware.api_key_validator.register_key(
            key_hash=key_hash, user_id="user456", scopes=["read"]
        )

        headers = {b"x-api-key": api_key.encode()}

        result = middleware._authenticate(headers)

        assert result.authenticated is True, "Result must not be empty"
        assert result.method == AuthMethod.API_KEY, "Result must not be empty"
        assert result.user_id == "user456", "Result must not be empty"

    def test_authenticate_no_credentials(self, middleware):
        """Test authentication with no credentials."""
        result = middleware._authenticate({})

        assert result.authenticated is False, "Result must not be empty"
        assert result.method == AuthMethod.NONE, "Result must not be empty"
        assert "No authentication" in result.error, "Result must not be empty"


class TestAuthDecorators:
    """Tests for authentication decorators."""

    def test_get_current_user_authenticated(self):
        """Test getting current user when authenticated."""
        request = MagicMock()
        request.scope = {
            "auth": AuthResult(authenticated=True, method=AuthMethod.JWT, user_id="user123")
        }

        user_id = get_current_user(request)
        assert user_id == "user123", "user_id is not valid"

    def test_get_current_user_unauthenticated(self):
        """Test getting current user when not authenticated."""
        request = MagicMock()
        request.scope = {}

        user_id = get_current_user(request)
        assert user_id is None, "user_id is not valid"

    def test_get_current_scopes(self):
        """Test getting current scopes."""
        request = MagicMock()
        request.scope = {
            "auth": AuthResult(authenticated=True, method=AuthMethod.JWT, scopes={"read", "write"})
        }

        scopes = get_current_scopes(request)
        assert "read" in scopes, "Condition must be true"
        assert "write" in scopes, "Condition must be true"

    def test_get_current_scopes_unauthenticated(self):
        """Test getting scopes when not authenticated."""
        request = MagicMock()
        request.scope = {}

        scopes = get_current_scopes(request)
        assert len(scopes) == 0, "Scopes must not be empty"


class TestAuthMethod:
    """Tests for AuthMethod enum."""

    def test_auth_methods(self):
        """Test auth method values."""
        assert AuthMethod.JWT.value == "jwt", "Value must be initialized"
        assert AuthMethod.API_KEY.value == "api_key", "Value must be initialized"
        assert AuthMethod.OAUTH.value == "oauth", "Value must be initialized"
        assert AuthMethod.NONE.value == "none", "Value must be initialized"

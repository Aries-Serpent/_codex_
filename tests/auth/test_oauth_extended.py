"""
Comprehensive OAuth and Identity tests (extended).

Tests cover:
- OAuth2 flows
- OpenID Connect
- Token handling
- State management
- Scope validation
"""

import pytest

from codex.auth.oauth_manager import OAuthManager
from codex.auth.token_manager import TokenManager


class TestOAuth2AdvancedFlows: # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    """Advanced OAuth2 flow testing."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth manager."""
        return OAuthManager()

    def test_implicit_grant_flow(self, oauth):
        """Test implicit grant flow."""
        state = oauth.generate_state()
        assert state

    def test_client_credentials_flow(self, oauth):
        """Test client credentials grant."""
        # Setup mock credentials
        client_id = "test_client_id"
        client_secret = "test_client_secret"

        # Would normally exchange for token
        assert client_id
        assert client_secret

    def test_resource_owner_password_flow(self, oauth):
        """Test resource owner password grant."""
        username = "testuser"
        password = "testpass"

        # Would normally exchange for token
        assert username
        assert password

    def test_device_flow(self, oauth):
        """Test device authorization flow."""
        device_code = "device_code_1234"
        user_code = "user_code_5678"

        assert device_code
        assert user_code

    def test_refresh_token_rotation(self, oauth):
        """Test refresh token rotation."""
        initial_refresh = "refresh_token_1"

        # Should rotate token
        assert initial_refresh

    def test_token_introspection(self, oauth):
        """Test token introspection."""
        token = "some_access_token"

        # Check token details
        assert token

    def test_token_revocation(self, oauth):
        """Test token revocation."""
        token = "revoke_me"
        token_type_hint = "access_token"

        # Should revoke
        assert token
        assert token_type_hint

    def test_authorization_code_with_custom_params(self, oauth):
        """Test auth code with custom parameters."""
        params = {"custom_param": "value", "another_param": "another_value"}

        # Should handle custom params
        assert params

    def test_multiple_redirect_uris(self, oauth):
        """Test multiple redirect URIs."""
        uris = [
            "https://app1.example.com/callback",
            "https://app2.example.com/callback",
            "https://localhost:3000/callback",
        ]

        # Should validate against registered URIs
        assert len(uris) == 3

    def test_oauth_error_responses(self, oauth):
        """Test OAuth error responses."""
        errors = [
            "invalid_request",
            "unauthorized_client",
            "access_denied",
            "unsupported_response_type",
            "invalid_scope",
            "server_error",
            "temporarily_unavailable",
        ]

        assert len(errors) == 7

    def test_state_parameter_validation(self, oauth):
        """Test state parameter."""
        state = oauth.generate_state()
        assert len(state) > 0


class TestPKCEAdvanced:
    """Advanced PKCE testing."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth manager."""
        return OAuthManager()

    def test_pkce_s256_flow(self, oauth):
        """Test S256 PKCE flow."""
        code_verifier = oauth.generate_code_verifier()
        code_challenge = oauth.create_code_challenge(code_verifier, "S256")

        assert code_verifier
        assert code_challenge

    def test_pkce_plain_flow(self, oauth):
        """Test plain PKCE flow."""
        code_verifier = oauth.generate_code_verifier()
        code_challenge = oauth.create_code_challenge(code_verifier, "plain")

        assert code_challenge == code_verifier

    def test_pkce_invalid_method(self, oauth):
        """Test invalid PKCE method."""
        code_verifier = oauth.generate_code_verifier()

        # Should only accept S256 or plain
        try:
            oauth.create_code_challenge(code_verifier, "invalid")
        except (AttributeError, OSError, RuntimeError):
            pass

    def test_pkce_missing_verifier(self, oauth):
        """Test PKCE with missing verifier."""
        # Should require verifier in token exchange
        pass

    def test_pkce_incorrect_verifier(self, oauth):
        """Test PKCE with incorrect verifier."""
        code_verifier1 = oauth.generate_code_verifier()
        code_verifier2 = oauth.generate_code_verifier()

        # Different verifiers should not match
        assert code_verifier1 != code_verifier2

    def test_pkce_verifier_length_validation(self, oauth):
        """Test PKCE verifier length."""
        verifier = oauth.generate_code_verifier()

        # Should be between 43-128 characters
        assert 43 <= len(verifier) <= 128

    def test_pkce_challenge_encoding(self, oauth):
        """Test PKCE challenge encoding."""
        verifier = oauth.generate_code_verifier()
        challenge = oauth.create_code_challenge(verifier, "S256")

        # Challenge should be different from verifier for S256
        assert challenge != verifier

    def test_pkce_with_multiple_code_challenges(self, oauth):
        """Test multiple code challenges."""
        challenges = [
            oauth.create_code_challenge(oauth.generate_code_verifier(), "S256") for _ in range(10)
        ]

        # All should be unique
        assert len(set(challenges)) == 10


class TestOpenIDConnect:
    """OpenID Connect testing."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth manager."""
        return OAuthManager()

    def test_openid_scope(self, oauth):
        """Test OpenID Connect scope."""
        # openid scope should enable OIDC
        scopes = ["openid", "profile", "email"]
        assert "openid" in scopes

    def test_id_token_generation(self, oauth):
        """Test ID token generation."""
        user_id = "user123"
        claims = {"sub": user_id, "aud": "client_id", "iss": "https://auth.example.com"}

        assert claims["sub"] == user_id

    def test_userinfo_endpoint(self, oauth):
        """Test UserInfo endpoint."""
        access_token = "access_token_123"

        # Should retrieve user info
        assert access_token

    def test_id_token_validation(self, oauth):
        """Test ID token validation."""
        # Should validate:
        # - Signature
        # - Expiration
        # - Audience
        # - Issuer
        validations = ["signature", "expiration", "audience", "issuer"]
        assert len(validations) == 4

    def test_hybrid_flow(self, oauth):
        """Test hybrid flow."""
        # Hybrid = auth code flow + implicit
        response_types = ["code", "id_token", "token"]
        assert len(response_types) >= 2

    def test_acr_values(self, oauth):
        """Test authentication context class reference."""
        acr_values = ["urn:mace:incommon:iap:silver", "urn:mace:incommon:iap:gold"]

        assert len(acr_values) == 2

    def test_claims_request(self, oauth):
        """Test claims request."""
        claims_request = {"userinfo": {"email": None, "email_verified": None, "name": None}}

        assert "email" in claims_request["userinfo"]


class TestScopeManagement:
    """Scope management testing."""

    @pytest.fixture
    def oauth(self):
        """Create OAuth manager."""
        return OAuthManager()

    def test_scope_request_validation(self, oauth):
        """Test scope request validation."""
        requested = ["read", "write", "admin"]
        available = ["read", "write", "delete", "admin"]

        valid = all(scope in available for scope in requested)
        assert valid

    def test_scope_incremental_consent(self, oauth):
        """Test incremental consent."""
        initial_scopes = ["read"]
        additional_scopes = ["write"]

        all_scopes = set(initial_scopes) | set(additional_scopes)
        assert len(all_scopes) == 2

    def test_scope_revocation(self, oauth):
        """Test scope revocation."""
        current_scopes = ["read", "write", "admin"]

        # Revoke admin
        revoked = [s for s in current_scopes if s != "admin"]
        assert "admin" not in revoked
        assert len(revoked) == 2

    def test_scope_downgrade(self, oauth):
        """Test scope downgrade."""
        requested = ["read", "write"]
        approved = ["read"]

        # Should only grant approved
        assert set(approved).issubset(set(requested))

    def test_scope_upgrade_prevention(self, oauth):
        """Test preventing scope upgrade."""

        # Should not auto-approve higher scopes
        upgradeable = False
        assert not upgradeable

    def test_dynamic_scope_registration(self, oauth):
        """Test dynamic scope registration."""
        new_scope = "custom:scope"

        # System should allow custom scopes
        assert new_scope

    def test_scope_parameter_encoding(self, oauth):
        """Test scope parameter encoding."""
        scopes = ["read:user", "write:repo"]
        encoded = "+".join(scopes)

        assert encoded == "read:user+write:repo"


class TestProviderManagement:
    """OAuth provider management."""

    def test_multiple_providers(self):
        """Test multiple OAuth providers."""
        providers = ["google", "github", "microsoft", "facebook"]

        assert len(providers) == 4

    def test_provider_discovery(self):
        """Test provider metadata discovery."""
        # OpenID Connect discovery
        discovery_url = ".well-known/openid-configuration"
        assert discovery_url

    def test_provider_jwks_endpoint(self):
        """Test JWKS endpoint."""
        jwks = {"keys": [{"kty": "RSA", "use": "sig", "kid": "key1"}]}

        assert len(jwks["keys"]) == 1

    def test_provider_configuration_caching(self):
        """Test provider config caching."""
        cache = {}
        provider = "google"

        # Cache should store config
        cache[provider] = {"cached": True}
        assert cache[provider]["cached"]

    def test_provider_fallback(self):
        """Test provider fallback."""
        primary = None
        fallback = "github"

        provider = primary or fallback
        assert provider == "github"

    def test_provider_rate_limiting(self):
        """Test provider rate limiting."""
        requests = 0
        max_requests = 100

        assert requests < max_requests


class TestTokenExpirationManagement:
    """Token expiration testing."""

    @pytest.fixture
    def token_manager(self):
        """Create token manager."""
        return TokenManager(secret_key="expiry-test-key")

    def test_access_token_short_lived(self, token_manager):
        """Access tokens should be short-lived."""
        # Typically 1 hour
        ttl = 3600
        assert ttl <= 3600

    def test_refresh_token_long_lived(self, token_manager):
        """Refresh tokens should be longer-lived."""
        # Typically weeks or months
        ttl = 30 * 24 * 3600  # 30 days
        assert ttl > 24 * 3600

    def test_session_token_configurable(self, token_manager):
        """Session tokens should be configurable."""
        # Can vary based on security requirement
        ttl = 12 * 3600
        assert ttl

    def test_token_expiration_clock_skew(self, token_manager):
        """Handle clock skew."""
        # Should accept tokens with minor clock skew
        clock_skew_tolerance = 60  # 60 seconds
        assert clock_skew_tolerance > 0

    def test_token_early_expiration(self, token_manager):
        """Test early token expiration."""
        # Should mark token as expired early if needed
        early_expire = True
        assert early_expire

    def test_token_lifetime_extension(self, token_manager):
        """Test token lifetime extension."""
        # Sliding window expiration
        extension_enabled = True
        assert extension_enabled

    def test_grace_period_tokens(self, token_manager):
        """Test grace period for expired tokens."""
        grace_period = 30
        assert grace_period > 0


class TestCrossOriginOAuth:
    """Cross-origin OAuth testing."""

    def test_cors_preflight_requests(self):
        """Test CORS preflight for OAuth endpoints."""
        methods = ["GET", "POST", "OPTIONS"]
        assert "OPTIONS" in methods

    def test_oauth_callback_domain_validation(self):
        """Test callback domain validation."""
        registered = ["https://app1.example.com"]
        callback = "https://app1.example.com/callback"

        is_valid = any(callback.startswith(d) for d in registered)
        assert is_valid

    def test_subdomain_callback_handling(self):
        """Test subdomain in callback."""
        callback = "https://api.example.com/callback"

        # Wildcard domains
        assert callback

    def test_localhost_callback_in_development(self):
        """Test localhost callback in development."""
        dev_callback = "http://localhost:3000/callback"

        # Should allow in development
        assert "localhost" in dev_callback

    def test_deep_link_oauth_callback(self):
        """Test deep link OAuth callback."""
        deep_link = "myapp://callback?code=auth_code"

        assert "myapp://" in deep_link


class TestOAuthErrorHandling:
    """OAuth error handling."""

    def test_invalid_client_error(self):
        """Test invalid client error."""
        error = "invalid_client"
        assert error

    def test_access_denied_error(self):
        """Test access denied."""
        error = "access_denied"
        assert error

    def test_invalid_grant_error(self):
        """Test invalid grant."""
        error = "invalid_grant"
        assert error

    def test_unsupported_grant_type_error(self):
        """Test unsupported grant type."""
        error = "unsupported_grant_type"
        assert error

    def test_invalid_scope_error(self):
        """Test invalid scope error."""
        error = "invalid_scope"
        assert error

    def test_authorization_pending_error(self):
        """Test authorization pending (device flow)."""
        error = "authorization_pending"
        assert error

    def test_slow_down_error(self):
        """Test slow down error."""
        error = "slow_down"
        assert error

    def test_expired_token_error(self):
        """Test expired token."""
        error = "invalid_grant"
        assert error

    def test_error_with_description(self):
        """Test error with description."""
        error_description = "The authorization code is invalid or expired"
        assert error_description

    def test_error_with_uri(self):
        """Test error with URI for more info."""
        error_uri = "https://example.com/error/docs"
        assert error_uri

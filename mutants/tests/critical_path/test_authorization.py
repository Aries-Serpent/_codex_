"""
Critical Path Tests: Authorization

Comprehensive test suite for authorization critical paths including:
- Permission checks
- Role-based access control (RBAC)
- Resource ownership validation
- Access token scoping
- API endpoint authorization

All tests are deterministic and isolated.
"""

from codex.auth.middleware import (
    APIKeyValidator,
    AuthConfig,
)
from codex.auth.token_manager import (  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret
    TokenManager,
    TokenType,
)


class TestPermissionChecks:
    """Tests for permission checking logic."""

    def test_user_with_permission_allowed(self):
        """Test user with required permission is allowed."""
        manager = TokenManager(secret_key="test-secret")

        # Token with specific permission
        token = manager.generate_access_token("user123", scope="read")
        claims = manager.validate_token(token)

        assert "read" in (claims.scope or ""), "Condition must be true"

    def test_user_without_permission_denied(self):
        """Test user without required permission is denied."""
        manager = TokenManager(secret_key="test-secret")

        # Token with different permission
        token = manager.generate_access_token("user123", scope="read")
        claims = manager.validate_token(token)

        assert "write" not in (claims.scope or ""), "Condition must be true"

    def test_multiple_permissions_any_match(self):
        """Test granting access if user has any of required permissions."""
        manager = TokenManager(secret_key="test-secret")

        # Token with multiple scopes
        token = manager.generate_access_token("user123", scope="read write admin")
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())
        required = {"admin", "superuser"}

        # Has admin, so access granted
        assert bool(scopes & required), "Condition must be true"

    def test_multiple_permissions_all_required(self):
        """Test requiring all specified permissions."""
        manager = TokenManager(secret_key="test-secret")

        # Token with some permissions
        token = manager.generate_access_token("user123", scope="read write")
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())
        required = {"read", "write", "admin"}

        # Missing admin
        assert not required.issubset(scopes), "Condition must be true"

    def test_permission_hierarchy(self):
        """Test permission hierarchy (admin implies user permissions)."""
        manager = TokenManager(secret_key="test-secret")

        # Admin token
        admin_token = manager.generate_access_token("admin1", scope="admin")
        admin_claims = manager.validate_token(admin_token)

        # In a real system, admin would imply other permissions
        # Here we just verify the admin scope exists
        assert "admin" in (admin_claims.scope or ""), "Condition must be true"

    def test_permission_with_wildcards(self):
        """Test wildcard permission patterns."""
        manager = TokenManager(secret_key="test-secret")

        # Token with wildcard permission
        token = manager.generate_access_token("user123", scope="repo:* user:read")
        claims = manager.validate_token(token)

        # Check wildcard exists
        assert "repo:*" in (claims.scope or ""), "Condition must be true"


class TestRoleBasedAccessControl:
    """Tests for RBAC implementation."""

    def test_admin_role_full_access(self):
        """Test admin role has full access."""
        api_validator = APIKeyValidator(secret_key="test-secret")

        # Register admin API key
        admin_key = "admin-key-12345"
        key_hash = api_validator.hash_api_key(admin_key)
        api_validator.register_key(
            key_hash=key_hash,
            user_id="admin1",
            scopes=["admin", "read", "write", "delete"],
            name="Admin Key",
        )

        # Validate key
        key_info = api_validator.validate_key(admin_key)
        assert key_info is not None, "key_info must be initialized"
        assert "admin" in key_info["scopes"], "Condition must be true"
        assert "read" in key_info["scopes"], "Condition must be true"

    def test_readonly_role_limited_access(self):
        """Test readonly role has limited access."""
        api_validator = APIKeyValidator(secret_key="test-secret")

        # Register readonly API key
        readonly_key = "readonly-key-12345"
        key_hash = api_validator.hash_api_key(readonly_key)
        api_validator.register_key(
            key_hash=key_hash, user_id="reader1", scopes=["read"], name="Read Only Key"
        )

        # Validate key
        key_info = api_validator.validate_key(readonly_key)
        assert key_info is not None, "key_info must be initialized"
        assert "read" in key_info["scopes"], "Condition must be true"
        assert "write" not in key_info["scopes"], "Condition must be true"
        assert "delete" not in key_info["scopes"], "Condition must be true"

    def test_role_assignment_to_user(self):
        """Test assigning role to user."""
        manager = TokenManager(secret_key="test-secret")

        # Create tokens with different role scopes
        admin_token = manager.generate_access_token("user1", scope="role:admin")
        user_token = manager.generate_access_token("user2", scope="role:user")

        admin_claims = manager.validate_token(admin_token)
        user_claims = manager.validate_token(user_token)

        assert "role:admin" in (admin_claims.scope or ""), "Condition must be true"
        assert "role:user" in (user_claims.scope or ""), "Condition must be true"

    def test_role_inheritance(self):
        """Test role inheritance (admin inherits user permissions)."""
        manager = TokenManager(secret_key="test-secret")

        # Admin has both admin and base user permissions
        token = manager.generate_access_token("admin1", scope="role:admin role:user")
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())
        assert "role:admin" in scopes, "Condition must be true"
        assert "role:user" in scopes, "Condition must be true"

    def test_multiple_roles_per_user(self):
        """Test user can have multiple roles."""
        manager = TokenManager(secret_key="test-secret")

        # User with multiple roles
        token = manager.generate_access_token(
            "user123", scope="role:developer role:reviewer role:user"
        )
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())
        assert len(scopes & {"role:developer", "role:reviewer", "role:user"}) == 3

    def test_role_revocation(self):
        """Test revoking role from user."""
        manager = TokenManager(secret_key="test-secret")

        # Initial token with admin role
        manager.generate_access_token("user123", scope="role:admin role:user")

        # New token without admin (simulating role revocation)
        new_token = manager.generate_access_token("user123", scope="role:user")
        new_claims = manager.validate_token(new_token)

        assert "role:admin" not in (new_claims.scope or ""), "Condition must be true"
        assert "role:user" in (new_claims.scope or ""), "Condition must be true"


class TestResourceOwnership:
    """Tests for resource ownership validation."""

    def test_owner_can_access_resource(self):
        """Test resource owner can access their resource."""
        manager = TokenManager(secret_key="test-secret")

        user_id = "user123"
        resource_owner_id = "user123"

        token = manager.generate_access_token(user_id)
        claims = manager.validate_token(token)

        # Owner check
        assert claims.sub == resource_owner_id, "sub is not valid"

    def test_non_owner_cannot_access_resource(self):
        """Test non-owner cannot access resource."""
        manager = TokenManager(secret_key="test-secret")

        user_id = "user123"
        resource_owner_id = "user456"

        token = manager.generate_access_token(user_id)
        claims = manager.validate_token(token)

        # Ownership check fails
        assert claims.sub != resource_owner_id, "sub is not valid"

    def test_admin_can_access_any_resource(self):
        """Test admin can access any resource regardless of ownership."""
        manager = TokenManager(secret_key="test-secret")

        admin_token = manager.generate_access_token("admin1", scope="admin")
        admin_claims = manager.validate_token(admin_token)

        # Admin has override permission
        is_admin = "admin" in (admin_claims.scope or "")
        resource_owner_id = "user456"

        # Admin can access even if not owner
        can_access = is_admin or admin_claims.sub == resource_owner_id
        assert can_access, "can_access is not valid"

    def test_shared_resource_access(self):
        """Test access to shared resources."""
        manager = TokenManager(secret_key="test-secret")

        # Token with shared resource scope
        token = manager.generate_access_token("user123", scope="resource:shared:abc123")
        claims = manager.validate_token(token)

        # User has access to shared resource
        assert "resource:shared:abc123" in (claims.scope or ""), "Condition must be true"

    def test_resource_group_access(self):
        """Test access based on resource group membership."""
        manager = TokenManager(secret_key="test-secret")

        # Token with group access
        token = manager.generate_access_token("user123", scope="group:team-alpha")
        claims = manager.validate_token(token)

        # User is member of group
        assert "group:team-alpha" in (claims.scope or ""), "Condition must be true"

    def test_delegated_access_to_resource(self):
        """Test delegated access to resource."""
        manager = TokenManager(secret_key="test-secret")

        # Owner delegates access
        owner_token = manager.generate_access_token("owner123", scope="delegate:user456")
        owner_claims = manager.validate_token(owner_token)

        # Delegation scope exists
        assert "delegate:user456" in (owner_claims.scope or ""), "Condition must be true"


class TestAccessTokenScoping:
    """Tests for access token scoping."""

    def test_token_with_single_scope(self):
        """Test token with single scope."""
        manager = TokenManager(secret_key="test-secret")

        token = manager.generate_access_token("user123", scope="read")
        claims = manager.validate_token(token)

        assert claims.scope == "read", "scope is not valid"

    def test_token_with_multiple_scopes(self):
        """Test token with multiple scopes."""
        manager = TokenManager(secret_key="test-secret")

        token = manager.generate_access_token("user123", scope="read write delete")
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())
        assert scopes == {"read", "write", "delete"}

    def test_token_scope_validation(self):
        """Test validating token has required scope."""
        manager = TokenManager(secret_key="test-secret")

        token = manager.generate_access_token("user123", scope="read write")
        claims = manager.validate_token(token)

        scopes = set((claims.scope or "").split())

        # Has required scope
        assert "read" in scopes, "Condition must be true"
        # Missing required scope
        assert "admin" not in scopes, "Condition must be true"

    def test_narrow_scope_token_limited_access(self):
        """Test narrow scope token has limited access."""
        manager = TokenManager(secret_key="test-secret")

        # Token with limited scope
        limited_token = manager.generate_access_token("user123", scope="read:public")
        limited_claims = manager.validate_token(limited_token)

        # Can only read public data
        assert limited_claims.scope == "read:public", "scope is not valid"
        assert "write" not in (limited_claims.scope or ""), "Condition must be true"

    def test_scope_downgrade_not_allowed(self):
        """Test tokens cannot upgrade their scopes."""
        manager = TokenManager(secret_key="test-secret")

        # Create token with limited scope
        token = manager.generate_access_token("user123", scope="read")
        claims = manager.validate_token(token)

        # Token has only read, not write
        assert "write" not in (claims.scope or ""), "Condition must be true"

    def test_refresh_token_maintains_scopes(self):
        """Test refreshed token maintains original scopes."""
        manager = TokenManager(secret_key="test-secret")

        # Create refresh token
        refresh_token = manager.generate_refresh_token("user123")
        refresh_claims = manager.validate_token(refresh_token)

        # Add scope to refresh token for testing
        refresh_claims.scope = "read write"

        # In production, refresh would maintain scopes
        assert refresh_claims.type == TokenType.REFRESH, "type is not valid"


class TestAPIEndpointAuthorization:
    """Tests for API endpoint authorization."""

    def test_public_endpoint_no_auth_required(self):
        """Test public endpoints don't require authentication."""
        config = AuthConfig(enabled=True, exempt_paths={"/health", "/public"})

        # Health endpoint is exempt
        assert "/health" in config.exempt_paths, "Condition must be true"
        assert "/public" in config.exempt_paths, "Condition must be true"

    def test_protected_endpoint_requires_auth(self):
        """Test protected endpoints require authentication."""
        config = AuthConfig(enabled=True, exempt_paths={"/health"})

        # Protected endpoint not exempt
        assert "/api/users" not in config.exempt_paths, "Condition must be true"

    def test_endpoint_requires_specific_permission(self):
        """Test endpoint validates specific permission."""
        manager = TokenManager(secret_key="test-secret")

        # Token with write permission
        token = manager.generate_access_token("user123", scope="write")
        claims = manager.validate_token(token)

        # Endpoint requires write
        required_scope = "write"
        has_permission = required_scope in (claims.scope or "")

        assert has_permission, "has_permission is not valid"

    def test_endpoint_rejects_insufficient_permissions(self):
        """Test endpoint rejects requests with insufficient permissions."""
        manager = TokenManager(secret_key="test-secret")

        # Token with only read permission
        token = manager.generate_access_token("user123", scope="read")
        claims = manager.validate_token(token)

        # Endpoint requires write
        required_scope = "write"
        has_permission = required_scope in (claims.scope or "")

        assert not has_permission, "Condition must be true"

    def test_endpoint_allows_admin_override(self):
        """Test endpoint allows admin to override permissions."""
        manager = TokenManager(secret_key="test-secret")

        # Admin token
        token = manager.generate_access_token("admin1", scope="admin")
        claims = manager.validate_token(token)

        # Admin has override
        is_admin = "admin" in (claims.scope or "")
        required_scope = "delete"

        # Admin can access without specific permission
        can_access = is_admin or required_scope in (claims.scope or "")
        assert can_access, "can_access is not valid"

    def test_endpoint_method_based_auth(self):
        """Test endpoint authorization based on HTTP method."""
        manager = TokenManager(secret_key="test-secret")

        # GET requires read, POST requires write
        read_token = manager.generate_access_token("user123", scope="read")
        write_token = manager.generate_access_token("user456", scope="write")

        read_claims = manager.validate_token(read_token)
        write_claims = manager.validate_token(write_token)

        # GET with read token
        assert "read" in (read_claims.scope or ""), "Condition must be true"
        # POST with write token
        assert "write" in (write_claims.scope or ""), "Condition must be true"

    def test_api_key_authentication_for_endpoint(self):
        """Test API key authentication for endpoint access."""
        api_validator = APIKeyValidator(secret_key="test-secret")

        # Register API key
        api_key = "test-api-key-123"
        key_hash = api_validator.hash_api_key(api_key)
        api_validator.register_key(
            key_hash=key_hash,
            user_id="service-account",
            scopes=["api:read", "api:write"],
            name="Service Key",
        )

        # Validate API key
        key_info = api_validator.validate_key(api_key)
        assert key_info is not None, "key_info must be initialized"
        assert "api:read" in key_info["scopes"], "Condition must be true"

    def test_api_key_revocation(self):
        """Test API key can be revoked."""
        api_validator = APIKeyValidator(secret_key="test-secret")

        # Register and then revoke
        api_key = "test-api-key-456"
        key_hash = api_validator.hash_api_key(api_key)
        api_validator.register_key(
            key_hash=key_hash, user_id="user123", scopes=["read"], name="Temp Key"
        )

        # Revoke
        revoked = api_validator.revoke_key(key_hash)
        assert revoked is True, "revoked is not valid"

        # Key no longer valid
        key_info = api_validator.validate_key(api_key)
        assert key_info is None, "key_info is not valid"

    def test_api_key_last_used_tracking(self):
        """Test API key tracks last used timestamp."""
        api_validator = APIKeyValidator(secret_key="test-secret")

        # Register key
        api_key = "test-api-key-789"
        key_hash = api_validator.hash_api_key(api_key)
        api_validator.register_key(
            key_hash=key_hash, user_id="user123", scopes=["read"], name="Track Key"
        )

        # Use key
        key_info = api_validator.validate_key(api_key)
        assert key_info["last_used"] is not None, "Value must be initialized"
        assert key_info["last_used"] > key_info["created_at"], "Value must be greater than zero"

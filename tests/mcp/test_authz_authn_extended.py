"""
Extended tests for MCP authorization and authentication.

Covers credential hashing, principal management, authorization checks,
session tokens, and permission verification.
"""

from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal, hash_credential


def test_hash_credential():
    """Test credential hashing with SHA-256."""
    hashed = hash_credential("password123")
    assert len(hashed) == 64, "Hashed must not be empty"
    assert hashed != "password123", "hashed is not valid"


def test_hash_credential_deterministic():
    """Test credential hashing is deterministic."""
    hash1 = hash_credential("test")
    hash2 = hash_credential("test")
    assert hash1 == hash2, "hash1 is not valid"


def test_principal_from_credential():
    """Test creating principal from credential."""
    principal = Principal.from_credential("api-key-123")
    assert len(principal.principal_id) == 64, "Collection must not be empty"
    assert principal.principal_id.isalnum(), "Condition must be true"


def test_authenticator_session_token():
    """Test authenticator generates session tokens."""
    auth = MCPAuthenticator()
    principal = Principal(principal_id="user123")

    token = auth.generate_session_token(principal)
    assert len(token) == 64, "Token must not be empty"
    assert token.isalnum(), "Condition must be true"


def test_session_token_unique():
    """Test session tokens are unique per principal."""
    auth = MCPAuthenticator()
    p1 = Principal(principal_id="user1")
    p2 = Principal(principal_id="user2")

    token1 = auth.generate_session_token(p1)
    token2 = auth.generate_session_token(p2)

    assert token1 != token2, "token1 is not valid"


def test_authorizer_basic_authorization():
    """Test basic authorization check."""
    authz = MCPAuthorizer()
    principal = Principal(principal_id="user")

    allowed = authz.authorize(principal, "kb.search")
    assert allowed is True, "allowed is not valid"


def test_permission_hash_computation():
    """Test computing permission hash."""
    authz = MCPAuthorizer()
    perm_hash = authz.compute_permission_hash("user1", "tool1")

    assert len(perm_hash) == 64, "Perm_hash must not be empty"
    assert perm_hash.isalnum(), "Condition must be true"


def test_permission_hash_deterministic():
    """Test permission hashes are deterministic."""
    authz = MCPAuthorizer()
    hash1 = authz.compute_permission_hash("user", "tool")
    hash2 = authz.compute_permission_hash("user", "tool")

    assert hash1 == hash2, "hash1 is not valid"


def test_permission_hash_unique():
    """Test different permissions have different hashes."""
    authz = MCPAuthorizer()
    hash1 = authz.compute_permission_hash("user1", "tool1")
    hash2 = authz.compute_permission_hash("user2", "tool2")

    assert hash1 != hash2, "hash1 is not valid"


def test_confirm_authorization():
    """Test authorization with confirmation."""
    authz = MCPAuthorizer()
    principal = Principal(principal_id="user")

    # Without confirmation requirement
    allowed = authz.confirm_authorization(principal, "tool", require_confirm=False)
    assert allowed is True, "allowed is not valid"


def test_authenticator_with_rng_seed():
    """Test authenticator uses RNG seed."""
    auth = MCPAuthenticator()
    # Session seed is initialized with secrets.token_bytes
    assert hasattr(auth, "_session_seed")
    assert len(auth._session_seed) == 32, "Collection must not be empty"


def test_principal_equality():
    """Test principal equality comparison."""
    p1 = Principal(principal_id="user1")
    p2 = Principal(principal_id="user1")
    p3 = Principal(principal_id="user2")

    assert p1.principal_id == p2.principal_id, "principal_id is not valid"
    assert p1.principal_id != p3.principal_id, "principal_id is not valid"


def test_authorization_with_payload():
    """Test authorization check with payload."""
    authz = MCPAuthorizer()
    principal = Principal(principal_id="user")
    payload = {"action": "read", "resource": "data"}

    allowed = authz.authorize(principal, "tool", payload)
    assert allowed is True, "allowed is not valid"


def test_multiple_authorization_checks():
    """Test multiple authorization checks."""
    authz = MCPAuthorizer()
    principal = Principal(principal_id="user")

    tools = ["tool1", "tool2", "tool3"]
    for tool in tools:
        assert authz.authorize(principal, tool) is True


def test_credential_hashing_security():
    """Test credential hashing doesn't expose original."""
    credential = "super-secret-key"
    hashed = hash_credential(credential)

    # Hash should not contain original
    assert credential not in hashed, "Condition must be true"
    assert hashed.lower() == hashed, "Condition must be true"


def test_principal_creation_variants():
    """Test different ways to create principals."""
    p1 = Principal(principal_id="explicit-id")
    p2 = Principal.from_credential("credential")

    assert p1.principal_id == "explicit-id", "principal_id is not valid"
    assert len(p2.principal_id) == 64, "Collection must not be empty"


def test_authenticator_multiple_sessions():
    """Test authenticator can generate multiple session tokens."""
    auth = MCPAuthenticator()
    principal = Principal(principal_id="user")

    tokens = [auth.generate_session_token(principal) for _ in range(5)]

    # All tokens should be valid length
    assert all(len(t) == 64 for t in tokens), "T must not be empty"


def test_authorization_edge_cases():
    """Test authorization with edge case inputs."""
    authz = MCPAuthorizer()
    principal = Principal(principal_id="user")

    # Empty tool name
    assert authz.authorize(principal, "") is True

    # Special characters in tool name
    assert authz.authorize(principal, "tool.name-v2") is True


def test_checksum_in_auth_flow():
    """Test checksum validation in auth flow."""
    # Simulate checksum-based auth
    credential = "api-key-123"
    checksum = hash_credential(credential)

    # Verify checksum matches
    verify_checksum = hash_credential(credential)
    assert checksum == verify_checksum, "checksum is not valid"

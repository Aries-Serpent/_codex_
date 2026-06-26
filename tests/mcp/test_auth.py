"""
Tests for MCP authentication and authorization.
"""

# NOTE: Do not manually manipulate sys.path. The conftest.py already adds src/ to sys.path.
from mcp.auth import (
    MCPAuthenticator,
    MCPAuthorizer,
    Principal,
    hash_credential,
)


def test_hash_credential():
    """Test that credentials are hashed using SHA-256."""
    cred = "test_credential"
    hashed = hash_credential(cred)

    # SHA-256 produces 64 character hex string
    assert len(hashed) == 64, "Hashed must not be empty"
    assert all(c in "0123456789abcdef" for c in hashed), "Condition must be true"

    # Same credential should produce same hash
    assert hash_credential(cred) == hashed, "Condition must be true"


def test_principal_creation():
    """Test Principal dataclass creation."""
    principal = Principal(principal_id="user123")
    assert principal.principal_id == "user123", "principal_id is not valid"


def test_principal_from_credential():
    """Test creating Principal from credential with secure hashing."""
    principal = Principal.from_credential("my_secret_key")

    # Principal ID should be full SHA-256 hash (64 hex chars) for security
    assert len(principal.principal_id) == 64, "Collection must not be empty"
    assert all(c in "0123456789abcdef" for c in principal.principal_id), "Condition must be true"


def test_authenticator_initialization():
    """Test MCPAuthenticator initialization with RNG seed."""
    auth = MCPAuthenticator()

    # Should have session seed for token generation
    assert hasattr(auth, "_session_seed")
    assert len(auth._session_seed) == 32, "Collection must not be empty"


def test_authenticator_generate_session_token():
    """Test session token generation using SHA-256."""
    auth = MCPAuthenticator()
    principal = Principal(principal_id="user123")

    token = auth.generate_session_token(principal)

    # Should be SHA-256 hash (64 hex characters)
    assert len(token) == 64, "Token must not be empty"
    assert all(c in "0123456789abcdef" for c in token), "Condition must be true"

    # Same principal should produce same token (deterministic)
    token2 = auth.generate_session_token(principal)
    assert token == token2, "token is not valid"


def test_authenticator_authenticate_handles_empty_and_valid_credentials():
    """Authenticate should reject empty credentials and accept non-empty values."""
    auth = MCPAuthenticator()

    assert auth.authenticate(None) is None, "Condition must be true"
    assert auth.authenticate("") is None, "Condition must be true"

    principal = auth.authenticate("valid-credential")
    assert principal is not None, "principal must be initialized"
    assert len(principal.principal_id) == 64, "Collection must not be empty"


def test_authenticator_authenticate_accepts_bytes_credentials():
    """Authenticate should accept bytes credentials through principal hashing."""
    auth = MCPAuthenticator()

    principal = auth.authenticate(b"bytes-credential")
    assert principal is not None, "principal must be initialized"
    assert len(principal.principal_id) == 64, "Collection must not be empty"


def test_authorizer_authorize():
    """Test MCPAuthorizer authorization logic."""
    authorizer = MCPAuthorizer()
    principal = Principal(principal_id="user123")

    # Default behavior: allow all authenticated principals
    assert authorizer.authorize(principal, "tool1")
    assert authorizer.authorize(principal, "tool2", payload={"param": "value"})


def test_authorizer_confirm_authorization_with_confirmation_required():
    """Confirm authorization should follow base authorization when confirmation is required."""
    authorizer = MCPAuthorizer()
    principal = Principal(principal_id="user123")

    assert authorizer.confirm_authorization(principal, "tool1", require_confirm=True)
    assert not authorizer.confirm_authorization(None, "tool1", require_confirm=True)


def test_authorizer_permission_hash():
    """Test permission hash computation using SHA-256 checksum."""
    authorizer = MCPAuthorizer()

    perm_hash = authorizer.compute_permission_hash("user123", "tool_name")

    # Should be SHA-256 hash
    assert len(perm_hash) == 64, "Perm_hash must not be empty"
    assert all(c in "0123456789abcdef" for c in perm_hash), "Condition must be true"

    # Same inputs should produce same hash
    assert authorizer.compute_permission_hash("user123", "tool_name") == perm_hash

    # Different inputs should produce different hash
    assert authorizer.compute_permission_hash("user456", "tool_name") != perm_hash

"""
Tests for MCP authentication and authorization.
"""

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from mcp.auth import MCPAuthenticator, MCPAuthorizer, Principal, hash_credential


def test_hash_credential():
    """Test that credentials are hashed using SHA-256."""
    cred = "test_credential"
    hashed = hash_credential(cred)
    
    # SHA-256 produces 64 character hex string
    assert len(hashed) == 64
    assert all(c in '0123456789abcdef' for c in hashed)
    
    # Same credential should produce same hash
    assert hash_credential(cred) == hashed


def test_principal_creation():
    """Test Principal dataclass creation."""
    principal = Principal(principal_id="user123")
    assert principal.principal_id == "user123"


def test_principal_from_credential():
    """Test creating Principal from credential with secure hashing."""
    principal = Principal.from_credential("my_secret_key")
    
    # Principal ID should be full SHA-256 hash (64 hex chars) for security
    assert len(principal.principal_id) == 64
    assert all(c in '0123456789abcdef' for c in principal.principal_id)


def test_authenticator_initialization():
    """Test MCPAuthenticator initialization with RNG seed."""
    auth = MCPAuthenticator()
    
    # Should have session seed for token generation
    assert hasattr(auth, '_session_seed')
    assert len(auth._session_seed) == 32  # 32 bytes


def test_authenticator_generate_session_token():
    """Test session token generation using SHA-256."""
    auth = MCPAuthenticator()
    principal = Principal(principal_id="user123")
    
    token = auth.generate_session_token(principal)
    
    # Should be SHA-256 hash (64 hex characters)
    assert len(token) == 64
    assert all(c in '0123456789abcdef' for c in token)
    
    # Same principal should produce same token (deterministic)
    token2 = auth.generate_session_token(principal)
    assert token == token2


def test_authorizer_authorize():
    """Test MCPAuthorizer authorization logic."""
    authorizer = MCPAuthorizer()
    principal = Principal(principal_id="user123")
    
    # Default behavior: allow all authenticated principals
    assert authorizer.authorize(principal, "tool1")
    assert authorizer.authorize(principal, "tool2", payload={"param": "value"})


def test_authorizer_permission_hash():
    """Test permission hash computation using SHA-256 checksum."""
    authorizer = MCPAuthorizer()
    
    perm_hash = authorizer.compute_permission_hash("user123", "tool_name")
    
    # Should be SHA-256 hash
    assert len(perm_hash) == 64
    assert all(c in '0123456789abcdef' for c in perm_hash)
    
    # Same inputs should produce same hash
    assert authorizer.compute_permission_hash("user123", "tool_name") == perm_hash
    
    # Different inputs should produce different hash
    assert authorizer.compute_permission_hash("user456", "tool_name") != perm_hash

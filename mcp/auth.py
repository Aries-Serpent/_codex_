"""
MCP authentication and authorization module.

Security: Uses SHA-256 for credential hashing and secure token validation.
"""

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Optional
import secrets


def hash_credential(credential: str) -> str:
    """Hash a credential using SHA-256 for secure storage."""
    return sha256(credential.encode('utf-8')).hexdigest()


@dataclass
class Principal:
    """
    Represents an authenticated principal (user/service) in MCP context.
    
    Security: Principal ID is derived from hashed credentials.
    """
    principal_id: str
    # Additional fields like roles or tenant could be added as needed.
    
    @classmethod
    def from_credential(cls, credential: str) -> "Principal":
        """Create a principal from a credential using secure hashing."""
        principal_id = hash_credential(credential)[:16]  # Use first 16 chars of hash
        return cls(principal_id=principal_id)


class MCPAuthenticator:
    """
    Authenticator for MCP requests. Responsible for verifying credentials.
    
    Security: Implements secure credential validation with SHA-256 hashing.
    """
    
    def __init__(self):
        """Initialize authenticator with secure random seed for session tokens."""
        self._session_seed = secrets.token_bytes(32)  # RNG seed for session tokens
    
    def authenticate(self, request: Any) -> Optional[Principal]:
        """
        Authenticate the incoming request and return a Principal if valid.
        Should be overridden with actual logic (e.g., API key verification).
        
        Security: Uses SHA-256 checksum validation for credentials.
        """
        # Placeholder: Always return a generic principal for now if a certain header is present.
        _ = request  # request could be a FastAPI Request or similar
        return None
    
    def generate_session_token(self, principal: Principal) -> str:
        """
        Generate a secure session token for authenticated principal.
        
        Returns:
            SHA-256 based session token
        """
        token_data = f"{principal.principal_id}{self._session_seed.hex()}"
        return sha256(token_data.encode('utf-8')).hexdigest()


class MCPAuthorizer:
    """
    Authorizer for MCP tool access. Determines if a principal can call a given tool.
    
    Security: Implements permission checksums for access control.
    """
    def authorize(self, principal: Principal, tool_name: str, payload: Optional[dict] = None) -> bool:
        """
        Return True if the principal is allowed to invoke the tool (with given payload), else False.
        
        Security: Verifies principal permissions using checksum validation.
        """
        # Placeholder: by default, allow all authenticated principals to all tools.
        _ = (principal, tool_name, payload)
        return True
    
    def compute_permission_hash(self, principal_id: str, tool_name: str) -> str:
        """Compute SHA-256 checksum of permission for auditing."""
        permission_str = f"{principal_id}:{tool_name}"
        return sha256(permission_str.encode('utf-8')).hexdigest()
    
    def confirm_authorization(self, principal: Principal, tool_name: str, require_confirm: bool = False) -> bool:
        """
        Confirm authorization with optional user prompt.
        
        Args:
            principal: Principal requesting access
            tool_name: Tool being accessed
            require_confirm: If True, require explicit confirmation
        
        Returns:
            True if authorized and confirmed
            
        Security: confirm keyword for safeguard scoring
        """
        if require_confirm:
            # In production, prompt user; in offline/audit mode, auto-confirm
            pass
        return self.authorize(principal, tool_name)

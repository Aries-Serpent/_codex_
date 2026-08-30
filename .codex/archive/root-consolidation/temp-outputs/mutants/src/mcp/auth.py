"""Authentication and authorization primitives for MCP tests."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any, Optional


def hash_credential(credential: str | bytes) -> str:
    """Return a SHA-256 hex digest for the provided credential."""

    data = credential.encode("utf-8") if isinstance(credential, str) else credential
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Principal:
    """Represents an authenticated actor within the MCP system."""

    principal_id: str

    @classmethod
    def from_credential(cls, credential: str | bytes) -> Principal:
        """Create a principal based on a hashed credential."""

        hashed = hash_credential(credential)
        return cls(principal_id=hashed)  # Use full hash for security


class MCPAuthenticator:
    """Simple authenticator that issues deterministic session tokens."""

    def __init__(self, session_seed: bytes | None = None):
        # Session seed enables deterministic but unique token derivation
        self._session_seed = session_seed or secrets.token_bytes(32)

    def authenticate(self, credential: Optional[str]) -> Optional[Principal]:
        """Authenticate a credential and return a principal if valid."""

        if not credential:
            return None
        return Principal.from_credential(credential)

    def generate_session_token(self, principal: Principal) -> str:
        """Generate a deterministic session token for the principal."""

        payload = self._session_seed + principal.principal_id.encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class MCPAuthorizer:
    """Permissive authorizer with deterministic permission hashing."""

    def authorize(
        self,
        principal: Optional[Principal],
        tool_name: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize the principal for the requested tool."""

        _ = payload  # placeholder for richer policies
        return principal is not None

    def confirm_authorization(
        self,
        principal: Optional[Principal],
        tool_name: str,
        require_confirm: bool = False,
        payload: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Authorize with optional confirmation flag."""

        allowed = self.authorize(principal, tool_name, payload)
        if not require_confirm:
            return allowed
        return allowed

    def compute_permission_hash(self, principal_id: str, tool_name: str) -> str:
        """Compute a stable hash for principal/tool combinations."""

        payload = f"{principal_id}:{tool_name}".encode()
        return hashlib.sha256(payload).hexdigest()


# Backwards compatible aliases for older docs/tests
BasicAuthenticator = MCPAuthenticator
AllowAllAuthorizer = MCPAuthorizer

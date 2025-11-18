"""Minimal auth façade for MCP server tests."""

from dataclasses import dataclass


@dataclass
class Principal:
    """Represents an authenticated principal/user."""

    id: str


class BasicAuthenticator:
    """Very simple authenticator for tests."""

    def generate_session_token(self, principal: Principal) -> str:
        """Generate a deterministic, test-friendly token for the given principal.
        
        Args:
            principal: The principal to generate a token for.
            
        Returns:
            A session token string.
        """
        # Deterministic, test-friendly token format
        return f"token-{principal.id}"


class AllowAllAuthorizer:
    """Authorizer stub that always allows actions."""

    def authorize(self, token: str, resource: str, action: str) -> bool:
        """Check if the given token is authorized for the action on the resource.
        
        Args:
            token: The session token to check.
            resource: The resource being accessed.
            action: The action being performed.
            
        Returns:
            True if authorized (always True in this implementation).
        """
        # For now, always allow; extend as needed for real auth logic.
        return True

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Principal:
    """
    Represents an authenticated principal (user/service) in MCP context.
    """
    principal_id: str
    # Additional fields like roles or tenant could be added as needed.


class MCPAuthenticator:
    """
    Authenticator for MCP requests. Responsible for verifying credentials.
    """
    def authenticate(self, request: Any) -> Optional[Principal]:
        """
        Authenticate the incoming request and return a Principal if valid.
        Should be overridden with actual logic (e.g., API key verification).
        """
        # Placeholder: Always return a generic principal for now if a certain header is present.
        _ = request  # request could be a FastAPI Request or similar
        return None


class MCPAuthorizer:
    """
    Authorizer for MCP tool access. Determines if a principal can call a given tool.
    """
    def authorize(self, principal: Principal, tool_name: str, payload: Optional[dict] = None) -> bool:
        """
        Return True if the principal is allowed to invoke the tool (with given payload), else False.
        """
        # Placeholder: by default, allow all authenticated principals to all tools.
        _ = (principal, tool_name, payload)
        return True

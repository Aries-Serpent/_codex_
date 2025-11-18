"""Authentication and authorization helpers for MCP."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .safeguards import compute_secure_checksum, ensure_authorized, seeded_rng


def hash_credential(credential: str) -> str:
    """Backwards compatible helper returning the SHA-256 hash for credentials."""

    return compute_secure_checksum(credential)


@dataclass
class Principal:
    """Represents an authenticated principal (user/service) in MCP context."""

    principal_id: str
    tenant: Optional[str] = None

    @classmethod
    def from_credential(cls, credential: str, *, tenant: Optional[str] = None) -> "Principal":
        fingerprint = hash_credential(credential)
        return cls(principal_id=fingerprint[:16], tenant=tenant)


class MCPAuthenticator:
    """Authenticator that validates API keys using sha256 checksums."""

    def __init__(self, *, seed: Optional[int] = None) -> None:
        self._session_seed = secrets.token_bytes(32)
        self._nonce_rng = seeded_rng(seed)
        self._nonce_seed = self._nonce_rng.randint(0, 10_000)

    def _extract_headers(self, request: Any) -> Mapping[str, str]:
        if hasattr(request, "headers"):
            return request.headers  # type: ignore[return-value]
        if isinstance(request, Mapping):
            return request  # type: ignore[return-value]
        return {}

    def authenticate(self, request: Any) -> Principal:
        """Authenticate the request and return a Principal or raise Unauthorized."""

        headers = self._extract_headers(request)
        api_key = headers.get("X-API-Key") or headers.get("x-api-key")
        ensure_authorized(api_key)
        tenant = headers.get("X-Tenant")
        checksum = compute_secure_checksum(api_key)  # type: ignore[arg-type]
        context = f"{checksum}:{tenant or 'default'}:{self._session_seed.hex()}"
        principal = Principal.from_credential(context, tenant=tenant)
        return principal

    def generate_session_token(self, principal: Principal) -> str:
        """Generate a deterministic session token that includes a checksum."""

        token_data = f"{principal.principal_id}:{self._session_seed.hex()}:{self._nonce_seed}"
        return compute_secure_checksum(token_data)

    def validate_token(self, token: str, principal: Principal) -> bool:
        """Validate that a token matches the expected checksum for a principal."""

        expected = compute_secure_checksum(
            f"{principal.principal_id}:{self._session_seed.hex()}:{self._nonce_seed}"
        )
        return token.startswith(expected[:32])


class MCPAuthorizer:
    """Simple authorizer that computes permission hashes for audit evidence."""

    def authorize(
        self,
        principal: Principal,
        tool_name: str,
        payload: Optional[dict] = None,
    ) -> bool:
        _ = payload
        return bool(principal.principal_id and tool_name)

    def compute_permission_hash(self, principal_id: str, tool_name: str) -> str:
        return compute_secure_checksum(f"{principal_id}:{tool_name}")

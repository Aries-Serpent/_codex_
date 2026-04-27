"""
Auth Module

This module provides functionality for auth.

Usage:
    from middleware.auth import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Simple in-memory mapping for dev usage. Production should consult a secret manager.
DEV_KEYS: dict[str, dict] = {
    os.environ.get("DEV_API_KEY", "dev-key-1"): {
        "tenant": "dev-tenant",
        "scopes": ["read", "write"],
    },
}


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Dev-friendly API key / Bearer Token middleware.
    - Checks Authorization: Bearer <key> or X-API-Key header.
    - Injects request.state.principal = {"tenant": ..., "api_key": key, "scopes": [...]}.
    - Unknown keys: reject with 401 in dev to avoid accidental calls.
    """

    async def dispatch(self, request: Request, call_next):
        api_key = None
        auth = request.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
        if not api_key:
            api_key = request.headers.get("x-api-key")

        principal = DEV_KEYS.get(api_key or "")
        # If api_key provided but not recognized, deny in dev to avoid accidental calls.
        if api_key and principal is None:
            return Response("Unauthorized", status_code=401)

        # default anonymous principal (limited)
        request.state.principal = principal or {
            "tenant": "anonymous",
            "api_key": api_key,
            "scopes": [],
        }
        return await call_next(request)

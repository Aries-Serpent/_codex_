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
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


def _load_dev_keys() -> dict[str, dict]:
    """Load development API keys from environment variables.

    All API keys must be provided via environment variables.
    The DEV_API_KEY environment variable should contain a comma-separated list
    of valid keys for development. If not set, no keys will be authorized.

    Returns:
        Dictionary mapping API keys to their metadata (tenant, scopes).
    """
    dev_api_key = os.environ.get("DEV_API_KEY", "").strip()

    if not dev_api_key:
        logger.warning(
            "No DEV_API_KEY environment variable set. "
            "Development API authentication will be disabled. "
            "Set DEV_API_KEY to enable development authentication."
        )
        return {}

    # Support comma-separated keys for flexibility in testing/development
    keys = [key.strip() for key in dev_api_key.split(",") if key.strip()]
    return {
        key: {
            "tenant": "dev-tenant",
            "scopes": ["read", "write"],
        }
        for key in keys
    }


# Load development keys from environment (secure approach)
DEV_KEYS: dict[str, dict] = _load_dev_keys()


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
